import subprocess
import socket
import threading
import requests
import time
import re

# KONFIGURACE
SERVER_URL = "http://127.0.0.1:5000/log"
MY_IP_PREFIX = "" 
ALIVE_HOSTS = []

def get_local_ip():
    # Získá lokální IP (např. 192.168.1.15)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Nemusí se nikam připojit, jen zjistí routování
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def ping_host(ip):
    # Pingne IP adresu (Termux friendly)
    try:
        # -c 1 (jeden paket), -W 1 (timeout 1s)
        output = subprocess.check_output(f"ping -c 1 -W 1 {ip}", shell=True, stderr=subprocess.DEVNULL)
        print(f"   [+] NALEZEN CÍL: {ip}")
        try:
            # Pokus o získání jména (hostname)
            hostname = socket.gethostbyaddr(ip)[0]
            ALIVE_HOSTS.append(f"{ip} ({hostname})")
        except:
            ALIVE_HOSTS.append(ip)
    except:
        pass # Mrtvý cíl ignorujeme

def reap_network():
    my_ip = get_local_ip()
    if my_ip == "127.0.0.1":
        print("❌ CHYBA: Nejsem připojen k Wi-Fi.")
        return

    # Získáme prefix (např. "192.168.1")
    prefix = ".".join(my_ip.split(".")[:-1])
    print(f"--- LAN REAPER: Skenuji síť {prefix}.0/24 ---")
    print(f"   (Moje IP: {my_ip})")

    threads = []
    # Rozjezd 254 vláken pro rychlost
    for i in range(1, 255):
        ip = f"{prefix}.{i}"
        if ip == my_ip: continue # Neskenejeme sami sebe
        t = threading.Thread(target=ping_host, args=(ip,))
        t.start()
        threads.append(t)
    
    # Čekání na dokončení všech
    for t in threads:
        t.join()

    # Reportování výsledků
    if ALIVE_HOSTS:
        msg = f"LAN REAPER REPORT: Nalezeno {len(ALIVE_HOSTS)} zařízení: {ALIVE_HOSTS}"
    else:
        msg = "LAN REAPER REPORT: Žádná další zařízení nenalezena (Jsem sám)."
    
    print(f"\n📊 {msg}")
    
    try:
        requests.post(SERVER_URL, json={"message": msg}, timeout=2)
        print("✅ Odesláno na server.")
    except:
        print("⚠️ Server neodpovídá.")

if __name__ == "__main__":
    reap_network()
