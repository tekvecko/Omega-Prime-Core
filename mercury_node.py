import requests
import time
import os
from datetime import datetime

# Cíl: API pro cenu Bitcoinu (nebo HTML stránka e-shopu)
URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
LOG_FILE = os.path.expanduser("~/OmegaCore/price_log.csv")

def get_btc_price():
    try:
        r = requests.get(URL, timeout=5)
        data = r.json()
        return data['bitcoin']['usd']
    except:
        return None

print("🦅 MERCURY AGENT: Sleduji trh (BTC/USD)...")
print("   (Ukonči pomocí CTRL+C)")

last_price = 0

while True:
    price = get_btc_price()
    now = datetime.now().strftime("%H:%M:%S")
    
    if price:
        # Změna ceny
        diff = price - last_price
        icon = "➖"
        if last_price != 0:
            icon = "📈" if diff > 0 else "📉"
        
        # Výpis
        print(f"[{now}] {icon} Cena: ${price} (Změna: ${diff:.2f})")
        
        # Uložení do souboru (Excel format)
        with open(LOG_FILE, "a") as f:
            f.write(f"{now},{price}\n")
            
        last_price = price
    else:
        print(f"[{now}] ❌ Chyba spojení...")
    
    time.sleep(10) # Kontrola každých 10 sekund
