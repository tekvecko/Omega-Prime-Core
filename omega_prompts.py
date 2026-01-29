import os
import json
import time
import subprocess

# --- BARVY ---
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[0m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "prompt_history.json")

def load_db():
    if not os.path.exists(DB_FILE):
        return {"history": [], "saved": []}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"history": [], "saved": []}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def copy_to_clipboard(text):
    try:
        process = subprocess.Popen(['termux-clipboard-set'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
        print(f"{GREEN}✅ Zkopírováno do schránky.{RESET}")
    except:
        print(f"{RED}⚠️ Termux API chybí (nelze kopírovat).{RESET}")

def manage_prompts():
    while True:
        data = load_db()
        print(f"\n{CYAN}╔══════════════════════════════════════╗{RESET}")
        print(f"{CYAN}║     Ω  PROMPT VAULT (MEMORY)         ║{RESET}")
        print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")
        print(f"   [1] Zobrazit HISTORII ({len(data['history'])})")
        print(f"   [2] Zobrazit ULOŽENÉ ({len(data['saved'])})")
        print(f"   [3] Uložit nový prompt")
        print(f"   [4] Vyčistit historii")
        print(f"   [0] Zpět")

        choice = input(f"\n{YELLOW}VAULT > {RESET}")

        if choice == '1':
            print(f"\n{CYAN}--- POSLEDNÍCH 10 PROMPTŮ ---{RESET}")
            for i, item in enumerate(reversed(data['history'][-10:])):
                print(f"{YELLOW}[{i+1}]{RESET} {item['timestamp']} | {item['text'][:60]}...")
            
            sel = input(f"\n{CYAN}Vyber číslo pro detail/kopírování (nebo Enter): {RESET}")
            if sel.isdigit() and 0 < int(sel) <= 10:
                idx = -int(sel)
                full_text = data['history'][idx]['text']
                print(f"\n{GREEN}{full_text}{RESET}")
                copy_to_clipboard(full_text)
                input("Stiskni Enter...")

        elif choice == '2':
            print(f"\n{CYAN}--- ULOŽENÉ ŠABLONY ---{RESET}")
            for i, item in enumerate(data['saved']):
                print(f"{YELLOW}[{i+1}]{RESET} {item['title']}")
            
            sel = input(f"\n{CYAN}Vyber číslo (nebo Enter): {RESET}")
            if sel.isdigit() and 0 < int(sel) <= len(data['saved']):
                item = data['saved'][int(sel)-1]
                print(f"\n{CYAN}NÁZEV:{RESET} {item['title']}")
                print(f"{GREEN}{item['text']}{RESET}")
                copy_to_clipboard(item['text'])
                
                act = input(f"Smazat? (ano/ne): ")
                if act.lower().startswith('a'):
                    data['saved'].pop(int(sel)-1)
                    save_db(data)
                    print("Smazáno.")

        elif choice == '3':
            title = input("Název promptu: ")
            text = input("Text promptu: ")
            data['saved'].append({"title": title, "text": text, "timestamp": time.strftime("%Y-%m-%d %H:%M")})
            save_db(data)
            print(f"{GREEN}Uloženo.{RESET}")

        elif choice == '4':
            confirm = input("Smazat celou historii? (ano/ne): ")
            if confirm.lower() == 'ano':
                data['history'] = []
                save_db(data)
                print("Historie vymazána.")

        elif choice == '0':
            break

if __name__ == "__main__":
    manage_prompts()
