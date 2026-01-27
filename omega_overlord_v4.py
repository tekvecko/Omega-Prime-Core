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

# 3. BEZPEČNOSTNÍ FILTR (NÁHUBEK)
def sanitize_cmd(cmd):
    # Pokud chce AI zabít python, donutíme ji zabít jen server.py
    if "pkill python" in cmd or "killall python" in cmd:
        print(f"⚠️ ZACHYCEN SEBEVRAŽEDNÝ PŘÍKAZ: '{cmd}' -> PŘEPISUJI NA 'pkill -f server.py'")
        return "pkill -f server.py"
    return cmd

def run_cmd(cmd, timeout=30):
    cmd = sanitize_cmd(cmd) # Aplikace filtru
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        return output if output.strip() else "OK (Silent success)."
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
    try:
        subprocess.check_output("pgrep -f server.py", shell=True)
    except:
        return False, "Proces server.py NEBĚŽÍ."
    
    try:
        subprocess.check_output("curl -s --max-time 2 http://localhost:5000", shell=True)
        return True, "ONLINE"
    except:
        return False, "Proces běží, ale PORT 5000 neodpovídá."

def read_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            return "".join(lines[-30:]) 
    return "Log file empty."

# 4. EXECUTOR
def execute_ai_plan(ai_text):
    log_output = ""
    
    # Python Direct Write
    python_blocks = re.findall(r'```python\n(.*?)```', ai_text, re.DOTALL)
    if python_blocks:
        print("   💾 PŘEPISUJI KÓD SERVERU...")
        log_output += write_file_directly(SERVER_FILE, python_blocks[0]) + "\n"

    # Shell Commands
    bash_blocks = re.findall(r'```bash\n(.*?)```', ai_text, re.DOTALL)
    commands = bash_blocks if bash_blocks else []
    
    if not commands and "EXEC:" in ai_text:
        commands = [line.split("EXEC:", 1)[1].strip() for line in ai_text.split('\n') if "EXEC:" in line]

    for cmd in commands:
        if "cat <<" in cmd and python_blocks: continue # Skip cat if we used direct write
        
        print(f"   ⚡ VYKONÁVÁM: {cmd[:50]}...")
        log_output += run_cmd(cmd) + "\n"
    
    return log_output if log_output.strip() else "Žádná akce."

# 5. HLAVNÍ SMYČKA
def overlord_loop():
    print(f"--- OMEGA OVERLORD v4: IMMORTAL MODE ---")
    
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
            objective = "OPRAVA. Zkontroluj logy, uprav kód (zabal do ```python) a restartuj (zabal do ```bash)."
        else:
            stable_streak += 1
            situation = "STABILNÍ: Server běží."
            objective = "ÚDRŽBA. Nic neměň."

        if stable_streak >= REQUIRED_STABLE_STREAK:
            print(f"\n🏆 MISSE SPLNĚNA! Server je stabilní.")
            break

        prompt = (
            f"Jsi OMEGA OVERLORD v4.\n"
            f"STAV: {situation}\n"
            f"LOGY: \n{server_logs}\n"
            f"CÍL: {objective}\n"
            f"INSTRUKCE:\n"
            f"1. Kód Pythonu zabal do ```python (přímý zápis).\n"
            f"2. Příkazy shellu zabal do ```bash.\n"
            f"3. PRO RESTART POUŽIJ: pkill -f server.py; nohup python3 server.py > server.log 2>&1 &"
        )

        try:
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"   🤖 AI PLÁNUJE: {ai_text[:80]}...")
            
            exec_log = execute_ai_plan(ai_text)
            print(f"   📝 VÝSTUP: {exec_log.strip()[:200]}...")
            
            time.sleep(3)

        except Exception as e:
            print(f"❌ CHYBA: {e}")
            break

if __name__ == "__main__":
    overlord_loop()
