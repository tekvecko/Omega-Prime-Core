import os
import sys
import time
import subprocess
# Načítáme konfiguraci, aby menu vědělo, jaký model běží
try:
    from omega_config import config
except ImportError:
    config = {}

# --- BARVY A STYL ---
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
PURPLE = "\033[1;35m"
BLUE = "\033[1;34m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Načtení info z configu
VERSION = config.get("system", {}).get("version", "v9.1")
MODEL = config.get("ai", {}).get("model", "Unknown")

def clear_screen():
    os.system('clear')

def run_script(script_name):
    """Spustí python skript a po skončení čeká"""
    if os.path.exists(script_name):
        try:
            # Spuštění skriptu
            subprocess.run(["python3", script_name])
        except KeyboardInterrupt:
            print(f"\n{RED}🚫 Přerušeno uživatelem.{RESET}")
    else:
        print(f"{RED}❌ Chyba: Soubor {script_name} neexistuje!{RESET}")
        time.sleep(1)

def print_header():
    clear_screen()
    print(f"{BLUE}══════════════════════════════════════════════{RESET}")
    print(f"{CYAN}   Ω OMEGA PRIME [{VERSION}] | AI: {MODEL}{RESET}")
    print(f"{BLUE}══════════════════════════════════════════════{RESET}")

def menu_dev_tools():
    while True:
        print(f"\n   {YELLOW}--- DEV TOOLS ---{RESET}")
        print("   [a] Brain (Test AI)")
        print("   [b] Hunter (Nmap Sken)")
        print("   [c] Vitality (System Info)")
        print("   [d] Sentinel (Integrity Check)")
        print("   [0] Zpět")
        
        choice = input(f"\n   {YELLOW}DEV > {RESET}")
        
        if choice == 'a': run_script("omega_brain.py")
        elif choice == 'b': run_script("omega_lan_reaper.py")
        elif choice == 'c': run_script("omega_vitality.py")
        elif choice == 'd': run_script("omega_sentinel.py")
        elif choice == '0': break

def menu_shadow_realm():
    while True:
        print(f"\n   {PURPLE}--- SHADOW REALM ---{RESET}")
        print("   [A] MANUAL SHELL (Isolated Bash)")
        print("   [B] AUTONOMOUS NODE (AI Loop)")
        print("   [0] Zpět")
        
        choice = input(f"\n   {PURPLE}SHADOW > {RESET}").lower()
        
        if choice == 'a': run_script("omega_shadow.py")
        elif choice == 'b': run_script("omega_shadow_node.py")
        elif choice == '0': break

def menu_logs():
    while True:
        print(f"\n   {RED}--- LOG MANAGEMENT ---{RESET}")
        print("   [A] Zobrazit log")
        print("   [B] Kopírovat log")
        print("   [C] AI OPRAVA")
        print("   [D] Smazat log")
        print("   [0] Zpět")
        
        choice = input(f"\n   {RED}LOG > {RESET}").lower()
        
        if choice == 'a': os.system("python3 omega_logger.py show")
        elif choice == 'b': os.system("python3 omega_logger.py copy")
        elif choice == 'c': os.system("python3 omega_logger.py repair")
        elif choice == 'd': os.system("python3 omega_logger.py clear")
        elif choice == '0': break

def main_menu():
    while True:
        print_header()
        
        print(f"{GREEN}   [1] EXECUTE (Loop)   [2] FOCUS (Task){RESET}")
        print(f"{YELLOW}   [3] DEV TOOLS        [4] SHADOW REALM{RESET}")
        print(f"{CYAN}   [P] PACKAGES (Mgmt)  [H] HISTORY (Prompts){RESET}")
        print(f"{RED}   [S] STRESS TEST      [L] LOG & REPAIR{RESET}")
        print(f"{PURPLE}   [5] DASHBOARD        [C] SMS CHAT{RESET}")
        print(f"{BLUE}   [F] FACTORY (Create){RESET}")
        
        print(f"{BLUE}──────────────────────────────────────────────{RESET}")
        print(f"   [6] KILL  [7] BACKUP  [8] EXIT")
        
        choice = input(f"\n   {CYAN}OMEGA > {RESET}").lower()

        if choice == '1': run_script("omega_nexus.py")
        elif choice == '2': 
            os.environ["OMEGA_DB_PATH"] = "omega.db"
            run_script("omega_focus.py")
        elif choice == '3': menu_dev_tools()
        elif choice == '4': menu_shadow_realm()
        
        elif choice == 'p': run_script("omega_packages.py")
        elif choice == 'h': run_script("omega_prompts.py")
        elif choice == 's': run_script("omega_stress_test.py")
        elif choice == 'l': menu_logs()
        
        elif choice == '5':
            # Dashboard logic - získáme IP
            try:
                ip = subprocess.check_output("ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1", shell=True).decode().strip()
            except: ip = "127.0.0.1"
            if not ip: ip = "127.0.0.1"
            
            print(f"   Startuji server na: http://{ip}:5000/dashboard")
            os.system("pkill -f server.py > /dev/null 2>&1")
            os.system("nohup python3 server.py > /dev/null 2>&1 &")
            os.system(f"termux-open-url http://{ip}:5000/dashboard")
            input("   [Stiskni Enter pro návrat do menu...]")

        elif choice == 'c': run_script("omega_chat.py")
        elif choice == 'f': run_script("omega_factory.py")
        
        elif choice == '6': 
            os.system("pkill -f python3")
            print("   🚫 Všechny procesy Python ukončeny.")
            time.sleep(1)
            
        elif choice == '7':
            print("   Zálohuji na GitHub...")
            os.system("git add .; git commit -m 'AutoBackup'; git push")
            input("   [Hotovo. Enter...]")
            
        elif choice == '8': 
            print("   👋 Odhlašuji...")
            break
        
        elif choice == '': pass
        else:
            print("   ⚠️ Neplatná volba.")
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n   👋 Force Exit.")
