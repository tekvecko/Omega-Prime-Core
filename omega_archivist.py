import os
import glob
import shutil

# --- BARVY ---
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[0m"

# 1. DEFINICE JÁDRA (To, co používáme TEĎ v v8.4)
CORE_FILES = [
    "omega_nexus.py",      # Hlavní smyčka
    "omega_focus.py",      # Úkolníček
    "omega_brain.py",      # AI Analýza
    "omega_vitality.py",   # System check
    "omega_lan_reaper.py", # Sken sítě
    "omega_logger.py",     # Logy
    "omega_factory.py",    # Tvorba projektů
    "omega_chat.py",       # SMS Chat
    "omega_config.py",     # (Pokud existuje)
    "omega_test.py",       # Náš testovač
    "omega_archivist.py"   # Tento skript
]

def analyze_legacy():
    print(f"{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║    Ω  LEGACY CODE SCANNER v1.0       ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")
    
    all_omegas = glob.glob("omega_*.py")
    legacy_files = [f for f in all_omegas if f not in CORE_FILES]
    
    print(f"\n{YELLOW}🔍 Nalezeno {len(legacy_files)} souborů mimo aktuální jádro:{RESET}\n")

    for f in legacy_files:
        # Přečteme soubor a hledáme zajímavé věci
        features = []
        try:
            with open(f, "r", errors="ignore") as file:
                content = file.read()
                
                # Hledání klíčových slov (ztracené funkce)
                if "nmap" in content: features.append("NMAP")
                if "scapy" in content: features.append("SCAPY (Packet Hack)")
                if "flask" in content: features.append("FLASK (Web)")
                if "sqlite3" in content: features.append("SQLITE")
                if "pyaudio" in content: features.append("AUDIO")
                if "cv2" in content: features.append("KAMERA")
                if "os.system('rm" in content: features.append("DESTRUCTIVE")
                
        except:
            features = ["Nelze přečíst"]

        feat_str = f" -> Obsahuje: {', '.join(features)}" if features else ""
        print(f"   📄 {f:<25} {CYAN}{feat_str}{RESET}")

    print(f"\n{YELLOW}--- MOŽNOSTI ÚKLIDU ---{RESET}")
    print("Mám tyto soubory přesunout do složky 'ARCHIVE', aby byl systém čistý?")
    choice = input("Zadej 'yes' pro přesun, nebo Enter pro ponechání: ")

    if choice.lower() == "yes":
        if not os.path.exists("ARCHIVE"):
            os.makedirs("ARCHIVE")
        
        for f in legacy_files:
            try:
                shutil.move(f, os.path.join("ARCHIVE", f))
                print(f"   📦 Archivováno: {f}")
            except Exception as e:
                print(f"   ❌ Chyba u {f}: {e}")
        
        print(f"\n{GREEN}✅ Úklid dokončen. Jádro je nyní čisté.{RESET}")

if __name__ == "__main__":
    analyze_legacy()
