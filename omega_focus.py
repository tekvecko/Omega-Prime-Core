import os
import sys
import google.generativeai as genai
import subprocess
import re
import json
import time
from omega_config import config

# --- KONFIGURACE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEY_FILE = os.path.join(BASE_DIR, "api_key.txt")
STAGING_FILE = os.path.join(BASE_DIR, "omega_staging.py")
HISTORY_FILE = os.path.join(BASE_DIR, "prompt_history.json")
LOG_FILE = os.path.join(BASE_DIR, "nohup.out")

# Barvy
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[0m"

def save_to_history(text):
    data = {"history": [], "saved": []}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
        except: pass
    
    entry = {"text": text, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    data['history'].append(entry)
    
    if len(data['history']) > 100:
        data['history'] = data['history'][-100:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def send_notification(title, content):
    try:
        subprocess.run(["termux-notification", "--title", title, "--content", content], check=False)
        subprocess.run(["termux-vibrate", "-d", "200"], check=False)
    except: pass

def ask_approval():
    print(f"\n{YELLOW}👀 ZKONTROLUJ KÓD VÝŠE.{RESET}")
    input(f"{CYAN}   [Stiskni ENTER pro otevření hlasování...]{RESET}")
    try:
        result = subprocess.run(
            ["termux-dialog", "confirm", "-t", "Ω OMEGA PROTOCOL", "-i", "Je kód v pořádku? Spustit?"],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        return data.get("text") == "yes"
    except:
        choice = input(f"{YELLOW}Schválit spuštění? (ano/ne): {RESET}")
        return choice.lower().startswith('a')

def extract_code(text):
    match = re.search(r"```(?:python|bash)?\n(.*?)```", text, re.DOTALL)
    if match: return match.group(1)
    return None

def focus_mode():
    print(f"\n{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║    Ω  FOCUS v2.4 (LIVE LOGGING)      ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")

    try:
        with open(API_KEY_FILE, "r") as f:
            genai.configure(api_key=f.read().strip())
        model_name = config.get('ai', {}).get('model', 'gemini-pro')
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"❌ CHYBA API: {e}")
        return

    while True:
        task = input(f"\n{YELLOW}ZADEJ ÚKOL (nebo 'exit'): {RESET}")
        if task.lower() in ['exit', 'quit']: break
        
        save_to_history(task)

        print(f"{CYAN}🧠 Generuji řešení...{RESET}")
        
        prompt = (
            f"Jsi Omega Prime. Uživatel chce: '{task}'.\n"
            f"1. Napiš kompletní, funkční Python skript (nebo Bash), který to vyřeší v Termuxu.\n"
            f"2. Kód uzavři do bloku ```.\n"
            f"3. DŮLEŽITÉ: Pokud generuješ HTML/CSS obsah uvnitř Pythonu, NEPOUŽÍVEJ funkci `.format()`, "
            f"protože koliduje se složenými závorkami {{}} v CSS. Místo toho použij f-stringy nebo replace().\n"
            f"4. Nepiš omáčku, hlavně funkční kód."
        )
        
        try:
            response = model.generate_content(prompt)
            print(f"\n{GREEN}Ω NÁVRH:{RESET}\n{response.text}")
            
            code = extract_code(response.text)
            
            if code:
                print(f"\n{YELLOW}⚡ DETEKOVÁN KÓD K IMPLEMENTACI.{RESET}")
                send_notification("OMEGA PRIME", "Kód připraven k revizi.")
                
                if ask_approval():
                    print(f"{GREEN}✅ SCHVÁLENO. Spouštím...{RESET}")
                    with open(STAGING_FILE, "w") as f:
                        f.write(code)
                    
                    print(f"{CYAN}----------------------------------------{RESET}")
                    
                    # --- ZMĚNA: LOGOVÁNÍ ---
                    # 2>&1 = pošli chyby do stejného kanálu jako text
                    # | tee -a log.txt = zobraz na displeji A PŘIDEJ do logu
                    cmd = f"python3 {STAGING_FILE} 2>&1 | tee -a {LOG_FILE}"
                    
                    # Zápis oddělovače do logu, ať víme, kdy to začalo
                    os.system(f"echo '\n--- FOCUS RUN START ({time.strftime('%H:%M:%S')}) ---' >> {LOG_FILE}")
                    
                    # Spuštění s nahráváním
                    try:
                        os.system(cmd)
                    except Exception as r:
                        print(f"{RED}❌ CHYBA BĚHU: {r}{RESET}")
                        
                    print(f"{CYAN}----------------------------------------{RESET}")
                    print(f"{GREEN}✅ Dokončeno (Výstup uložen do logu).{RESET}")
                else:
                    print(f"{RED}❌ ZAMÍTNUTO. Kód zahozen.{RESET}")
        except Exception as e:
            print(f"❌ Chyba: {e}")

if __name__ == "__main__":
    focus_mode()
