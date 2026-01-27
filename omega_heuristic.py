#!/usr/bin/env python3
import os
import sys
import json
import platform
import subprocess

# --- OMEGA HEURISTICS ENGINE v1.0 ---
# Účel: Automatická detekce prostředí a příprava kontextu pro LLM (Option 3)

def check_connectivity():
    """Rychlý ping na Google DNS pro ověření sítě."""
    try:
        subprocess.check_call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def analyze_environment():
    """
    Provádí hloubkovou inspekci prostředí.
    Rozlišuje: Termux (Android) vs Standard Linux.
    """
    heuristics = {
        "os_type": platform.system(),
        "architecture": platform.machine(),
        "is_termux": False,
        "python_ver": sys.version.split()[0],
        "workspace": os.getcwd(),
        "connectivity": check_connectivity()
    }

    # Specifická detekce pro Termux (podle cest a proměnných)
    prefix = os.environ.get("PREFIX", "")
    if "com.termux" in prefix or os.path.exists("/data/data/com.termux"):
        heuristics["is_termux"] = True
        heuristics["package_manager"] = "pkg"
    else:
        heuristics["is_termux"] = False
        heuristics["package_manager"] = "apt/yum"

    return heuristics

def save_state(data):
    """Ukládá stav do JSON pro 'memory persistence' mezi dotazy."""
    filename = "omega_env_state.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[+] Heuristics Saved: {filename}")
    except Exception as e:
        print(f"[!] Write Error: {e}")

if __name__ == "__main__":
    print("[*] Spouštím Omega Heuristiku...")
    
    data = analyze_environment()
    
    # Výpis pro uživatele
    env_label = "TERMUX (Android)" if data["is_termux"] else "STANDARD LINUX"
    print(f"[+] Detekováno prostředí: {env_label}")
    print(f"[+] Architektura: {data['architecture']}")
    print(f"[+] Konektivita: {'ONLINE' if data['connectivity'] else 'OFFLINE'}")
    
    save_state(data)

