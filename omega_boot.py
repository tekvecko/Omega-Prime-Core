import os
import shutil

# --- CESTY ---
HOME_DIR = os.path.expanduser("~")
BASHRC_PATH = os.path.join(HOME_DIR, ".bashrc")
BACKUP_PATH = os.path.join(HOME_DIR, ".bashrc.old_omega")

# --- NOVÝ OBSAH .BASHRC ---
# Tento kód zajistí start Menu, ale nechá ti možnost úniku
BOOT_BLOCK = """
# --- OMEGA PRIME BOOTLOADER v8.6 ---
# Pokud existuje jádro, jdi tam a spusť HUB
if [ -d "$HOME/OmegaCore" ]; then
    cd "$HOME/OmegaCore"
    
    # Vyčisti obrazovku pro 'cool' efekt
    clear
    
    # Spusť hlavní nabídku (Interface)
    # Použití 'exec' nahradí shell menu - šetří paměť
    # ./interface.sh
    bash interface.sh
fi
# -----------------------------------
"""

def setup_boot():
    print("\033[1;36m╔══════════════════════════════════════╗\033[0m")
    print("\033[1;36m║   Ω  OMEGA BOOT CONFIGURATOR         ║\033[0m")
    print("\033[1;36m╚══════════════════════════════════════╝\033[0m")

    # 1. Záloha
    if os.path.exists(BASHRC_PATH):
        shutil.copy(BASHRC_PATH, BACKUP_PATH)
        print(f"   [BACKUP] Starý config uložen do: .bashrc.old_omega")
    
    # 2. Načtení starého obsahu (chceme zachovat systémové věci, ale smazat staré Omega věci)
    original_lines = []
    if os.path.exists(BASHRC_PATH):
        with open(BASHRC_PATH, "r") as f:
            original_lines = f.readlines()
    
    # 3. Filtrace (Odstraníme staré zmínky o Omeze nebo Strongholdu)
    clean_lines = []
    for line in original_lines:
        if "Omega" not in line and "STRONGHOLD" not in line and "interface.sh" not in line:
            clean_lines.append(line)
    
    # 4. Zápis nového configu
    with open(BASHRC_PATH, "w") as f:
        f.writelines(clean_lines)
        f.write("\n" + BOOT_BLOCK)
    
    print(f"   [WRITE]  Bootloader zapsán úspěšně.")
    print(f"\n\033[1;32m✅ HOTOVO. Při příštím startu Termuxu naskočí rovnou MENU.\033[0m")
    print("   (Pro návrat do příkazové řádky stačí v menu zvolit [8] EXIT)")

if __name__ == "__main__":
    setup_boot()
