import shutil
import psutil
import os
import time
import requests

# KONFIGURACE
SERVER_URL = "http://127.0.0.1:5000/log"

def get_disk_usage():
    total, used, free = shutil.disk_usage("/")
    percent = (used / total) * 100
    return f"{percent:.1f}%"

def get_battery_status():
    # Pokus o čtení z Android filesystému (nevyžaduje termux-api balíček, pokud je přístupný)
    try:
        with open("/sys/class/power_supply/battery/capacity", "r") as f:
            cap = f.read().strip()
        with open("/sys/class/power_supply/battery/status", "r") as f:
            stat = f.read().strip()
        return f"{cap}% ({stat})"
    except:
        return "UNKNOWN (Sensor blocked)"

def get_memory():
    # Používá standardní knihovnu nebo čte /proc/meminfo
    try:
        mem = psutil.virtual_memory()
        return f"{mem.percent}% used"
    except:
        return "N/A"

def check_vitals():
    disk = get_disk_usage()
    batt = get_battery_status()
    
    msg = f"VITALITY REPORT: Battery: {batt} | Disk: {disk}"
    print(f"--- {msg} ---")
    
    # Kritické varování (pokud baterie pod 20%)
    if "UNKNOWN" not in batt and int(batt.split('%')[0]) < 20:
        print("⚠️ CRITICAL POWER LEVEL!")
        msg = "🚨 LOW BATTERY WARNING: " + msg

    try:
        requests.post(SERVER_URL, json={"message": msg}, timeout=2)
    except:
        pass

if __name__ == "__main__":
    # Pokud nemáš psutil, doinstaluje se za běhu (nebo selže tiše)
    try:
        import psutil
    except ImportError:
        print("Instaluji psutil pro telemetrii...")
        os.system("pip install psutil")
        import psutil
        
    check_vitals()
