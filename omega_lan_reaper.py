import subprocess, socket, concurrent.futures, time, os

# --- KONFIGURACE (SAFE MODE) ---
MAX_WORKERS = 10   # Sníženo ze 40 na 10 (Proti pádu Signal 9)
TIMEOUT = 1.0
DB_FILE = "omega_targets.db"

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(('8.8.8.8', 1)); ip = s.getsockname()[0]
    except: ip = '127.0.0.1'
    finally: s.close()
    return ip

def get_fingerprint(ip):
    # Jednoduchá detekce portů
    ports = {53:"ROUTER", 80:"WEB", 445:"PC/SMB", 8009:"CAST"}
    found = []
    for p, name in ports.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        if s.connect_ex((ip, p)) == 0: found.append(name)
        s.close()
    return ",".join(found) if found else "DEVICE"

def scan_host(ip):
    try:
        # Ping
        subprocess.check_call(["ping", "-c", "1", "-W", str(TIMEOUT), str(ip)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Identifikace
        ident = get_fingerprint(ip)
        
        # OKAMŽITÝ ZÁPIS DO SOUBORU (Append mode)
        # Aby se data neztratila při pádu
        with open(DB_FILE, "a") as f:
            f.write(f"{ip}|{ident}\n")
            
        return (ip, ident)
    except: return None

def main():
    my_ip = get_my_ip()
    base = ".".join(my_ip.split('.')[:3])
    
    # Vyčištění staré DB na začátku
    with open(DB_FILE, "w") as f: pass 
    
    print(f"\033[1;36m--- SAFE SCAN: {base}.0/24 ---\033[0m")
    print("Hledám cíle (buď trpělivý, jedu pomalu)...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(scan_host, f"{base}.{i}"): i for i in range(1, 255)}
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                print(f"\033[1;32m[+] {res[0]}\033[0m ({res[1]}) - ULOŽENO")

    print(f"\n\033[1;33m✅ HOTOVO. Cíle jsou v databázi.\033[0m")

if __name__ == "__main__": main()

