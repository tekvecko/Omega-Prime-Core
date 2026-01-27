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
MAX_CYCLES = 10
REQUIRED_STABLE_STREAK = 3

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
        # Povolení nohup a tichých příkazů
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        return output if output.strip() else "OK (Příkaz proveden tiše)."
    except Exception as e:
        return f"EXEC FAIL: {e}"

def write_file_directly(filename, content):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"SOUBOR ZAPSÁN: {filename} ({len(content)} bytů)"
    except Exception as e:
        return f"CHYBA ZÁPISU: {e}"

def check_server_health():
    # 1. Proces
    try:
        subprocess.check_output("pgrep -f server.py", shell=True)
    except:
        return False, "Proces neběží."
    # 2. Port
    try:
        subprocess.check_output("curl -s --max-time 2 http://localhost:5000", shell=True)
        return True, "ONLINE"
    except:
        return False, "Proces běží, ale PORT neodpovídá."

def read_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            return "".join(lines[-30:]) 
    return "Log file empty."

# 4. EXECUTOR (Smarter)
def execute_ai_plan(ai_text):
    log_output = ""
    
    # A) HLEDÁNÍ PYTHON KÓDU PRO PŘÍMÝ ZÁPIS
    python_blocks = re.findall(r'```python\n(.*?)```', ai_text, re.DOTALL)
    if python_blocks:
        print("   💾 DETEKOVÁN KÓD: Provádím přímý zápis do 'server.py'...")
        log_output += write_file_directly(SERVER_FILE, python_blocks[0]) + "\n"

    # B) HLEDÁNÍ SHELL PŘÍKAZŮ (Restart, Install)
    bash_blocks = re.findall(r'```bash\n(.*?)```', ai_text, re.DOTALL)
    commands = bash_blocks if bash_blocks else []
    
    # Fallback pro starý formát
    if not commands and "EXEC:" in ai_text:
        commands = [line.split("EXEC:", 1)[1].strip() for line in ai_text.split('\n') if "EXEC:" in line]

    for cmd in commands:
        # Ignorujeme cat, pokud jsme už zapsali soubor pythonem
        if "cat <<" in cmd and python_blocks:
            continue
            
        print(f"   ⚡ VYKONÁVÁM: {cmd[:60]}...")
        log_output += run_cmd(cmd) + "\n"
    
    return log_output if log_output.strip() else "Žádná akce."

# 5. HLAVNÍ SMYČKA
def overlord_loop():
    print(f"--- OMEGA OVERLORD v3: DIRECT WRITE PROTOCOL ---")
    
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    best = next((m for m in models if "flash" in m or "pro" in m), models[0])
    model = genai.GenerativeModel(best)
    chat = model.start_chat(history=[])

    cycle = 0
    stable_streak = 0

    while cycle < MAX_CYCLES:
        cycle += 1
        print(f"\n🔄 [CYKLUS {cycle}] (Streak: {stable_streak}/{REQUIRED_STABLE_STREAK})")
        
        is_up, health_msg = check_server_health()
        server_logs = read_logs()
        
        if not is_up:
            stable_streak = 0
            situation = f"KRITICKÁ: {health_msg}"
            objective = "OPRAVA. Přepiš kód serveru (zabal ho do ```python) a restartuj."
        else:
            stable_streak += 1
            situation = "STABILNÍ: Server běží."
            objective = "ÚDRŽBA. Nic neměň, jen potvrď stav."

        if stable_streak >= REQUIRED_STABLE_STREAK:
            print(f"\n🏆 MISSE SPLNĚNA! Server je stabilní.")
            break

        prompt = (
            f"Jsi OMEGA OVERLORD v3.\n"
            f"STAV: {situation}\n"
            f"POSLEDNÍ LOG (Důvod pádu): \n{server_logs}\n\n"
            f"CÍL: {objective}\n"
            f"INSTRUKCE:\n"
            f"1. Nový kód serveru zabal do ```python (já ho zapíšu na disk).\n"
            f"2. Restart příkaz zabal do ```bash (pkill -f server.py; nohup python3 server.py > server.log 2>&1 &).\n"
            f"3. Pokud v logu vidíš 'Address already in use', použij `pkill python`."
        )

        try:
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"   🤖 AI PLÁNUJE: {ai_text[:80]}...")
            
            exec_log = execute_ai_plan(ai_text)
            print(f"   📝 VÝSTUP AKCE:\n{exec_log.strip()}")
            
            # Catch-on-Boot: Rychlá kontrola logu po startu
            time.sleep(2)
            if "nohup" in exec_log:
                new_log = read_logs()
                if "Traceback" in new_log or "Error" in new_log:
                    print(f"   ⚠️ VAROVÁNÍ: Server asi spadl při startu! Log:\n{new_log[:200]}...")

        except Exception as e:
            print(f"❌ CHYBA: {e}")
            break

    print(f"\n--- UKONČENO ---")

if __name__ == "__main__":
    overlord_loop()
