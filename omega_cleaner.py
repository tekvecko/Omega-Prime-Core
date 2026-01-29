import os
import glob
import time

# --- BARVY ---
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"

# 1. NEXUS JÁDRO (To, co běží teď)
CORE_SYSTEM = [
    "omega_nexus.py", "omega_focus.py", "omega_brain.py",
    "omega_vitality.py", "omega_lan_reaper.py", "omega_logger.py",
    "omega_factory.py", "omega_chat.py", "omega_config.py",
    "omega_test.py", "omega_cleaner.py", "api_key.txt", "config.json",
    "interface.sh"
]

# 2. TVŮJ SEZNAM K ZACHOVÁNÍ (Legacy Keep)
USER_KEEP = [
    "omega_ai_healer.py",
    "omega_core.py",
    "omega_cortex.py",
    "omega_dashboard.py",
    "omega_evolution.py",
    "omega_executor.py",
    "omega_healer.py",
    "omega_heuristic.py",
    "omega_hunter.py",
    "omega_hybrid_healer.py",
    "omega_loader.py",
    "omega_overlord_v5.py",
    "omega_sentinel.py",
    "omega_server.py",
    "omega_shadow.py",
    "omega_shadow_build.py",
    "omega_shadow_evolve_v3.py",
    "omega_solver.py",
    "omega_stress_test.py",
    "omega_watchdog.py",
    "omega_archivist.py"
]

def clean_system():
    print(f"{RED}╔══════════════════════════════════════╗{RESET}")
    print(f"{RED}║   Ω  CUSTOM PURGE (SMART CLEAN)      ║{RESET}")
    print(f"{RED}╚══════════════════════════════════════╝{RESET}")
    
    # Sloučení whitelistů
    WHITELIST = set(CORE_SYSTEM + USER_KEEP)

    # Najdeme všechny omega soubory
    all_files = glob.glob("omega_*.py")
    
    # K smazání je jen to, co NENÍ ve whitelistu
    to_delete = [f for f in all_files if f not in WHITELIST]
    to_delete.sort()
    
    if not to_delete:
        print(f"\n{GREEN}✅ Systém je čistý. Všechny soubory jsou na whitelistu.{RESET}")
        return

    print(f"\n{YELLOW}⚠️ NALEZENO {len(to_delete)} SOUBORŮ K ODSTRANĚNÍ (Balast):{RESET}")
    for f in to_delete:
        print(f"   ❌ {f}")

    print(f"\n{GREEN}ℹ️  ZACHOVÁNO BUDE {len(WHITELIST)} SOUBORŮ (včetně Overlord v5).{RESET}")
    print(f"{RED}VAROVÁNÍ: Smazané soubory nelze obnovit!{RESET}")
    
    confirm = input("Napiš 'delete' pro potvrzení smazání: ")

    if confirm.strip().lower() == "delete":
        print(f"\n{YELLOW}⚡ Mazání zahájeno...{RESET}")
        count = 0
        for f in to_delete:
            try:
                os.remove(f)
                print(f"   🗑️ Smazáno: {f}")
                count += 1
            except Exception as e:
                print(f"   ⚠️ Chyba {f}: {e}")
        
        print(f"\n{GREEN}✨ HOTOVO. Smazáno {count} zbytečných verzí.{RESET}")
    else:
        print(f"\n{GREEN}Akce zrušena.{RESET}")

if __name__ == "__main__":
    clean_system()
