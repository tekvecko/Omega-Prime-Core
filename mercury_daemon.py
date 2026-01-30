import requests
import time
import os
import sys
from datetime import datetime

# IMPORT DYNAMICKÝCH PRAVIDEL
sys.path.append(os.path.expanduser("~/OmegaCore"))
from omega_policy import policy

LOG_FILE = os.path.expanduser("~/OmegaCore/price_history.csv")

def get_price(url):
    try:
        headers = {'User-Agent': 'OmegaPrime/Gen2'}
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()['bitcoin']['usd']
    except:
        return None

print("🦅 MERCURY: Připojeno k OMEGA CODEX.")

last_price = 0
error_count = 0

while True:
    # 1. DOTAZ NA MOZEK: Můžu běžet?
    can_run, reason = policy.can_run("mercury_agent")
    
    if not can_run:
        print(f"🛑 MERCURY PAUSED: {reason}")
        time.sleep(30) # Čekáme, dokud se nezmění pravidla
        continue

    # 2. NAČTENÍ KONFIGURACE Z JSONu
    target_url = policy.get_setting("mercury_agent", "target_url")
    interval = policy.get_setting("mercury_agent", "interval_seconds", 60)

    # 3. VYKONÁNÍ PRÁCE
    price = get_price(target_url)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if price:
        if price != last_price:
            with open(LOG_FILE, "a") as f:
                f.write(f"{now},PRICE,{price}\n")
            print(f"✅ [{now}] ${price}")
            last_price = price
    else:
        print(f"⚠️ [{now}] Chyba spojení")

    # Dynamický sleep podle pravidel
    time.sleep(interval)
