import hashlib
import os
import json
import time

# --- BARVY ---
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "integrity_db.json")

# Soubory, které hlídáme
WATCH_LIST = [
    "omega_nexus.py", "omega_focus.py", "omega_brain.py",
    "omega_vitality.py", "omega_sentinel.py", "interface.sh"
]

def calculate_hash(filepath):
    """Vypočítá SHA-256 hash souboru"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def check_integrity():
    print(f"   [SENTINEL] Kontrola integrity jádra...")
    
    # Načtení starého stavu
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            saved_hashes = json.load(f)
    else:
        saved_hashes = {}

    current_hashes = {}
    changes_detected = False

    for filename in WATCH_LIST:
        path = os.path.join(BASE_DIR, filename)
        current_hash = calculate_hash(path)
        
        if current_hash:
            current_hashes[filename] = current_hash
            
            # Porovnání
            if filename in saved_hashes:
                if saved_hashes[filename] != current_hash:
                    print(f"   {RED}⚠️ VAROVÁNÍ: Soubor {filename} byl změněn!{RESET}")
                    changes_detected = True
            else:
                print(f"   {YELLOW}ℹ️ Nový soubor pod ochranou: {filename}{RESET}")
                changes_detected = True
        else:
            print(f"   {RED}❌ CHYBA: Soubor {filename} zmizel!{RESET}")

    # Uložení nového stavu
    if changes_detected:
        with open(DB_FILE, "w") as f:
            json.dump(current_hashes, f, indent=4)
        print(f"   [SENTINEL] Databáze integrity aktualizována.")
    else:
        print(f"   [SENTINEL] {GREEN}System Integrity: 100%{RESET}")

if __name__ == "__main__":
    check_integrity()
