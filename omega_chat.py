import google.generativeai as genai
import sys
import os
import json
import glob
import subprocess
from omega_config import config

# BARVY
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[0m"

# KONFIGURACE
API_KEY_FILE = config.get('ai', {}).get('api_key_file', "api_key.txt")
MODEL_NAME = config.get('ai', {}).get('model', 'models/gemini-pro-latest')

def get_system_context():
    """Vytvoří 'paměť' pro AI o aktuálním stavu projektu"""
    try:
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        files_str = ", ".join(files)
        with open("config.json", "r") as f:
            conf_data = f.read()
    except:
        files_str = "Unknown"
        conf_data = "Config Error"

    context = f"""
    Jsi OMEGA PRIME (v8.4 SMS), pokročilý systém v Termuxu.
    LOKACE: ~/OmegaCore
    SOUBORY: {files_str}
    CONFIG: {conf_data}
    INSTRUKCE: Odpovídej stručně, jako v SMS chatu. Buď užitečná.
    """
    return context

def get_android_input():
    """Otevře nativní Android okno pro psaní (Gboard friendly)"""
    try:
        # Volání Termux API pro dialog
        result = subprocess.run(
            ["termux-dialog", "text", "-t", "Ω OMEGA LINK", "-i", "Zpráva..."], 
            capture_output=True, text=True
        )
        # Parsování JSON odpovědi
        if result.stdout:
            data = json.loads(result.stdout)
            # kód -1 = Potvrzeno, -2 = Zrušeno
            if data.get("code") == -1:
                return data.get("text", "").strip()
            else:
                return "exit" # Uživatel kliknul na Zrušit
    except FileNotFoundError:
        # Fallback pokud není nainstalované Termux:API
        print(f"{RED}⚠️ Termux:API nenalezeno, používám terminál.{RESET}")
        return input(f"{GREEN}TY > {RESET}")
    except Exception:
        return input(f"{GREEN}TY > {RESET}")
    
    return "exit"

def init_chat():
    os.system('clear')
    print(f"{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║   Ω  NEURAL LINK v2.1 (GBOARD)       ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")
    print(f" {YELLOW}📡 Model: {MODEL_NAME}{RESET}")
    print(f" {YELLOW}📱 Režim: Nativní SMS Input{RESET}\n")

    try:
        with open(API_KEY_FILE, "r") as f:
            genai.configure(api_key=f.read().strip())
        
        system_prompt = get_system_context()
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_prompt)
        chat = model.start_chat(history=[])
        return chat
    except Exception as e:
        print(f"{RED}❌ CHYBA PŘIPOJENÍ: {e}{RESET}")
        return None

def main():
    chat_session = init_chat()
    if not chat_session: return

    print(f"{CYAN}[SPOJENÍ NAVÁZÁNO. OTEVÍRÁM SMS KANÁL...]{RESET}\n")

    while True:
        try:
            # 1. Získání vstupu přes Android Dialog
            user_msg = get_android_input()
            
            # Kontrola ukončení
            if user_msg.lower() in ['exit', 'quit', 'konec']:
                print(f"{YELLOW}🔌 Spojení ukončeno.{RESET}")
                break
            
            if not user_msg: continue

            # Vypsání tvé zprávy do terminálu (aby byla vidět historie)
            print(f"{GREEN}TY > {RESET}{user_msg}")

            # 2. Odeslání do AI
            sys.stdout.write(f"{CYAN}    (Omega píše...){RESET}")
            sys.stdout.flush()
            
            response = chat_session.send_message(user_msg)
            
            sys.stdout.write("\r" + " " * 20 + "\r") 
            print(f"{CYAN}Ω > {RESET}{response.text}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n{RED}❌ CHYBA: {e}{RESET}")

if __name__ == "__main__":
    main()
