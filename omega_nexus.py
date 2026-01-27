#!/usr/bin/env python3
import os
import sys
import json
import shutil
import time
import subprocess
import datetime
from urllib.request import Request, urlopen

# --- OMEGA NEXUS CONFIG ---
VERSION = "1.0.1 (Termux Edition)"
STATE_FILE = "omega_env_state.json"
REPORT_FILE = "nexus_status.html"
API_KEY = os.environ.get("GEMINI_API_KEY")

# Barevné výstupy pro terminál
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def load_heuristics():
    """Načte data o prostředí z předchozího kroku."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"is_termux": True, "note": "Heuristics data missing"}

def get_telemetry():
    """Získá aktuální stav systému (Disk, Load, Net)."""
    telemetry = {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    # 1. Disk Usage
    total, used, free = shutil.disk_usage(".")
    telemetry["disk_free_gb"] = round(free / (1024**3), 2)
    telemetry["disk_percent"] = round((used / total) * 100, 1)
    
    # 2. System Load (pokud je dostupné)
    try:
        load = os.getloadavg()
        telemetry["cpu_load"] = load[0] # 1 min avg
    except:
        telemetry["cpu_load"] = 0.0

    # 3. Network Latency (Ping)
    try:
        # -c 1 = jeden paket, -W 1 = timeout 1s
        subprocess.check_output(["ping", "-c", "1", "-W", "1", "8.8.8.8"])
        telemetry["net_status"] = "ONLINE"
        telemetry["net_latency"] = "OK (<100ms)"
    except:
        telemetry["net_status"] = "OFFLINE"
        telemetry["net_latency"] = "TIMEOUT"

    return telemetry

def consult_gemini(issue_description):
    """Pokud je problém, zeptá se Gemini na řešení."""
    if not API_KEY:
        return "AI ADVICE UNAVAILABLE: No API Key found."

    print(f"{YELLOW}⚠️  Detekována anomálie: {issue_description}{RESET}")
    print(f"{YELLOW}🤖 Kontaktuji Gemini pro řešení...{RESET}")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"Jsem v Termuxu (Android). Mám tento problém: {issue_description}. Navrhni JEDEN konkrétní terminálový příkaz k vyřešení nebo diagnostice. Buď stručný."
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        req = Request(url, data=json.dumps(data).encode(), headers=headers)
        with urlopen(req) as response:
            result = json.loads(response.read())
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"AI Error: {str(e)}"

def generate_html_report(env, tele, advice):
    """Vygeneruje Cyberpunk HTML Dashboard."""
    
    color_status = "green" if tele["net_status"] == "ONLINE" else "red"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OMEGA NEXUS STATUS</title>
        <style>
            body {{ background-color: #0d0d0d; color: #00ff41; font-family: monospace; padding: 20px; }}
            h1 {{ border-bottom: 2px solid #00ff41; padding-bottom: 10px; }}
            .card {{ border: 1px solid #333; padding: 15px; margin-bottom: 15px; background: #111; }}
            .alert {{ color: #ff3333; border: 1px solid #ff3333; padding: 10px; }}
            .metric {{ font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <h1>OMEGA NEXUS <span style="font-size:0.5em">{VERSION}</span></h1>
        
        <div class="card">
            <h3>ENVIRONMENT</h3>
            User: {os.environ.get('USER', 'unknown')}<br>
            System: {"Termux" if env.get("is_termux") else "Standard Linux"}<br>
            Path: {os.getcwd()}
        </div>

        <div class="card">
            <h3>TELEMETRY</h3>
            <div class="metric">DISK FREE: {tele['disk_free_gb']} GB ({tele['disk_percent']}% used)</div>
            <div class="metric">CPU LOAD: {tele['cpu_load']}</div>
            <div class="metric">NETWORK: <span style="color:{color_status}">{tele['net_status']}</span></div>
        </div>

        {f'<div class="card alert"><h3>⚔️ ACTIVE ANOMALY & AI ADVICE</h3>{advice}</div>' if advice else ''}
        
        <p>Last Scan: {tele['timestamp']}</p>
    </body>
    </html>
    """
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    return REPORT_FILE

def main():
    print(f"{GREEN}[*] Spouštím OMEGA NEXUS...{RESET}")
    
    # 1. Načíst kontext
    env_data = load_heuristics()
    
    # 2. Změřit telemetrii
    telemetry = get_telemetry()
    
    # 3. Analýza anomálií
    advice = None
    issues = []
    
    if telemetry["disk_free_gb"] < 1.0:
        issues.append(f"Kriticky málo místa na disku ({telemetry['disk_free_gb']} GB)")
    
    if telemetry["net_status"] == "OFFLINE":
        issues.append("Ztráta konektivity")

    # Pokud jsou problémy, voláme AI
    if issues:
        advice = consult_gemini(", ".join(issues))
    else:
        print(f"{GREEN}✅ Systém je stabilní. Žádné anomálie.{RESET}")

    # 4. Generovat report
    report_path = generate_html_report(env_data, telemetry, advice)
    print(f"{GREEN}[+] Report vygenerován: {report_path}{RESET}")
    print(f"    -> Pro zobrazení použij: termux-open {report_path}")

if __name__ == "__main__":
    main()
