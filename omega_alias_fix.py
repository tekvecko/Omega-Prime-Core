import os

# Cesta k nastavení shellu
BASHRC_PATH = os.path.expanduser("~/.bashrc")

# Co chceme přidat (Alias)
ALIAS_LINE = "alias gonexus='cd ~/OmegaCore && bash interface.sh'"

def fix_bashrc():
    print("\033[1;36m🔧 OMEGA CONFIG FIXER\033[0m")
    
    if not os.path.exists(BASHRC_PATH):
        # Vytvoříme nový, pokud neexistuje
        with open(BASHRC_PATH, "w") as f:
            f.write(ALIAS_LINE + "\n")
        print("✅ Vytvořen nový .bashrc s aliasem.")
        return

    # Načteme existující řádky
    with open(BASHRC_PATH, "r") as f:
        lines = f.readlines()

    new_lines = []
    has_alias = False
    cleaned_warnings = 0

    for line in lines:
        # 1. Odstraníme staré červené varování STRONGHOLD
        if "STRONGHOLD" in line or "MONITORING ENABLED" in line:
            cleaned_warnings += 1
            continue # Přeskočit (smazat)
            
        # 2. Zkontrolujeme, jestli už tam alias není
        if "alias gonexus=" in line:
            has_alias = True
        
        new_lines.append(line)

    # 3. Pokud alias chybí, přidáme ho na konec
    if not has_alias:
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n") # Odřádkování
        new_lines.append(ALIAS_LINE + "\n")
        print("✅ Přidán příkaz 'gonexus'.")
    else:
        print("ℹ️ Příkaz 'gonexus' již existuje.")

    # Zápis zpět
    with open(BASHRC_PATH, "w") as f:
        f.writelines(new_lines)

    if cleaned_warnings > 0:
        print(f"✅ Odstraněno {cleaned_warnings} řádků starých varování (Stronghold).")

    print("\n\033[1;33m⚠️ DŮLEŽITÉ: Aby to fungovalo hned, zadej tento příkaz:\033[0m")
    print("source ~/.bashrc")

if __name__ == "__main__":
    fix_bashrc()
