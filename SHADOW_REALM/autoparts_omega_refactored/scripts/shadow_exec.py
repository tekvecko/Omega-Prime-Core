
import subprocess
import os

# --- KROK 2: Refactoring adresářové struktury ---
# ANALÝZA: Aktuální struktura je neorganizovaná. Soubory projektu, skripty,
# databáze a logy jsou smíchány v jednom adresáři.
# CÍL: Vytvořit čistou, standardizovanou adresářovou strukturu pro projekt
# a přesunout existující soubory na příslušná místa.

working_dir = "/data/data/com.termux/files/home/OmegaCore/SHADOW_REALM"
refactored_root = os.path.join(working_dir, "autoparts_omega_refactored")
dirs_to_create = {
    "src": "Pro hlavní zdrojový kód (Django projekt)",
    "scripts": "Pro pomocné a údržbové skripty",
    "data": "Pro databázové soubory",
    "logs": "Pro logovací soubory",
    "docs": "Pro dokumentaci",
    "config": "Pro konfigurační soubory"
}

# Mapa pro přesun souborů a adresářů
# formát: { 'cíl': ['zdroj1', 'zdroj2', ...], ... }
move_map = {
    os.path.join(refactored_root, "src"): [
        "autoparts_omega",
        "store",
        "manage.py"
    ],
    os.path.join(refactored_root, "scripts"): [
        "db_init.py",
        "omega_cortex.py",
        "omega_lan_reaper.py",
        "omega_vitality.py",
        "seed_db.py",
        "server.py",
        "shadow_exec.py"
    ],
    os.path.join(refactored_root, "data"): [
        "db.sqlite3",
        "doma.db",
        "logs.db",
        "omega.db",
        "prace_2026_01_27.db",
        "server.db"
    ],
    os.path.join(refactored_root, "logs"): [
        "server.log"
    ],
    os.path.join(refactored_root, "docs"): [
        "tajny_plan.txt"
    ]
}

def execute_command(command, cwd=None):
    """Pomocná funkce pro spouštění a logování systémových příkazů."""
    print(f"SPUŠTĚN PŘÍKAZ: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"CHYBA při provádění příkazu: {' '.join(command)}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        return False
    # print(f"VÝSTUP:\n{result.stdout}")
    return True

try:
    # 1. Vytvoření nové kořenové složky a podadresářů
    print("--- FÁZE 1: Vytváření nové adresářové struktury ---")
    if not os.path.exists(refactored_root):
        os.makedirs(refactored_root)
        print(f"Vytvořen adresář: {refactored_root}")
    
    for subdir, desc in dirs_to_create.items():
        path = os.path.join(refactored_root, subdir)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Vytvořen podadresář: {path} ({desc})")

    # 2. Přesun souborů a adresářů
    print("\n--- FÁZE 2: Přesun souborů a adresářů ---")
    all_moves_ok = True
    for dest_dir, items in move_map.items():
        for item in items:
            source_path = os.path.join(working_dir, item)
            if os.path.exists(source_path):
                if not execute_command(["mv", source_path, dest_dir], cwd=working_dir):
                    all_moves_ok = False
                    print(f"Selhal přesun: {source_path} -> {dest_dir}")
            else:
                print(f"VAROVÁNÍ: Zdroj '{source_path}' neexistuje, přeskočeno.")
    
    if not all_moves_ok:
        raise RuntimeError("Některé soubory se nepodařilo přesunout. Refactoring byl neúplný.")

    # 3. Vytvoření základních souborů pro správu projektu
    print("\n--- FÁZE 3: Vytvoření souborů pro správu projektu ---")
    
    # README.md
    readme_content = """# Projekt: autoparts_omega (Refactored)

    Tento projekt byl restrukturalizován pro lepší přehlednost a údržbu.

    ## Adresářová struktura

    - **/src**: Hlavní zdrojový kód (Django projekt).
    - **/scripts**: Pomocné a automatizační skripty.
    - **/data**: Databázové soubory.
    - **/logs**: Logy aplikace.
    - **/docs**: Dokumentace.
    - **/config**: Konfigurační soubory.
    - `requirements.txt`: Seznam Python závislostí.
    """
    with open(os.path.join(refactored_root, "README.md"), "w") as f:
        f.write(readme_content)
    print("Vytvořen soubor README.md")

    # requirements.txt
    with open(os.path.join(refactored_root, "requirements.txt"), "w") as f:
        f.write("# Zde uveďte závislosti projektu, např. django==4.2\n")
    print("Vytvořen soubor requirements.txt")

    print("\nANALÝZA VÝSTUPU: Struktura projektu byla úspěšně refaktorována.")
    print("PLÁN: Provedu kontrolní výpis nového a starého adresáře pro ověření změn.")
    
    # Kontrolní výpis
    print("\n--- KONTROLNÍ VÝPIS: Původní adresář (po úklidu) ---")
    execute_command(["ls", "-lA"], cwd=working_dir)

    print("\n--- KONTROLNÍ VÝPIS: Nový adresář projektu ---")
    execute_command(["ls", "-lA"], cwd=refactored_root)

    print("\n--- KONTROLNÍ VÝPIS: Obsah podadresáře 'src' ---")
    execute_command(["ls", "-lA"], cwd=os.path.join(refactored_root, "src"))


except Exception as e:
    print(f"\nKritická chyba v KROKU 2: {e}")

