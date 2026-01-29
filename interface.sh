#!/bin/bash
# OMEGA PRIME: HUB v8.9 (SHADOW NODE)

cd ~/OmegaCore || { echo "❌ CHYBA: Adresář ~/OmegaCore neexistuje!"; exit 1; }

# BARVY
RED='\033[1;31m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
PURPLE='\033[1;35m'
NC='\033[0m'

while true; do
    echo -e "\n${BLUE}══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}   Ω OMEGA PRIME [HUB v8.9] | SYSTEM: ONLINE${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════${NC}"
    
    echo -e "${GREEN}   [1] EXECUTE (Loop)   [2] FOCUS (Task)${NC}"
    echo -e "${YELLOW}   [3] DEV TOOLS        [4] SHADOW REALM${NC}"
    echo -e "${CYAN}   [P] PACKAGES (Mgmt)  [H] HISTORY (Prompts)${NC}"
    echo -e "${RED}   [S] STRESS TEST      [L] LOG & REPAIR${NC}"
    echo -e "${PURPLE}   [5] DASHBOARD        [C] SMS CHAT${NC}"
    echo -e "${BLUE}   [F] FACTORY (Create)${NC}"
    
    echo -e "${BLUE}──────────────────────────────────────────────${NC}"
    echo -e "   [6] KILL  [7] BACKUP  [8] EXIT"
    
    echo ""
    read -p "   OMEGA > " choice

    case $choice in
        1) python3 omega_nexus.py ;;
        2) export OMEGA_DB_PATH="omega.db"; python3 omega_focus.py ;;
        3) 
           echo -e "\n   ${YELLOW}--- DEV TOOLS ---${NC}"
           echo "   [a] Brain (Test AI)"
           echo "   [b] Hunter (Nmap Sken)"
           echo "   [c] Vitality (System Info)"
           echo "   [d] Sentinel (Integrity Check)"
           read -p "   DEV > " dc
           case $dc in
               a) python3 omega_brain.py ;;
               b) python3 omega_lan_reaper.py ;;
               c) python3 omega_vitality.py ;;
               d) python3 omega_sentinel.py ;;
           esac
           ;;
        4) 
           echo -e "\n   ${PURPLE}--- SHADOW REALM ---${NC}"
           echo "   [A] MANUAL SHELL (Isolated Bash)"
           echo "   [B] AUTONOMOUS NODE (AI Loop)"
           read -p "   SHADOW > " sc
           case $sc in
               [Aa]) python3 omega_shadow.py ;;
               [Bb]) python3 omega_shadow_node.py ;;
           esac
           ;;
        [Pp]) python3 omega_packages.py ;;
        [Hh]) python3 omega_prompts.py ;;
        [Ss]) python3 omega_stress_test.py ;;
        [Ll])
            echo -e "\n${RED}--- LOG MANAGEMENT ---${NC}"
            echo "   [A] Zobrazit log"
            echo "   [B] Kopírovat log"
            echo "   [C] AI OPRAVA"
            echo "   [D] Smazat log"
            read -p "   LOG > " lchoice
            case $lchoice in
                [Aa]) python3 omega_logger.py show ;;
                [Bb]) python3 omega_logger.py copy ;;
                [Cc]) python3 omega_logger.py repair ;;
                [Dd]) python3 omega_logger.py clear ;;
            esac
            ;;
        5)
            MY_IP=$(ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)
            [ -z "$MY_IP" ] && MY_IP="127.0.0.1"
            echo -e "   Startuji server na: http://$MY_IP:5000/dashboard"
            pkill -f server.py > /dev/null 2>&1
            nohup python3 server.py > /dev/null 2>&1 &
            termux-open-url "http://$MY_IP:5000/dashboard"
            ;;
        [Cc]) python3 omega_chat.py ;;
        [Ff]) python3 omega_factory.py ;;
        6) pkill -f python3; echo "   🚫 Procesy ukončeny." ;;
        7) git add .; git commit -m "Update v8.9 Autonomous"; git push ;;
        8) break ;;
        *) echo "   ⚠️ Neplatná volba." ;;
    esac
done
