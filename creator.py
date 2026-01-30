import os
import stat

# --- DEFINICE PROJEKTU ---
PROJECT_DIR = "projekt_manager_oprava"

# Obsah souboru main.py
MAIN_PY_CONTENT = """
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_omega():
    return '<h1>OMEGA: Projekt běží!</h1>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"""

# Obsah souboru requirements.txt
REQUIREMENTS_TXT_CONTENT = """
Flask
"""

# Obsah VYLEPŠENÉHO souboru start.sh
START_SH_CONTENT = """#!/bin/bash

# OMEGA: Vylepšený spouštěč projektů v2.0

C_GREEN="\033[0;32m"
C_BLUE="\033[0;34m"
C_RED="\033[0;31m"
C_NC="\033[0m"

echo -e "${C_BLUE}OMEGA | Startuji projektový manažer...${C_NC}"

if [ -f "requirements.txt" ]; then
    echo -e "${C_GREEN}OMEGA | Detekován Python projekt (requirements.txt).${C_NC}"
    echo "OMEGA | Kontroluji závislosti..."
    pip install --disable-pip-version-check -q -r requirements.txt
    echo -e "${C_GREEN}OMEGA | Závislosti jsou aktuální.${C_NC}"

    if [ -f "main.py" ]; then
        echo -e "${C_BLUE}OMEGA | Spouštím 'python main.py'...${C_NC}"
        python main.py
    else
        echo -e "${C_RED}OMEGA | CHYBA: Soubor 'main.py' nebyl nalezen!${C_NC}"
        exit 1
    fi
else
    echo -e "${C_RED}OMEGA | CHYBA: Nepodařilo se identifikovat typ projektu (chybí requirements.txt).${C_NC}"
    exit 1
fi
"""

try:
    print("OMEGA | Vytvářím adresář projektu...")
    os.makedirs(PROJECT_DIR, exist_ok=True)
    
    files_to_create = {
        "main.py": MAIN_PY_CONTENT,
        "requirements.txt": REQUIREMENTS_TXT_CONTENT,
        "start.sh": START_SH_CONTENT
    }
    
    for filename, content in files_to_create.items():
        path = os.path.join(PROJECT_DIR, filename)
        print(f"OMEGA | Vytvářím soubor: {path}")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        if filename == "start.sh":
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)
            print("OMEGA | Nastavuji práva pro spuštění 'start.sh'...")

    print("\nOMEGA | OPERACE DOKONČENA. Projekt byl úspěšně vytvořen.")

except Exception as e:
    print(f"\nOMEGA | KRIZOVÁ CHYBA: {e}")
