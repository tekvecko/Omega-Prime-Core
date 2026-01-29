#!/bin/bash
# Zabití starých sezení
pkill tmux 2>/dev/null
tmux kill-session -t nnab 2>/dev/null

echo -e "\033[1;33m[BOOT] Spouštím OMEGA NEXUS v2.1...\033[0m"
sleep 1

# Spuštění nového Python jádra přímo (bez tmuxu, pro čistotu, nebo v tmuxu)
# Pro Nexus je lepší běžet přímo v terminálu, protože je interaktivní.
python3 omega_nexus.py
