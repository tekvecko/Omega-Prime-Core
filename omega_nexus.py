import subprocess
import time
import os
import socket
import sys
import glob

SHADOW_DIR = "SHADOW_REALM"
TIMEOUT_SEC = 10 

def select_environment():
    print("\n🌍 OMEGA: VÝBĚR PROSTŘEDÍ")
    dbs = glob.glob(f"{SHADOW_DIR}/*.db")
    db_list = [os.path.basename(d) for d in dbs]
    
    if not db_list: return "omega.db"
        
    for i, db in enumerate(db_list):
        print(f"   [{i+1}] {db}")
    print(f"   [{len(db_list)+1}] + NOVÝ SEKTOR")
    
    print(f"   (Auto-výběr poslední DB za {TIMEOUT_SEC}s...)")
    import select
    i, o, e = select.select([sys.stdin], [], [], TIMEOUT_SEC)

    if (i):
        choice = sys.stdin.readline().strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(db_list): return db_list[idx]
        elif len(choice) > 1: return choice if choice.endswith(".db") else choice + ".db"
    
    return db_list[0] if db_list else "omega.db"

def nexus_loop():
    active_db = select_environment()
    os.environ['OMEGA_DB_PATH'] = active_db
    
    print(f"--- NEXUS LEVEL 8 ONLINE ---")
    print(f"📍 DATABÁZE: {active_db}")
    
    if os.path.exists(SHADOW_DIR): os.chdir(SHADOW_DIR)
    
    # Start Dashboardu na pozadí
    subprocess.Popen("nohup python3 server.py > /dev/null 2>&1 &", shell=True)

    cycle = 0
    while True:
        cycle += 1
        print(f"\n🔄 [CYKLUS {cycle}] {time.strftime('%H:%M:%S')} | DB: {active_db}")

        # 1. SKENOVÁNÍ (OČI)
        print("   📡 Skenuji síť...")
        subprocess.run("python3 omega_lan_reaper.py", shell=True)
        
        # 2. ANALÝZA + NOTIFIKACE (MOZEK)
        print("   🧠 AI Analýza...")
        subprocess.run("python3 ../omega_brain.py", shell=True)
        
        # 3. VITALITA (TĚLO)
        subprocess.run("python3 omega_vitality.py", shell=True)

        print("   💤 Spánek 60s...")
        time.sleep(60)

if __name__ == "__main__":
    nexus_loop()
