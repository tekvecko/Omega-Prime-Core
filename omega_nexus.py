import os
import time
import subprocess
import sys
import json

# --- MODULY ---
# (Importujeme jen ty, které potřebujeme přímo, zbytek voláme přes subprocess)
try:
    import omega_voice
except ImportError:
    omega_voice = None

# --- ABSOLUTNÍ KOTVA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEY_FILE = os.path.join(BASE_DIR, "api_key.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
SHADOW_DIR = os.path.join(BASE_DIR, "SHADOW_REALM")
LOG_FILE = os.path.join(BASE_DIR, "nohup.out")

# --- BARVY ---
GREEN = "\033[1;32m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
RESET = "\033[0m"

def say(text):
    if omega_voice:
        omega_voice.speak(text)
    print(f"{BLUE}🗣️  OMEGA: {text}{RESET}")

def log_error(message):
    print(f"{RED}{message}{RESET}")
    with open(LOG_FILE, "a") as f:
        f.write(f"[NEXUS ERROR] {message}\n")

def run_module(script_name, env):
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        log_error(f"Soubor nenalezen: {script_name}")
        return
    with open(LOG_FILE, "a") as log_f:
        try:
            subprocess.run(["python3", script_path], env=env, stderr=log_f, stdout=log_f)
        except Exception as e:
            log_error(f"Pád modulu {script_name}: {e}")

def select_environment():
    print(f"\n{CYAN}🌍 OMEGA: VÝBĚR PROSTŘEDÍ{RESET}")
    if not os.path.exists(SHADOW_DIR): os.makedirs(SHADOW_DIR)
    dbs = sorted([f for f in os.listdir(SHADOW_DIR) if f.endswith(".db")])
    options = sorted(list(set(["omega.db", "prace.db", "doma.db"] + dbs)))
    
    for i, db in enumerate(options):
        print(f"   [{i+1}] {db}")
    
    print(f"{YELLOW}   (Auto-výběr '{options[0]}' za 5s...){RESET}")
    import select
    i, o, e = select.select([sys.stdin], [], [], 5)
    if i:
        choice = sys.stdin.readline().strip()
        if choice.isdigit() and 0 < int(choice) <= len(options):
            return options[int(choice)-1]
    return options[0]

def nexus_loop():
    active_db = select_environment()
    say(f"Nexus Online. Sektor {active_db}")
    
    env = os.environ.copy()
    env["OMEGA_DB_PATH"] = os.path.join(SHADOW_DIR, active_db)

    while True:
        try:
            # 1. INTEGRITA (Sentinel)
            print(f"\n{GREEN}🛡️  Sentinel Check...{RESET}")
            run_module("omega_sentinel.py", env)

            # 2. SÍŤ (Hunter)
            print(f"{CYAN}📡 Hunter Scan... (Výstup v logu){RESET}")
            run_module("omega_lan_reaper.py", env)
            
            # 3. ANALÝZA (Brain)
            print(f"{YELLOW}🧠 Brain Activity...{RESET}")
            run_module("omega_brain.py", env)
            
            # 4. VITALITA
            print(f"{GREEN}❤️ Vitality...{RESET}")
            run_module("omega_vitality.py", env)

            print(f"{BLUE}💤 Spánek 60s...{RESET}")
            time.sleep(60)

        except KeyboardInterrupt:
            say("Systém ukončen.")
            break
        except Exception as e:
            log_error(f"KRITICKÁ CHYBA: {e}")
            time.sleep(5)

if __name__ == "__main__":
    nexus_loop()
