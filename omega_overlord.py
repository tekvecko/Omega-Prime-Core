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
ITERATIONS = 5

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
def run_cmd(cmd, timeout=10):
    try:
        # Bezpečnostní pojistka proti sebevraždě
        if "pkill python" in cmd and "-f" not in cmd:
            cmd = "pkill -f server.py"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout + result.stderr
    except Exception as e:
        return f"EXEC FAIL: {e}"

def check_server_health():
    # Zkusíme curl na port 5000 (Flask default)
    try:
        subprocess.check_output("curl -s --max-time 2 http://localhost:5000", shell=True)
        return True
    except:
        return False

def stress_test():
    print("   🔥 SPUŠTĚNÍ STRESS TESTU (50 requestů)...")
    try:
        # Rychlý test: 50 requestů
        cmd = 'for i in {1..50}; do curl -s -X POST -H "Content-Type: application/json" -d \'{"message": "Stress"}\' http://localhost:5000/log > /dev/null; done'
        subprocess.run(cmd, shell=True, timeout=10)
        
        # Kontrola, zda server přežil
        if check_server_health():
            return True, "Stress test PROŠEL. Server stabilní."
        else:
            return False, "Stress test SELHAL. Server spadl pod zátěží."
    except Exception as e:
        return False, f"Chyba testu: {e}"

def read_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return "".join(f.readlines()[-15:]) # Posledních 15 řádků
    return "Log file empty."

# 4. EXECUTOR (Smarter)
def execute_ai_plan(ai_text):
    # Hledáme bloky kódu
    code_blocks = re.findall(r'```(?:bash|sh)?\n(.*?)```', ai_text, re.DOTALL)
    commands = code_blocks if code_blocks else []
    
    # Fallback pro řádkové příkazy
    if not commands and "EXEC:" in ai_text:
        commands = [line.split("EXEC:", 1)[1].strip() for line in ai_text.split('\n') if "EXEC:" in line]

    log = ""
    for cmd in commands:
        print(f"   ⚡ VYKONÁVÁM: {cmd[:60]}...")
        log += run_cmd(cmd, timeout=30) + "\n"
    
    return log if log.strip() else "Žádné příkazy k vykonání."

# 5. HLAVNÍ SMYČKA ŘÍZENÍ
def overlord_loop():
    print(f"--- OMEGA OVERLORD: AUTONOMNÍ SMYČKA ({ITERATIONS} KOL) ---")
    
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    best = next((m for m in models if "flash" in m or "pro" in m), models[0])
    model = genai.GenerativeModel(best)
    chat = model.start_chat(history=[])

    status_msg = "START: Přebírám kontrolu nad 'SHADOW_REALM'. Server pravděpodobně neběží."

    for i in range(1, ITERATIONS + 1):
        print(f"\n🔄 [CYKLUS {i}/{ITERATIONS}] --------------------------")
        
        # A) DIAGNOSTIKA
        is_alive = check_server_health()
        server_logs = read_logs()
        
        if not is_alive:
            situation = "KRITICKÁ: Server neodpovídá (DOWN)."
            objective = "OPRAVIT A NASTARTOVAT. (Zkontroluj logy, doinstaluj knihovny, restartuj)."
        else:
            # Server běží -> Zátěžový test
            passed, msg = stress_test()
            if not passed:
                situation = f"VAROVÁNÍ: {msg}"
                objective = "STABILIZOVAT. (Server spadl při testu. Zjisti proč a oprav)."
            else:
                situation = "STABILNÍ: Server běží a prošel testem."
                objective = "EVOLUCE. (Přidej novou funkci do 'server.py' - např. nový endpoint '/stats' nebo lepší HTML). Restartuj pro aplikaci změn."

        print(f"   📊 STAV: {situation}")
        print(f"   🎯 CÍL: {objective}")

        # B) KONZULTACE S AI
        prompt = (
            f"Jsi OMEGA OVERLORD (SysAdmin). Nacházíš se v Termuxu.\n"
            f"STAV SYSTÉMU: {situation}\n"
            f"POSLEDNÍ LOGY:\n{server_logs}\n"
            f"TVŮJ ÚKOL: {objective}\n\n"
            f"INSTRUKCE:\n"
            f"1. Pokud chybí 'flask', nainstaluj ho (`pip install flask`).\n"
            f"2. Pokud upravuješ python kód, použij `cat << 'EOF' > server.py`.\n"
            f"3. Pro restart použij: `pkill -f server.py; nohup python3 server.py > server.log 2>&1 &`.\n"
            f"4. Všechny příkazy zabal do ```bash bloků."
        )

        try:
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"   🤖 AI PLÁNUJE: {ai_text[:80]}...")
            
            # C) EXEKUCE
            exec_log = execute_ai_plan(ai_text)
            print(f"   📝 VÝSLEDEK AKCE:\n{exec_log[:200]}...") # Zkrácený výpis
            
            # Pauza na nadechnutí serveru
            time.sleep(3)

        except Exception as e:
            print(f"❌ CHYBA CYKLU: {e}")
            break

    print("\n--- SMĚNA UKONČENA ---")
    if check_server_health():
        print("✅ VÍTĚZSTVÍ: Server přežil a běží.")
    else:
        print("⚠️ VÝSLEDEK: Server je momentálně dole.")

if __name__ == "__main__":
    overlord_loop()
