import os
import subprocess
import time

# --- BARVY ---
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[0m"

def run_cmd(cmd):
    try:
        os.system(cmd)
    except Exception as e:
        print(f"{RED}Chyba: {e}{RESET}")

def package_manager():
    while True:
        print(f"\n{CYAN}╔══════════════════════════════════════╗{RESET}")
        print(f"{CYAN}║     Ω  PKG MASTER (SYSTEM UPDATE)    ║{RESET}")
        print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")
        print("   [1] 🔄 AKTUALIZOVAT SYSTÉM (Update & Upgrade)")
        print("   [2] 🔍 Hledat balíček")
        print("   [3] 📥 Instalovat balíček")
        print("   [4] 🗑️  Odinstalovat balíček")
        print("   [5] 🐍 Instalovat Python knihovnu (PIP)")
        print("   [0] Zpět")

        choice = input(f"\n{YELLOW}PKG > {RESET}")

        if choice == '1':
            print(f"{YELLOW}Spouštím aktualizaci...{RESET}")
            run_cmd("pkg update -y && pkg upgrade -y")
            print(f"{GREEN}Hotovo.{RESET}")
            input("Enter...")

        elif choice == '2':
            query = input("Hledat: ")
            run_cmd(f"pkg search {query}")
            input("Enter...")

        elif choice == '3':
            pkg = input("Název balíčku k instalaci: ")
            run_cmd(f"pkg install {pkg} -y")
            input("Enter...")

        elif choice == '4':
            pkg = input("Název balíčku k odstranění: ")
            run_cmd(f"pkg uninstall {pkg} -y")
            input("Enter...")
        
        elif choice == '5':
            lib = input("Název Python lib (pip): ")
            run_cmd(f"pip install {lib}")
            input("Enter...")

        elif choice == '0':
            break

if __name__ == "__main__":
    package_manager()
