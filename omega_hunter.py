import socket
import requests
import json
import time

TARGET_IP = "127.0.0.1"
PORTS = [21, 22, 80, 8080, 5000, 9000]
API_URL = "http://127.0.0.1:5000/log"

def scan():
    results = []
    print(f"--- HUNTER: Scanning {TARGET_IP} ---")
    for port in PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((TARGET_IP, port))
        if result == 0:
            results.append(port)
        sock.close()
    
    msg = f"HUNTER REPORT: Open ports on {TARGET_IP}: {results}"
    print(msg)
    
    # Odeslání na server
    try:
        requests.post(API_URL, json={"message": msg}, timeout=2)
    except:
        print("HUNTER ERROR: Server neodpovídá!")

if __name__ == "__main__":
    scan()
