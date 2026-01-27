#!/bin/bash
# SENTINEL CHECK
if [ ! -f ~/nlb2026/sentinel.txt ]; then
    echo "❌ CRITICAL ERROR: Sentinel file missing in ~/nlb2026!";
    exit 1;
fi
# OMEGA PRIME: TRINITY INTERFACE v6.0

# --- BARVY ---
RED='\033[1;31m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
PURPLE='\033[1;35m'
NC='\033[0m'

show_header() {
    clear
    echo -e "${CYAN}"
    echo "  ╔════════════════════════════════════════╗"
    echo "  ║      Ω  OMEGA PRIME [HUB v6.0]         ║"
    echo "  ║      ARCHITECT: AUTHORIZED             ║"
    echo "  ╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

# --- HLAVNÍ SMYČKA ---
while true; do
    show_header
    
    # 1. EXECUTE_MODE (PRODUKCE)
    echo -e "${GREEN}   >>> [1] EXECUTE_MODE (Production) <<<${NC}"
    echo -e "       Spustí OMEGA NEXUS (Smyčka + AI + Notifikace)."
    echo -e "       Stabilní, bezpečný, autonomní provoz."

    # 2. DEV_MODE (VÝVOJ)
    echo -e "\n${YELLOW}   >>> [2] DEV_MODE (Diagnostics) <<<${NC}"
    echo -e "       Nástroje pro ladění jednotlivých modulů."
    echo -e "       (Test AI, Manuální Reaper, Senzory, Python Shell)"

    # 3. SHADOW_MODE (SANDBOX)
    echo -e "\n${PURPLE}   >>> [3] SHADOW_MODE (Unrestricted) <<<${NC}"
    echo -e "       Vstup do izolované složky SHADOW_REALM."
    echo -e "       Žádné bezpečnostní pojistky. Volná exekuce."

    # OVLÁDÁNÍ
    echo -e "\n${BLUE}   ────────────────────────────────────────${NC}"
    echo -e "   [4] 🌐 DASHBOARD (Web)    [5] 🛑 KILL ALL"
    echo -e "   [6] 💾 BACKUP (Git)       [7] 🚪 EXIT"
    
    echo ""
    read -p "   SELECT MODE > " choice

    case $choice in
        1)
            echo -e "\n   ${GREEN}>> INITIATING EXECUTE_MODE...${NC}"
            python3 omega_nexus.py
            read -p "   Stiskni Enter..."
            ;;
        2)
            # SUB-MENU PRO DEV_MODE
            echo -e "\n   ${YELLOW}--- DEV_MODE TOOLKIT ---${NC}"
            echo "   [a] 🧠 TEST BRAIN (Gemini Response)"
            echo "   [b] 🔫 MANUAL REAPER (One-shot Scan)"
            echo "   [c] ❤️ VITALITY CHECK (Battery/Disk)"
            echo "   [d] 🐍 PYTHON CONSOLE"
            read -p "   Select Tool > " dev_choice
            case $dev_choice in
                a) export OMEGA_DB_PATH="omega.db"; python3 omega_brain.py ;;
                b) cd SHADOW_REALM; python3 ../omega_lan_reaper.py; cd .. ;;
                c) cd SHADOW_REALM; python3 ../omega_vitality.py; cd .. ;;
                d) python3 ;;
                *) echo "   Zrušeno." ;;
            esac
            read -p "   Stiskni Enter..."
            ;;
        3)
            echo -e "\n   ${PURPLE}>> ENTERING SHADOW_MODE...${NC}"
            python3 omega_shadow.py
            read -p "   Stiskni Enter..."
            ;;
        4)
            IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | awk '{print $2}' | head -n 1)
            echo -e "\n   🔗 http://$IP:5000/dashboard"
            cd SHADOW_REALM
            nohup python3 ../server.py > /dev/null 2>&1 &
            cd ..
            termux-open-url "http://$IP:5000/dashboard"
            sleep 2
            ;;
        5)
            echo -e "\n   ${RED}>> SYSTEM HALT.${NC}"
            pkill -f python3
            sleep 1
            ;;
        6)
            git add .
            git commit -m "Interface v6 Update"
            git push
            read -p "   Backup Complete."
            ;;
        7)
            break
            ;;
        *)
            ;;
    esac
done
