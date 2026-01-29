import os
import sys
import py_compile
import importlib.util
import time

# --- BARVY ---
GREEN = "\033[1;32m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def print_status(component, status, message=""):
    if status:
        print(f"   [{GREEN} OK {RESET}] {component:<20} {message}")
    else:
        print(f"   [{RED}FAIL{RESET}] {component:<20} {RED}{message}{RESET}")

def check_file(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        print_status(filename, True)
        return True
    else:
        print_status(filename, False, "Soubor nenalezen!")
        return False

def check_syntax(filename):
    path = os.path.join(BASE_DIR, filename)
    try:
        py_compile.compile(path, doraise=True)
        print_status(f"Syntax: {filename}", True)
        return True
    except py_compile.PyCompileError as e:
        print_status(f"Syntax: {filename}", False, f"Chyba kódu!")
        return False
    except Exception as e:
        print_status(f"Syntax: {filename}", False, str(e))
        return False

def check_import(module_name, filename):
    # Simulace importu (odhalí NameError, ImportError)
    path = os.path.join(BASE_DIR, filename)
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        print_status(f"Logic: {module_name}", True, "Modul se načetl v pořádku")
        return True
    except Exception as e:
        print_status(f"Logic: {module_name}", False, f"CRASH: {e}")
        return False

def run_audit():
    print(f"\n{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║     Ω  SYSTEM AUDIT (AUTO-TEST)      ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")
    print(f"LOKACE: {BASE_DIR}\n")

    # 1. KONTROLA SOUBORŮ
    print(f"{YELLOW}--- 1. INTEGRITA SOUBORŮ ---{RESET}")
    core_files = ["api_key.txt", "config.json", "omega_nexus.py", "omega_focus.py", "omega_brain.py", "omega_vitality.py", "omega_logger.py"]
    missing = 0
    for f in core_files:
        if not check_file(f): missing += 1
    
    if missing > 0:
        print(f"\n{RED}⛔ AUDIT ZASTAVEN: Chybí kritické soubory.{RESET}")
        return

    # 2. KONTROLA SYNTAXE
    print(f"\n{YELLOW}--- 2. KONTROLA SYNTAXE (Překlepy) ---{RESET}")
    scripts = ["omega_nexus.py", "omega_focus.py", "omega_brain.py", "omega_vitality.py"]
    syntax_errors = 0
    for s in scripts:
        if not check_syntax(s): syntax_errors += 1

    # 3. KONTROLA LOGIKY (Importy)
    print(f"\n{YELLOW}--- 3. SIMULACE BĚHU (Logika) ---{RESET}")
    logic_errors = 0
    # Testujeme jen ty, které nespouští nekonečné smyčky při importu
    safe_modules = [
        ("omega_brain", "omega_brain.py"),
        ("omega_vitality", "omega_vitality.py"),
        ("omega_logger", "omega_logger.py")
        # Nexus a Focus testujeme jen na syntax, protože by se spustily smyčky
    ]
    
    for name, file in safe_modules:
        if not check_import(name, file): logic_errors += 1

    # VÝSLEDEK
    print(f"\n{CYAN}══════════════════════════════════════{RESET}")
    if syntax_errors == 0 and logic_errors == 0:
        print(f"{GREEN}✅ VŠECHNY TESTY PROŠLY. SYSTÉM JE STABILNÍ.{RESET}")
        print("Můžeš bezpečně spustit 'gonexus'.")
    else:
        print(f"{RED}❌ DETEKOVÁNY CHYBY. ZKONTROLUJ VÝPIS VÝŠE.{RESET}")

if __name__ == "__main__":
    run_audit()
