import socket
import requests
import time

def scan_target():
    print("\033[1;36m--- OMEGA TARGET INSPECTOR ---\033[0m")
    target_ip = input("Zadej IP cíle (např. 192.168.0.1): ").strip()
    
    print(f"\n\033[1;33m⚡ Zahajuji hloubkovou analýzu: {target_ip}...\033[0m")

    # 1. ZKOUŠKA PORTŮ (Top 20)
    common_ports = [21, 22, 23, 53, 80, 443, 445, 3306, 8080, 8000, 5000, 8008, 8009]
    open_ports = []
    
    for port in common_ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((target_ip, port))
        if result == 0:
            open_ports.append(port)
            print(f"  [+] Otevřený port: \033[1;32m{port}\033[0m")
        s.close()

    if not open_ports:
        print("  [-] Žádné běžné porty nebyly nalezeny (Firewall?).")

    # 2. ZKOUŠKA WEBU (HTTP Headers)
    if 80 in open_ports or 8080 in open_ports or 443 in open_ports:
        print("\n\033[1;35m🌐 Detekována webová služba. Stahuji hlavičky...\033[0m")
        try:
            url = f"http://{target_ip}"
            r = requests.get(url, timeout=2)
            server = r.headers.get('Server', 'Unknown')
            title = "N/A"
            if "<title>" in r.text:
                title = r.text.split('<title>')[1].split('</title>')[0]
            
            print(f"  WEB SERVER: {server}")
            print(f"  STRÁNKA:    {title}")
        except Exception as e:
            print(f"  Chyba webu: {e}")

    print("\n\033[1;36m✅ ANALÝZA HOTOVA.\033[0m")

if __name__ == "__main__":
    scan_target()
