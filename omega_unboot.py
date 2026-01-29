import os

# --- CESTY ---
HOME_DIR = os.path.expanduser("~")
BASHRC_PATH = os.path.join(HOME_DIR, ".bashrc")

def disable_boot():
    print("\033[1;33m╔══════════════════════════════════════╗\033[0m")
    print("\033[1;33m║   Ω  OMEGA BOOT REMOVAL TOOL         ║\033[0m")
    print("\033[1;33m╚══════════════════════════════════════╝\033[0m")

    if not os.path.exists(BASHRC_PATH):
        print("❌ Soubor .bashrc neexistuje. Není co opravovat.")
        return

    # Načtení obsahu
    with open(BASHRC_PATH, "r") as f:
        lines = f.readlines()

    new_lines = []
    removed_count = 0
    inside_omega_block = False

    for line in lines:
        # Detekce začátku bloku
        if "# --- OMEGA PRIME BOOTLOADER" in line:
            inside_omega_block = True
            removed_count += 1
            continue
        
        # Detekce konce bloku (hledáme tu čáru)
        if inside_omega_block and "# -----------------------------------" in line:
            inside_omega_block = False
            removed_count += 1
            continue

        # Pokud jsme uvnitř bloku, řádek ignorujeme (mažeme)
        if inside_omega_block:
            removed_count += 1
        else:
            # Jinak ho zachováme
            new_lines.append(line)

    # Zápis zpět
    if removed_count > 0:
        with open(BASHRC_PATH, "w") as f:
            f.writelines(new_lines)
        print(f"✅ ÚSPĚCH: Odstraněno {removed_count} řádků Omega konfigurace.")
        print("   Termux nyní nastartuje do klasického příkazového řádku.")
    else:
        print("⚠️ Nebyl nalezen žádný aktivní Omega Bootloader.")

if __name__ == "__main__":
    disable_boot()
