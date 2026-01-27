import google.generativeai as genai
import subprocess
import time
import os
import re
import sys

# --- KONFIGURACE ---
API_KEY_FILE = "api_key.txt"
SHADOW_DIR = "SHADOW_REALM"
SERVER_FILE = "server.py"
LOG_FILE = "server.log"
MAX_CYCLES = 10
REQUIRED_STABLE_STREAK = 3

# ZÁCHRANNÝ KÓD (GOLDEN TEMPLATE)
GOLDEN_CODE = """
from flask import Flask, request, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__)
DB_NAME = 'omega.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, message TEXT)')

@app.route('/')
def home():
    return "<h1>OMEGA SERVER ONLINE</h1><p>Use /log to post data.</p><p><a href='/view'>VIEW LOGS</a></p>"

@app.route('/log', methods=['POST'])
def log_msg():
    data = request.json
    msg = data.get('message', 'No message')
    now = datetime.datetime.now().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('INSERT INTO logs VALUES (?, ?)', (now, msg))
    return jsonify({"status": "ok"})

@app.route('/view')
def view_logs():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC').fetchall()
    html = '<table border="1"><tr><th>Time</th><th>Message</th></tr>'
    for r in rows:
        html += f'<tr><td>{r[0]}</td><td>{r[1]}</td></tr>'
    return html + '</table>'

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
"""

# 1. NAČTENÍ KLÍČE
if not os.path.exists(API_KEY_FILE):
    print("CRITICAL: Chybí klíč.")
    exit(1)
with open(API_KEY_FILE, "r") as f:
    genai.configure(api_key=f.read().strip())

# 2. VSTUP DO IZOLACE
if not os.path.exists(SHADOW_DIR):
    os.makedirs(SHADOW_DIR)
os.chdir(SHADOW_DIR)

# 3. POMOCNÉ FUNKCE
def run_cmd(cmd):
    try:
        # Agresivní kill pro jistotu
        if "pkill" in cmd: 
            subprocess.run("pkill -9 -f server.py", shell=True)
            time.sleep(1)
            return "Old process killed."
            
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return f"EXEC FAIL: {e}"

def write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"SOUBOR PŘEPSÁN: {len(content)} bytů."

def check_health():
    try:
        subprocess.check_output("curl -s --max-time 2 http://localhost:5000", shell=True)
        return True
    except:
        return False

def read_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return "".join(f.readlines()[-20:]) 
    return "Log missing."

# 4. EXECUTOR
def execute_ai_plan(ai_text):
    log = ""
    # Python code
    py_match = re.search(r'```python\n(.*?)```', ai_text, re.DOTALL)
    if py_match:
        log += write_file(SERVER_FILE, py_match.group(1)) + "\n"
    
    # Restart logic
    if "RESTART" in ai_text or "restart" in ai_text.lower():
        log += run_cmd(f"pkill -9 -f {SERVER_FILE}")
        # Start new
        subprocess.Popen(f"nohup python3 {SERVER_FILE} > {LOG_FILE} 2>&1 &", shell=True)
        log += "SERVER RESTART INITIATED.\n"
        
    return log

# 5. HLAVNÍ SMYČKA
def overlord_loop():
    print("--- OMEGA OVERLORD v5: DICTATOR MODE ---")
    
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    best = next((m for m in models if "flash" in m or "pro" in m), models[0])
    model = genai.GenerativeModel(best)
    chat = model.start_chat(history=[])

    cycle = 0
    stable = 0
    fails = 0

    while cycle < MAX_CYCLES:
        cycle += 1
        print(f"\n🔄 [CYKLUS {cycle}] (Streak: {stable}/{REQUIRED_STABLE_STREAK} | Fails: {fails})")
        
        is_up = check_health()
        logs = read_logs()
        
        if not is_up:
            stable = 0
            fails += 1
            print(f"   ❌ STAV: DOWN. (Log: {logs.strip()[-100:]})")
            
            # AUTOMATICKÁ ZÁCHRANA (Inject)
            if fails >= 2:
                print("   🚨 INTERVENCE: AI selhává. Vkládám GOLDEN TEMPLATE kód...")
                write_file(SERVER_FILE, GOLDEN_CODE)
                fails = 0 # Reset fail counteru
                # Okamžitý restart bez ptaní AI
                run_cmd(f"pkill -9 -f {SERVER_FILE}")
                subprocess.Popen(f"nohup python3 {SERVER_FILE} > {LOG_FILE} 2>&1 &", shell=True)
                time.sleep(3)
                continue # Skip to next cycle to verify
        else:
            stable += 1
            fails = 0
            print("   ✅ STAV: ONLINE.")

        if stable >= REQUIRED_STABLE_STREAK:
            print("\n🏆 MISSE SPLNĚNA! Systém je stabilní.")
            break

        # Pokud server běží, AI má volno. Pokud ne, AI se snaží (pokud to nebyl Golden Inject).
        if not is_up:
            prompt = (
                f"Jsi OMEGA OVERLORD v5. Server NEBĚŽÍ. Log:\n{logs}\n"
                f"ÚKOL: Oprav 'server.py'.\n"
                f"PRAVIDLA:\n"
                f"1. Vypiš CELÝ kód serveru do ```python bloku.\n"
                f"2. Pokud chceš restart, napiš na konec slovo RESTART.\n"
                f"3. Žádné shell skripty. Žádné echo."
            )
            try:
                resp = chat.send_message(prompt)
                print(f"   🤖 AI: {resp.text[:50]}...")
                print(f"   ⚡ AKCE: {execute_ai_plan(resp.text)}")
                time.sleep(3)
            except Exception as e:
                print(f"Err: {e}")

if __name__ == "__main__":
    overlord_loop()
