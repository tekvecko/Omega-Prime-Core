import socket, requests, sys

def scan_target():
    print("\033[1;36m--- OMEGA TARGET INSPECTOR ---\033[0m")
    
    # Změna: Pokud dostanu IP jako argument, použiju ji. Jinak se zeptám.
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]
        print(f"Cíl předán systémem: {target_ip}")
    else:
        target_ip = input("Zadej IP cíle: ").strip()
    
    print(f"\n\033[1;33m⚡ Zahajuji hloubkovou analýzu: {target_ip}...\033[0m")

    common_ports = [21, 22, 23, 53, 80, 443, 445, 3306, 8080, 8000, 8008, 8009]
    open_ports = []
    
    for port in common_ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            if s.connect_ex((target_ip, port)) == 0:
                open_ports.append(port)
                print(f"  [+] Otevřený port: \033[1;32m{port}\033[0m")
        except: pass
        s.close()

    if not open_ports: print("  [-] Žádné otevřené porty.")

    if 80 in open_ports or 8080 in open_ports or 443 in open_ports:
        print("\n\033[1;35m🌐 Web detekován. Analýza...\033[0m")
        try:
            url = f"http://{target_ip}"
            r = requests.get(url, timeout=2)
            print(f"  SERVER: {r.headers.get('Server', 'Unknown')}")
        except: print("  Chyba webu.")

    print("\n\033[1;36m✅ HOTOVO.\033[0m")

if __name__ == "__main__":
    scan_target()
