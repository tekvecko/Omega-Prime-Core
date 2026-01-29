import os
import sys
import subprocess
import time
import socket
import threading

# --- BARVY ---
GREEN = "\033[1;32m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "nohup.out")

def print_header():
    print(f"\n{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║     Ω  OMEGA PRIME: FINAL EXAM       ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")
    print(f"Time: {time.strftime('%H:%M:%S')}")
    print(f"Mode: ACTIVE SYSTEM TEST\n")

def check_file(filename):
    """Ověří existenci souboru"""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        print(f"   [FILE] {filename:<25} {GREEN}OK{RESET}")
        return True
    else:
        print(f"   [FILE] {filename:<25} {RED}MISSING{RESET}")
        return False

def test_module_syntax(script_name):
    """Zkusí zkompilovat skript (odhalí syntax error)"""
    try:
        subprocess.check_output(["python3", "-m", "py_compile", script_name], stderr=subprocess.STDOUT)
        print(f"   [CODE] {script_name:<25} {GREEN}VALID{RESET}")
        return True
    except subprocess.CalledProcessError:
        print(f"   [CODE] {script_name:<25} {RED}SYNTAX ERROR{RESET}")
        return False

def test_server_live():
    """Skutečně spustí server a zkusí se připojit"""
    print(f"\n{YELLOW}⚡ TESTUJI DASHBOARD SERVER (Live Boot)...{RESET}")
    
    # 1. Start serveru na pozadí
    try:
        server_process = subprocess.Popen(
            ["python3", "server.py"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"   {RED}❌ Server nelze spustit: {e}{RESET}")
        return False

    # 2. Čekání na boot
    print("   ⏳ Čekám 3s na start serveru...")
    time.sleep(3)

    # 3. Test spojení na port 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()

    # 4. Úklid (zabití serveru)
    server_process.terminate()
    server_process.wait()

    if result == 0:
        print(f"   [HTTP] Port 5000 (Dashboard)      {GREEN}ONLINE (Odpovídá){RESET}")
        return True
    else:
        print(f"   [HTTP] Port 5000 (Dashboard)      {RED}OFFLINE (Neodpovídá){RESET}")
        print(f"   {YELLOW}Tip: Zkontroluj jestli 'server.py' neběží v jiném okně.{RESET}")
        return False

def run_exam():
    print_header()
    score = 0
    total = 0

    # 1. INTEGRITA SOUBORŮ
    print(f"{YELLOW}--- 1. KONTROLA ARZENÁLU ---{RESET}")
    files = [
        "omega_nexus.py", "omega_lan_reaper.py", "omega_brain.py",
        "omega_sentinel.py", "server.py", "interface.sh", "api_key.txt"
    ]
    for f in files:
        if check_file(f): score += 1
        total += 1

    # 2. KONTROLA KÓDU
    print(f"\n{YELLOW}--- 2. ANALÝZA NEURONŮ (Syntax) ---{RESET}")
    scripts = ["omega_nexus.py", "omega_lan_reaper.py", "server.py", "omega_sentinel.py"]
    for s in scripts:
        if test_module_syntax(s): score += 1
        total += 1

    # 3. KONTROLA SERVERU
    if test_server_live(): score += 5  # Server je důležitý, dáváme víc bodů
    total += 5

    # 4. KONTROLA DATABÁZE
    print(f"\n{YELLOW}--- 4. STAV PAMĚTI (Shadow Realm) ---{RESET}")
    shadow_path = os.path.join(BASE_DIR, "SHADOW_REALM")
    if os.path.exists(shadow_path):
        dbs = [f for f in os.listdir(shadow_path) if f.endswith(".db")]
        print(f"   [DB]   Nalezeno databází:         {GREEN}{len(dbs)}{RESET}")
        score += 1
    else:
        print(f"   [DB]   {RED}Složka SHADOW_REALM chybí!{RESET}")
    total += 1

    # VÝSLEDEK
    print(f"\n{CYAN}══════════════════════════════════════{RESET}")
    percentage = (score / total) * 100
    print(f"SKÓRE: {score}/{total} ({int(percentage)}%)")

    if percentage == 100:
        print(f"{GREEN}✅ SYSTÉM JE PLNĚ OPERAČNÍ.{RESET}")
        print("Všechny systémy (Scanner, Server, AI, Integrity) fungují.")
    elif percentage > 80:
        print(f"{YELLOW}⚠️ DROBNÉ ZÁVADY.{RESET} Zkontroluj chybějící soubory výše.")
    else:
        print(f"{RED}❌ KRITICKÉ SELHÁNÍ.{RESET} Systém potřebuje opravu.")

if __name__ == "__main__":
    run_exam()
