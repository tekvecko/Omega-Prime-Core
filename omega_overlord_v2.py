import google.generativeai as genai
import subprocess
import time
import os
import re
import sys

# --- KONFIGURACE ---
API_KEY_FILE = "api_key.txt"
SHADOW_DIR = "SHADOW_REALM"
SERVER_FILE = "server.py"
LOG_FILE = "server.log"

# LIMITY ADAPTIVNÍ SMYČKY
MAX_CYCLES = 20       # Maximální tvrdý limit (pojistka)
REQUIRED_STABLE_STREAK = 3  # Kolikrát musí projít testem, aby mise skončila úspěchem
GIVE_UP_THRESHOLD = 6 # Kolikrát může selhat v řadě, než to vzdáme

# 1. NAČTENÍ KLÍČE
if not os.path.exists(API_KEY_FILE):
    print("CRITICAL: Chybí klíč.")
    exit(1)
with open(API_KEY_FILE, "r") as f:
    genai.configure(api_key=f.read().strip())

# 2. VSTUP DO IZOLACE
if not os.path.exists(SHADOW_DIR):
    os.makedirs(SHADOW_DIR)
os.chdir(SHADOW_DIR)

# 3. POMOCNÉ FUNKCE
def run_cmd(cmd, timeout=30):
    try:
        # Ochrana proti zabití sebe sama
        if "pkill python" in cmd and "-f" not in cmd:
            cmd = "pkill -f server.py"
        
        # Povolení nohup
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Příkaz trval moc dlouho."
    except Exception as e:
        return f"EXEC FAIL: {e}"

def check_server_health():
    # 1. Běží proces?
    try:
        proc = subprocess.check_output("pgrep -f server.py", shell=True)
    except:
        return False, "Proces neběží."

    # 2. Odpovídá port?
    try:
        subprocess.check_output("curl -s --max-time 2 http://localhost:5000", shell=True)
        return True, "ONLINE"
    except:
        return False, "Proces běží, ale PORT neodpovídá (zaseklý?)."

def stress_test():
    print("   🔥 SPUŠTĚNÍ STRESS TESTU...")
    try:
        # Posleme 10 requestů
        cmd = 'for i in {1..10}; do curl -s -X POST -H "Content-Type: application/json" -d \'{"message": "Stress"}\' http://localhost:5000/log > /dev/null; done'
        subprocess.run(cmd, shell=True, timeout=5)
        
        is_up, msg = check_server_health()
        if is_up:
            return True, "Stress test OK."
        else:
            return False, "Server spadl pod zátěží."
    except Exception as e:
        return False, f"Chyba testu: {e}"

def read_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            # Pokud je log prázdný nebo má jen pár řádek
            if not lines: return "Log je prázdný."
            return "".join(lines[-20:]) 
    return "Log file missing."

def is_flask_installed():
    try:
        subprocess.check_output("pip show flask", shell=True)
        return True
    except:
        return False

# 4. EXECUTOR
def execute_ai_plan(ai_text):
    code_blocks = re.findall(r'```(?:bash|sh)?\n(.*?)```', ai_text, re.DOTALL)
    commands = code_blocks if code_blocks else []
    
    if not commands and "EXEC:" in ai_text:
        commands = [line.split("EXEC:", 1)[1].strip() for line in ai_text.split('\n') if "EXEC:" in line]

    log = ""
    for cmd in commands:
        print(f"   ⚡ VYKONÁVÁM: {cmd[:60]}...")
        log += run_cmd(cmd) + "\n"
    return log if log.strip() else "Žádné příkazy."

# 5. HLAVNÍ ADAPTIVNÍ SMYČKA
def overlord_loop():
    print(f"--- OMEGA OVERLORD: DYNAMIC MODE ---")
    print(f"Cíl: Udržet server stabilní po {REQUIRED_STABLE_STREAK} cykly v řadě.")
    
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    best = next((m for m in models if "flash" in m or "pro" in m), models[0])
    model = genai.GenerativeModel(best)
    chat = model.start_chat(history=[])

    cycle = 0
    stable_streak = 0
    fail_streak = 0

    while cycle < MAX_CYCLES:
        cycle += 1
        print(f"\n🔄 [CYKLUS {cycle}] (Streak: {stable_streak}/{REQUIRED_STABLE_STREAK} | Fails: {fail_streak})")
        
        # A) DIAGNOSTIKA
        is_up, health_msg = check_server_health()
        server_logs = read_logs()
        flask_status = "NAINSTALOVÁN" if is_flask_installed() else "CHYBÍ"
        
        # B) LOGIKA STAVU
        if not is_up:
            fail_streak += 1
            stable_streak = 0
            situation = f"KRITICKÁ: Server NEJEDE ({health_msg})."
            objective = "OPRAVA. Zkontroluj syntaxi, porty, logy. NERESTARTUJ bez změny kódu."
        else:
            # Server běží -> Stress Test
            passed, stress_msg = stress_test()
            if passed:
                stable_streak += 1
                fail_streak = 0 # Reset failů
                situation = "STABILNÍ: Server běží a prošel testem."
                objective = "EVOLUCE nebo ÚDRŽBA. Pokud je kód stabilní, přidej komentář nebo malou funkci."
            else:
                fail_streak += 1
                stable_streak = 0
                situation = f"NESTABILNÍ: {stress_msg}"
                objective = "STABILIZACE. Server padá pod zátěží."

        # C) PODMÍNKY UKONČENÍ
        if stable_streak >= REQUIRED_STABLE_STREAK:
            print(f"\n🏆 MISSE SPLNĚNA! Server byl stabilní {stable_streak}x v řadě.")
            break
        
        if fail_streak >= GIVE_UP_THRESHOLD:
            print(f"\n💀 KRITICKÉ SELHÁNÍ: {fail_streak}x v řadě se nepovedlo server nahodit.")
            print("Doporučuji manuální zásah. Ukončuji smyčku.")
            break

        # D) KONZULTACE S AI
        prompt = (
            f"Jsi OMEGA OVERLORD. \n"
            f"STAV: {situation}\n"
            f"INFO: Flask je {flask_status}.\n"
            f"POSLEDNÍ LOGY Z 'server.log':\n{server_logs}\n"
            f"CÍL: {objective}\n\n"
            f"INSTRUKCE:\n"
            f"1. Pokud Flask už je nainstalovaný, NEINSTALUJ HO ZNOVU. Hledej SyntaxError v logu.\n"
            f"2. Pokud je chyba v kódu, přepiš 'server.py' (cat << EOF).\n"
            f"3. Pro restart: `pkill -f server.py; nohup python3 server.py > server.log 2>&1 &`.\n"
            f"4. Zabal příkazy do ```bash."
        )

        try:
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"   🤖 AI PLÁNUJE: {ai_text[:80]}...")
            
            exec_log = execute_ai_plan(ai_text)
            print(f"   📝 VÝSTUP: {exec_log[:150]}...")
            
            time.sleep(3)

        except Exception as e:
            print(f"❌ CHYBA CYKLU: {e}")
            break

    print(f"\n--- OMEGA DYNAMIC LOOP ENDED (Cycles: {cycle}) ---")

if __name__ == "__main__":
    overlord_loop()
