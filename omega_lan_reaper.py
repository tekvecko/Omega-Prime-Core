import subprocess
import socket
import concurrent.futures
import time

# --- KONFIGURACE ---
MAX_WORKERS = 40   # Vlákna pro Ping
TIMEOUT = 0.8      # Ping timeout
PORT_TIMEOUT = 0.5 # Port scan timeout (musí být rychlý)

# PORTY PRO IDENTIFIKACI
INTERESTING_PORTS = {
    53: "Router/DNS",
    80: "Web Server",
    443: "Secure Web",
    22: "SSH/Linux",
    23: "Telnet/IoT",
    445: "Windows/SMB",
    8008: "Chromecast",
    8009: "Google Cast",
    5000: "UPnP/Synology",
    62078: "iOS Device"
}

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(('8.8.8.8', 1)); ip = s.getsockname()[0]
    except: ip = '127.0.0.1'
    finally: s.close()
    return ip

def check_port(ip, port):
    """Zkusí se připojit na port"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(PORT_TIMEOUT)
    try:
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except:
        return False

def get_fingerprint(ip):
    """Proklepne otevřené porty a odhadne zařízení"""
    open_ports = []
    # Rychlý scan klíčových portů
    for port in INTERESTING_PORTS:
        if check_port(ip, port):
            open_ports.append(port)
    
    # Analýza
    if 53 in open_ports: return "📡 ROUTER / GATEWAY"
    if 8009 in open_ports or 8008 in open_ports: return "📺 CHROMECAST / GOOGLE HOME"
    if 445 in open_ports: return "💻 WINDOWS PC / NAS"
    if 62078 in open_ports: return "📱 APPLE IPHONE/IPAD"
    if 22 in open_ports: return "🐧 LINUX SERVER"
    if 80 in open_ports or 443 in open_ports: return "🌐 WEB DEVICE (Cam/Printer)"
    
    if open_ports: return f"UNKNOWN (Ports: {open_ports})"
    return "❓ UNKNOWN DEVICE"

def scan_host(ip):
    """Ping + Fingerprint"""
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "-W", str(TIMEOUT), str(ip)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # Pokud žije, zjistíme co to je
        identity = get_fingerprint(ip)
        return (ip, identity)
    except:
        return None

def main():
    my_ip = get_my_ip()
    base = ".".join(my_ip.split('.')[:3])
    subnet = f"{base}.0/24"
    
    print(f"\033[1;36m--- HUNTER v6.0: FINGERPRINT SCAN ---\033[0m")
    print(f"📍 MOJE IP: {my_ip}")
    print(f"🔎 CÍL: {subnet}")
    print("---------------------------------------")

    found = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(scan_host, f"{base}.{i}"): i for i in range(1, 255)}
        
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                ip, ident = res
                print(f"\033[1;32m[+] {ip.ljust(15)}\033[0m -> {ident}")
                found.append(res)

    print("\n\033[1;33m--- FINÁLNÍ REPORT ---\033[0m")
    found.sort(key=lambda x: int(x[0].split('.')[-1]))
    for ip, ident in found:
        # Zvýraznění routeru
        color = "\033[1;35m" if "ROUTER" in ident else "\033[0m"
        print(f"{color}💀 {ip.ljust(15)} {ident}\033[0m")
    print("---------------------------------------")

if __name__ == "__main__":
    main()
