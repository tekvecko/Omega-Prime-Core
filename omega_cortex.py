import asyncio
import google.generativeai as genai
import json
import os
import time

# --- KONFIGURACE ---
HERMES_HOST = '127.0.0.1'
HERMES_PORT = 8888
MEMORY_DIR = "/data/data/com.termux/files/home/OMEGA_MEMORY"
MAP_FILE = os.path.join(MEMORY_DIR, "network_map.json")
REPORT_FILE = os.path.join(MEMORY_DIR, "cortex_report.txt")
API_KEY_FILE = "api_key.txt"

# Načtení klíče
try:
    with open(API_KEY_FILE, "r") as f:
        API_KEY = f.read().strip()
    genai.configure(api_key=API_KEY)
    MODEL = genai.GenerativeModel('gemini-1.5-flash') # Rychlý model
except Exception as e:
    print(f"CRITICAL: Nelze načíst API klíč! {e}")
    exit(1)

async def send_to_hermes(msg):
    try:
        reader, writer = await asyncio.open_connection(HERMES_HOST, HERMES_PORT)
        writer.write(f"MEMORIZE:{msg}".encode('utf-8'))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except:
        pass

def analyze_situation():
    """Sesbírá data a pošle je AI k analýze"""
    print("CORTEX: Analyzuji data...")
    
    # 1. Načíst síťová data
    net_data = "Žádná data sítě."
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, 'r') as f:
            net_data = f.read()
            
    # 2. Prompt pro AI
    prompt = f"""
    Jsi OMEGA CORTEX, bezpečnostní AI.
    Analyzuj tento JSON výpis z lokální sítě a vytvoř stručný bezpečnostní report v češtině.
    
    DATA SÍTĚ:
    {net_data}
    
    ÚKOLY:
    1. Identifikuj podezřelá zařízení nebo otevřené porty.
    2. Zhodnoť celkové "zdraví" sítě (škála 0-100%).
    3. Pokud vidíš SSH (port 22) nebo neznámé zařízení, vydat varování.
    
    Výstup formátuj jako HTML (použij <b>, <br>, <ul>). Buď stručný a profesionální.
    """
    
    try:
        response = MODEL.generate_content(prompt)
        report = response.text
        
        # Uložení reportu
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report)
            
        print("CORTEX: Analýza hotova a uložena.")
        return "AI Report Aktualizován"
    except Exception as e:
        err = f"Chyba spojení s AI: {e}"
        print(err)
        return err

async def cortex_loop():
    print("OMEGA CORTEX (Gemini Core) aktivován...")
    # První analýza hned po startu
    res = analyze_situation()
    await send_to_hermes(f"CORTEX: {res}")
    
    while True:
        # Analýza každých 10 minut (šetříme API limity)
        await asyncio.sleep(600) 
        res = analyze_situation()
        await send_to_hermes(f"CORTEX: {res}")

if __name__ == "__main__":
    asyncio.run(cortex_loop())
