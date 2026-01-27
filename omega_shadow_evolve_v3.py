import google.generativeai as genai
import subprocess
import time
import os
import re

# --- KONFIGURACE ---
API_KEY_FILE = "api_key.txt"
SHADOW_DIR = "SHADOW_REALM"
SERVER_FILE = "server.py"

# 1. NAČTENÍ KLÍČE
if not os.path.exists(API_KEY_FILE):
    print("CRITICAL: Chybí klíč.")
    exit(1)
with open(API_KEY_FILE, "r") as f:
    genai.configure(api_key=f.read().strip())

# 2. VSTUP DO IZOLACE
def enter_shadow_realm():
    if not os.path.exists(SHADOW_DIR):
        print("CRITICAL: Shadow Realm neexistuje!")
        exit(1)
    os.chdir(SHADOW_DIR)
    print(f"--- SHADOW REALM: {os.getcwd()} ---")

# 3. EXECUTOR (CHIRURGICKÝ)
def execute_smart(ai_response):
    # Najdeme bloky kódu
    code_blocks = re.findall(r'```(?:bash|sh)?\n(.*?)```', ai_response, re.DOTALL)
    commands = code_blocks if code_blocks else []
    
    if not commands:
        return "Žádný kód k provedení."

    output_log = ""
    for cmd in commands:
        # BEZPEČNOSTNÍ POJISTKA PROTI SEBEVRAŽDĚ
        if "pkill python" in cmd or "killall python" in cmd:
            if "-f server.py" not in cmd:
                print("⚠️ ZACHYCEN NEBEZPEČNÝ PŘÍKAZ (Kill All). Upravuji na 'pkill -f server.py'...")
                cmd = "pkill -f server.py"

        print(f"🔧 RUNNING: {cmd[:50]}...")
        try:
            # Spuštění s ignorováním chyb (pokud server neběží, pkill selže, to je OK)
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            output_log += result.stdout + result.stderr + "\n"
        except Exception as e:
            output_log += f"CRITICAL: {str(e)}\n"
            
    return output_log

# 4. HLAVNÍ SMYČKA
def loop():
    enter_shadow_realm()
    
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    best = next((m for m in models if "flash" in m or "pro" in m), models[0])
    model = genai.GenerativeModel(best)
    chat = model.start_chat(history=[])

    # ZADÁNÍ OD KLIENTA - S DŮRAZEM NA BEZPEČNÝ RESTART
    mission = (
        "Uprav 'server.py'. Přidej endpoint GET '/view', který zobrazí tabulku 'logs' v HTML. "
        "DŮLEŽITÉ: Pro restart použij PŘESNĚ tento příkaz: 'pkill -f server.py || true'. "
        "NIKDY nepoužívej 'pkill python3' (zabil bys mě)!"
    )
    
    print(f"POŽADAVEK: {mission}")

    sys_output = (
        f"Jsi SHADOW DEVELOPER v3. Úkol: {mission}\n"
        f"1. Vygeneruj nový 'server.py' (pomocí cat << EOF).\n"
        f"2. Restartuj server (`pkill -f server.py` -> `nohup python3 server.py ...`).\n"
        f"Vše zabal do ```bash bloků."
    )

    for i in range(1, 4):
        print(f"\n🔄 [EVOLUCE {i}/4]")
        
        try:
            prompt = f"STAV: {sys_output}\n\nAKCE (Zabal kód do ```bash):"
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"🤖 AI:\n{ai_text[:100]}...") 

            res = execute_smart(ai_text)
            print(f"💻 VÝSTUP SYSTÉMU:\n{res}")
            
            if "server.py" in ai_text and "nohup" in ai_text:
                print("✅ Server restartován.")
                break
                
            sys_output = f"Výsledek: {res}"
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ CHYBA: {e}")
            break

if __name__ == "__main__":
    loop()
