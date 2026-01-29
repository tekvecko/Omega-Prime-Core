import os
import sys
import warnings

# FILTR VAROVÁNÍ (Hned na začátku)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import google.generativeai as genai
from omega_config import config

# --- KONFIGURACE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "nohup.out")
API_KEY_FILE = os.path.join(BASE_DIR, "api_key.txt")

# BARVY
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
RESET = "\033[0m"

def analyze_and_repair():
    print(f"\n{CYAN}🔍 Čtu posledních 40 řádků z nohup.out...{RESET}")
    
    if not os.path.exists(LOG_FILE):
        print(f"{RED}❌ Log soubor neexistuje.{RESET}")
        return

    try:
        # Přečteme poslední řádky (Linux tail style)
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            last_lines = lines[-40:] if len(lines) > 40 else lines
            log_content = "".join(last_lines)
            
        # Jednoduchá detekce chyb
        if "Traceback" in log_content or "Error" in log_content:
            print(f"{RED}⚠️ NALEZENY CHYBY V LOGU!{RESET}")
        else:
            print(f"{GREEN}✅ V posledních řádcích nevidím žádné zjevné chyby.{RESET}")
            print("   (Tip: Pokud jsi chybu vyvolal před chvílí, možná je výš v logu.)")

        choice = input(f"{YELLOW}   Chceš i přesto spustit AI analýzu? (a/n): {RESET}")
        if choice.lower() != 'a':
            return

        # AI ANALÝZA
        try:
            with open(API_KEY_FILE, "r") as f:
                genai.configure(api_key=f.read().strip())
            
            # Použijeme model z configu
            model_name = config.get('ai', {}).get('model', 'gemini-2.5-flash')
            print(f"🧠 Odesílám data modelu: {model_name}...")
            
            model = genai.GenerativeModel(model_name)
            
            prompt = (
                f"Jsi Omega Prime System Admin. Tady je posledních 40 řádků logu.\n"
                f"Pokud vidíš chybu, vysvětli ji česky a navrhni opravu (Python kód).\n"
                f"LOG:\n{log_content}"
            )
            
            response = model.generate_content(prompt)
            print(f"\n{GREEN}Ω DIAGNÓZA:{RESET}\n{response.text}")

        except Exception as e:
            print(f"{RED}❌ Chyba připojení k AI: {e}{RESET}")

    except Exception as e:
        print(f"{RED}❌ Chyba čtení logu: {e}{RESET}")

def manage_logs():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "show":
            os.system(f"tail -n 50 {LOG_FILE}")
            input("\n[Enter...]")
        elif cmd == "copy":
            os.system(f"cat {LOG_FILE} | termux-clipboard-set")
            print("📋 Zkopírováno.")
        elif cmd == "clear":
            open(LOG_FILE, 'w').close()
            print("🗑️ Log vymazán.")
        elif cmd == "repair":
            analyze_and_repair()
    else:
        print("Použití: python3 omega_logger.py [show|copy|clear|repair]")

if __name__ == "__main__":
    manage_logs()
