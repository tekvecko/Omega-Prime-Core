#!/bin/bash
echo "--- OMEGA PRIME: INITIALIZATION ---"

echo "[1/3] Aktualizace balíčků..."
pkg update -y && pkg upgrade -y

echo "[2/3] Instalace závislostí (Python, Nmap, Git)..."
pkg install python python-pip nmap git termux-api -y

echo "[3/3] Instalace Python knihoven..."
pip install flask requests psutil google-generativeai

echo "--- SETUP COMPLETE ---"
echo "Nyní vytvoř soubor api_key.txt a spusť 'gonexus'."
