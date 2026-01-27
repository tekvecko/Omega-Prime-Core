import asyncio
import subprocess
import xml.etree.ElementTree as ET
import json
import os

# --- KONFIGURACE ---
HERMES_HOST = '127.0.0.1'
HERMES_PORT = 8888
SCAN_INTERVAL = 120 
MEMORY_DIR = "/data/data/com.termux/files/home/OMEGA_MEMORY"
MAP_FILE = os.path.join(MEMORY_DIR, "network_map.json")

# Seznam známých zařízení (v paměti běžícího procesu)
known_devices = set()
first_run = True

PORT_SIGNATURES = {
    "53": "Router / DNS", "80": "Web Server", "443": "Secure Web",
    "22": "SSH / Linux", "5555": "Android ADB", "8008": "Chromecast",
    "62078": "Apple Sync", "445": "Windows SMB", "9100": "Printer"
}

async def send_to_hermes(msg):
    try:
        reader, writer = await asyncio.open_connection(HERMES_HOST, HERMES_PORT)
        writer.write(f"MEMORIZE:{msg}".encode('utf-8'))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except:
        pass

def send_notification(title, content):
    """Odesle Android notifikaci pres Termux:API"""
    try:
        subprocess.run(["termux-notification", "--title", title, "--content", content], check=False)
    except Exception:
        pass

def get_local_subnet():
    try:
        output = subprocess.check_output("ifconfig | grep 'inet ' | grep -v '127.0.0.1'", shell=True).decode()
        ip = output.split()[1]
        # Pokud je IP z rozsahu 10.x.x.x (často mobilní data), varujeme
        if ip.startswith("10."):
            return None # Ignorujeme mobilní sítě pro bezpečnost
        subnet = ".".join(ip.split('.')[:3]) + ".0/24"
        return subnet
    except:
        return None

def scan_and_map(subnet):
    global first_run
    print(f"HUNTER: Skenuji sektor {subnet}...")
    try:
        ports = ",".join(PORT_SIGNATURES.keys())
        cmd = f"nmap -p {ports} --open -oX - {subnet}"
        xml_output = subprocess.check_output(cmd, shell=True).decode()
        
        root = ET.fromstring(xml_output)
        devices = []
        current_ips = set()
        
        for host in root.findall('host'):
            ip = host.find("address[@addrtype='ipv4']").get('addr')
            current_ips.add(ip)
            
            # Hostname
            hostname = "---"
            hostnames = host.find("hostnames")
            if hostnames is not None:
                hn = hostnames.find("hostname")
                if hn is not None:
                    hostname = hn.get('name')

            # Sluzby
            detected_services = []
            ports_elem = host.find("ports")
            if ports_elem is not None:
                for port in ports_elem.findall("port"):
                    pid = port.get("portid")
                    if pid in PORT_SIGNATURES:
                        detected_services.append(PORT_SIGNATURES[pid])
            
            identita = detected_services[0] if detected_services else "Neznámé zařízení"
            if "Apple" in str(detected_services): identita = "Apple Device"
            
            devices.append({"ip": ip, "vendor": str(detected_services), "hostname": hostname, "identita": identita})

            # --- DETEKCE NARUŠITELE ---
            if not first_run and ip not in known_devices:
                alert_msg = f"NOVÝ CÍL: {ip} ({identita})"
                print(f"ALARM: {alert_msg}")
                send_notification("OMEGA SECURITY ALERT", alert_msg)
                asyncio.create_task(send_to_hermes(f"SECURITY_BREACH: {alert_msg}"))

        # Aktualizace známých
        known_devices.update(current_ips)
        first_run = False

        # Uložení JSON
        os.makedirs(MEMORY_DIR, exist_ok=True)
        with open(MAP_FILE, 'w') as f:
            json.dump({"subnet": subnet, "devices": devices, "count": len(devices)}, f)
            
        return len(devices)
    except Exception as e:
        print(f"Chyba: {e}")
        return 0

async def hunter_loop():
    print("OMEGA HUNTER v5 (Silent Guardian) aktivován...")
    # Posleme testovaci notifikaci pri startu
    send_notification("OMEGA PRIME", "Obranné systémy aktivní.")
    
    while True:
        subnet = get_local_subnet()
        if subnet:
            count = scan_and_map(subnet)
            msg = f"RADAR: Sektor {subnet} zajištěn. Cílů: {count}"
            print(msg)
            await send_to_hermes(msg)
        else:
            print("HUNTER: Mobilní síť nebo offline. Radar pozastaven.")
            
        await asyncio.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    asyncio.run(hunter_loop())
