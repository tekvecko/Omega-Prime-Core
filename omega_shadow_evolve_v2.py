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
        print("CRITICAL: Shadow Realm neexistuje! Nejdřív spusť build.")
        exit(1)
    os.chdir(SHADOW_DIR)
    print(f"--- SHADOW REALM: {os.getcwd()} ---")

# 3. EXECUTOR (S REGEX PARSEREM)
def execute_smart(ai_response):
    # Hledáme bloky kódu označené ```bash nebo jen ```
    code_blocks = re.findall(r'```(?:bash|sh)?\n(.*?)```', ai_response, re.DOTALL)
    
    if not code_blocks:
        # Pokud AI nepoužila bloky, zkusíme najít řádky začínající EXEC:
        lines = ai_response.split('\n')
        commands = [line.split('EXEC:', 1)[1].strip() for line in lines if 'EXEC:' in line]
        if not commands:
            return "Žádný spustitelný kód nenalezen."
    else:
        commands = code_blocks

    output_log = ""
    for cmd in commands:
        print(f"🔧 RUNNING: {cmd[:50]}...")
        try:
            # Povolíme složitější operace
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=20)
            output_log += result.decode('utf-8') + "\n"
        except subprocess.CalledProcessError as e:
            output_log += f"CHYBA (Exit {e.returncode}): {e.output.decode()}\n"
        except Exception as e:
            output_log += f"CRITICAL: {str(e)}\n"
            
    return output_log if output_log.strip() else "Příkazy provedeny (bez výstupu)."

# 4. HLAVNÍ SMYČKA
def loop():
    enter_shadow_realm()
    
    # Načtení modelu
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    best = next((m for m in models if "flash" in m or "pro" in m), models[0])
    model = genai.GenerativeModel(best)
    chat = model.start_chat(history=[])

    # ZADÁNÍ OD KLIENTA (ARCHITEKTA)
    mission = (
        "Uprav 'server.py'. Chci endpoint GET '/view', který vypíše obsah tabulky 'logs' "
        "jako hezkou HTML tabulku. "
        "Až to přepíšeš, restartuj server (pkill python3 -> nohup python3 server.py)."
    )
    
    print(f"POŽADAVEK: {mission}")

    sys_output = (
        f"Jsi SHADOW DEVELOPER v2. "
        f"Tvůj úkol: {mission}\n"
        f"DŮLEŽITÉ: Veškerý shell kód (cat, pkill, nohup) zabal do bloků ```bash ... ```.\n"
        f"Nepoužívej prefix EXEC, použij Markdown bloky."
    )

    for i in range(1, 5):
        print(f"\n🔄 [EVOLUCE {i}/5]")
        
        try:
            prompt = f"STAV: {sys_output}\n\nAKCE (Zabal kód do ```bash):"
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"🤖 AI:\n{ai_text[:100]}...") # Výpis jen začátku

            res = execute_smart(ai_text)
            print(f"💻 VÝSTUP SYSTÉMU:\n{res}")
            
            if "server.py" in ai_text and "nohup" in ai_text:
                print("✅ Vypadá to, že server byl aktualizován a restartován.")
                break
                
            sys_output = f"Výsledek tvých příkazů:\n{res}"
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ CHYBA: {e}")
            break

if __name__ == "__main__":
    loop()
