import google.generativeai as genai
import sqlite3
import os
import subprocess
import json

# KONFIGURACE
API_KEY_FILE = "api_key.txt"
DB_PATH = os.environ.get('OMEGA_DB_PATH', 'omega.db')
SHADOW_DIR = "SHADOW_REALM"

# Načtení API klíče
if os.path.exists(API_KEY_FILE):
    with open(API_KEY_FILE, "r") as f:
        genai.configure(api_key=f.read().strip())
else:
    print("❌ CHYBA: Chybí api_key.txt!")
    exit()

model = genai.GenerativeModel('gemini-1.5-flash')

def send_notification(title, content):
    """Pošle notifikaci do Android lišty"""
    try:
        subprocess.run(["termux-notification", "--title", title, "--content", content], check=False)
    except:
        pass # Pokud není nainstalováno API, ignorujeme

def analyze_situation():
    # Cesta k DB (musí být v SHADOW_REALM)
    db_full_path = os.path.join(SHADOW_REALM, DB_PATH) if os.path.exists(SHADOW_DIR) else DB_PATH
    
    if not os.path.exists(db_full_path):
        return

    try:
        conn = sqlite3.connect(db_full_path)
        # Získáme posledních 5 záznamů pro kontext
        rows = conn.execute("SELECT timestamp, message FROM logs ORDER BY timestamp DESC LIMIT 5").fetchall()
        conn.close()

        if not rows: return

        # Příprava dat pro Gemini
        data_text = "\n".join([f"[{r[0]}] {r[1]}" for r in rows])
        
        # PROMPT PRO GEMINI
        prompt = f"""
        Jsi bezpečnostní AI systému Omega Prime. Zde jsou poslední logy ze sítě:
        {data_text}
        
        ÚKOL:
        1. Analyzuj, zda se děje něco podezřelého (nové neznámé zařízení, výpadek, anomálie).
        2. Pokud je vše v normálu (známá zařízení), odpověz pouze "OK".
        3. Pokud je tam hrozba nebo změna, napiš krátké varování (max 1 věta) pro notifikaci.
        """

        response = model.generate_content(prompt)
        ai_msg = response.text.strip()

        print(f"   🧠 GEMINI: {ai_msg}")

        # Pokud to není jen "OK", pošleme notifikaci
        if "OK" not in ai_msg and len(ai_msg) > 2:
            send_notification("OMEGA PRIME ALERT", ai_msg)
            
    except Exception as e:
        print(f"   ⚠️ Brain Error: {e}")

if __name__ == "__main__":
    analyze_situation()
