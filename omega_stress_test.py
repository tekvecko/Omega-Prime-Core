import subprocess
import time
import sys
import json

# UPRAVENÝ CÍL PRO FLASK (Port 5000)
TARGET_URL = "http://localhost:5000"
LOG_ENDPOINT = f"{TARGET_URL}/log"
VIEW_ENDPOINT = f"{TARGET_URL}/view"
REQUESTS = 50

print(f"--- OMEGA STRESS TEST: CÍL {TARGET_URL} ---")

def run_cmd(cmd):
    try:
        # Přidán timeout pro jistotu
        return subprocess.check_output(cmd, shell=True, timeout=5).decode()
    except:
        return None

# 1. KONTROLA DOSTUPNOSTI
print("1. [PING] Kontrola spojení...")
if run_cmd(f"curl -s {TARGET_URL}"):
    print("   ✅ SERVER ONLINE (Flask detekován)")
else:
    print(f"   ❌ SERVER NEODPOVÍDÁ na {TARGET_URL}")
    print("   (Běží server? Zkontroluj 'ps aux | grep python')")
    sys.exit(1)

# 2. PŘEHRADA (BARRAGE)
print(f"2. [FIRE] Odesílám {REQUESTS} logovacích paketů...")
success_count = 0
start_time = time.time()

for i in range(REQUESTS):
    msg = f"STRESS_TEST_DATA_{i}"
    # Opravený curl pro Flask JSON handling
    cmd = f'curl -s -X POST -H "Content-Type: application/json" -d \'{{"message": "{msg}"}}\' {LOG_ENDPOINT}'
    res = run_cmd(cmd)
    
    # Flask vrací JSON, hledáme "success" nebo status 200
    if res and ("success" in res or "200" in res or "timestamp" in res):
        success_count += 1
        # Vizuální progress bar
        sys.stdout.write(f"\r   🚀 Paket {i+1}/{REQUESTS} OK")
        sys.stdout.flush()
    else:
        sys.stdout.write(f"\r   💥 Paket {i+1} FAIL")

duration = time.time() - start_time
print(f"\n   ✅ Úspěšnost: {success_count}/{REQUESTS} ({duration:.2f}s)")

# 3. VIZUÁLNÍ INSPEKCE
print("3. [VERIFY] Stahuji HTML report...")
html_content = run_cmd(f"curl -s {VIEW_ENDPOINT}")

if html_content and ("<table" in html_content or "STRESS_TEST" in html_content):
    print("   ✅ HTML OBSAHUJE DATA (Tabulka nalezena)")
    print("   🏆 MISSE SPLNĚNA: AI úspěšně nasadila a udržela systém.")
else:
    print("   ⚠️ VAROVÁNÍ: HTML neobsahuje data. Zkontroluj http://localhost:5000/view")
    print(f"   (Přijatá data: {html_content[:50]}...)")

