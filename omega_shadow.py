import subprocess
import os
import sys

# KONFIGURACE
SHADOW_DIR = "SHADOW_REALM"

def shadow_session():
    print(f"\n--- 🌑 SHADOW_MODE: ISOLATED SANDBOX ---")
    
    # 1. Vytvoření/Vstup do izolace
    if not os.path.exists(SHADOW_DIR):
        os.makedirs(SHADOW_DIR)
        print(f"   [+] Vytvářím izolovanou dimenzi: {SHADOW_DIR}")
    
    os.chdir(SHADOW_DIR)
    print(f"   🔒 KONTEXT UZAMČEN V: {os.getcwd()}")
    print("   ⚠️  VAROVÁNÍ: Zde neplatí žádné bezpečnostní pojistky.")
    print("   (Můžeš spouštět 'rm', mazat DB, testovat exploity.)")
    
    # 2. Generování dummy dat (aby bylo co ničit)
    if not os.path.exists("dummy_target.txt"):
        with open("dummy_target.txt", "w") as f: f.write("TOP SECRET DATA")
    
    # 3. Spuštění shellu v izolaci
    print("\n   Spouštím izolovaný shell (napiš 'exit' pro návrat)...")
    os.system("bash")
    
    print("\n--- SHADOW SESSION ENDED ---")

if __name__ == "__main__":
    shadow_session()
