import asyncio
import subprocess
import json
import os

# --- KONFIGURACE ---
HERMES_HOST = '127.0.0.1'
HERMES_PORT = 8888
CHECK_INTERVAL = 60  # Interval kontroly v sekundách

async def send_to_hermes(msg):
    """Odeslání zprávy do paměti přes server Hermes."""
    try:
        reader, writer = await asyncio.open_connection(HERMES_HOST, HERMES_PORT)
        writer.write(f"MEMORIZE:{msg}".encode('utf-8'))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass # Pokud server nejede, mlčíme

def get_net_bytes():
    """Přečte celkový počet přijatých + odeslaných bytů ze všech rozhraní."""
    try:
        total = 0
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()
        for line in lines[2:]: # Přeskočíme hlavičky
            parts = line.split()
            if len(parts) > 9:
                # parts[1] = RX bytes, parts[9] = TX bytes
                total += int(parts[1]) + int(parts[9])
        return total
    except:
        return 0

async def loop():
    print("OMEGA SENTINEL v2 (NetWatch) aktivován...")
    
    # Inicializace čítačů
    last_net = get_net_bytes()
    
    while True:
        try:
            # 1. Získání dat
            curr_net = get_net_bytes()
            
            # Výpočet rozdílu (Data za poslední interval)
            diff_bytes = curr_net - last_net
            diff_mb = diff_bytes / (1024 * 1024)
            last_net = curr_net

            # 2. Hardware data (Baterie & CPU)
            bat_raw = subprocess.check_output(['termux-battery-status'], stderr=subprocess.DEVNULL)
            bat = json.loads(bat_raw)
            temp = bat.get('temperature', 0)
            perc = bat.get('percentage', 0)
            proc = int(subprocess.check_output('ps aux | wc -l', shell=True).strip())

            # 3. Logika rozhodování (AI Trigger)
            # Pokud proteklo více než 10 MB za minutu -> VAROVÁNÍ
            if diff_mb > 10:
                await send_to_hermes(f"NET_ALERT: Vysoký přenos dat! ({diff_mb:.2f} MB za {CHECK_INTERVAL}s)")
            
            # Pokud se změnila teplota nebo je baterie nízko -> STATUS
            # (Pro tento test posíláme status vždy, abys viděl i data sítě)
            status_msg = f"STATUS: Bat {perc}%, Teplota {temp}C, Procesy {proc}, Síť +{diff_mb:.2f}MB"
            await send_to_hermes(status_msg)
                
        except Exception as e:
            # Tichá chyba, aby sentinel nepadal
            pass
        
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(loop())
