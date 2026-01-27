import google.generativeai as genai
import subprocess
import time
import os
import sys

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
        print("CRITICAL: Shadow Realm neexistuje! Nejdřív spusť build.")
        exit(1)
    os.chdir(SHADOW_DIR)
    print(f"--- EVOLUCE SYSTÉMU V: {os.getcwd()} ---")

# 3. ČTENÍ EXISTUJÍCÍHO KÓDU
def read_current_code():
    if os.path.exists(SERVER_FILE):
        with open(SERVER_FILE, "r") as f:
            return f.read()
    return "Soubor neexistuje."

# 4. EXECUTOR (REŽIM ÚDRŽBY)
def execute_raw(cmd):
    print(f"🔧 MAINTAIN EXEC: {cmd}")
    try:
        # Povolíme pkill i nohup
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10)
        output = result.decode('utf-8').strip()
        return output if output else "OK (bez výstupu)."
    except subprocess.CalledProcessError as e:
        return f"CHYBA: {e.output.decode()}"
    except Exception as e:
        return f"FAIL: {str(e)}"

# 5. HLAVNÍ SMYČKA
def loop():
    enter_shadow_realm()
    
    # Načteme aktuální stav, aby AI věděla, co upravuje
    current_code = read_current_code()
    
    # ZADÁNÍ OD KLIENTA
    mission = "Uprav 'server.py'. Přidej novou cestu GET '/view', která načte data z DB (tabulka logs) a zobrazí je v HTML tabulce (<table>). Poté restartuj server."
    
    print(f"POŽADAVEK: {mission}")
    
    # Model
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    best = next((m for m in models if "flash" in m or "pro" in m), models[0])
    model = genai.GenerativeModel(best)
    chat = model.start_chat(history=[])

    sys_output = (
        f"Jsi SHADOW DEVELOPER. Tady je aktuální kód serveru:\n\n{current_code}\n\n"
        f"ÚKOL: {mission}\n"
        f"POSTUP:\n"
        f"1. Napiš vylepšený kód serveru a ulož ho (`cat << 'EOF' > server.py`).\n"
        f"2. Zastav starý server (`pkill -f server.py`).\n"
        f"3. Spusť nový (`nohup python3 server.py > server.log 2>&1 &`).\n"
        f"4. Ověř (`curl http://localhost:9000/view`)."
    )

    for i in range(1, 8): # Stačí méně kroků
        print(f"\n🔄 [EVOLUCE {i}/8]")
        
        try:
            prompt = f"STAV: {sys_output}\n\nAKCE (použij 'EXEC:'):"
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"🤖 AI: {ai_text}")

            if "EXEC:" in ai_text:
                raw_cmd = ai_text.split("EXEC:", 1)[1].strip()
                raw_cmd = raw_cmd.replace("```bash", "").replace("```python", "").replace("```", "")
                
                res = execute_raw(raw_cmd)
                print(f"💻 VÝSTUP:\n{res}")
                sys_output = f"Výsledek: {res}"
            
            elif "HOTOVO" in ai_text or "DONE" in ai_text:
                print("✅ ÚPRAVA DOKONČENA.")
                break
            
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ CHYBA: {e}")
            break

if __name__ == "__main__":
    loop()
