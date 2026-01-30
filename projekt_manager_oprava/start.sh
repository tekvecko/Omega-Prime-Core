#!/bin/bash

# OMEGA: Vylepšený spouštěč projektů v2.0

C_GREEN="[0;32m"
C_BLUE="[0;34m"
C_RED="[0;31m"
C_NC="[0m"

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