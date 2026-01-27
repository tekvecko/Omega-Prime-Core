import hashlib
import os
import requests
import time

WATCH_FILE = "server.py"
API_URL = "http://127.0.0.1:5000/log"

def get_hash(filename):
    if not os.path.exists(filename): return "MISSING"
    with open(filename, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def patrol():
    print(f"--- WATCHDOG: Checking {WATCH_FILE} ---")
    current_hash = get_hash(WATCH_FILE)
    
    # Simulace: Zde by se porovnávalo s "Golden Hash", teď jen logujeme stav
    msg = f"WATCHDOG STATUS: {WATCH_FILE} signature is {current_hash}"
    print(msg)
    
    try:
        requests.post(API_URL, json={"message": msg}, timeout=2)
    except:
        print("WATCHDOG ERROR: Server neodpovídá!")

if __name__ == "__main__":
    patrol()
