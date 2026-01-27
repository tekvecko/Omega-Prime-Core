import google.generativeai as genai
import subprocess
import time
import os
import sys

# --- KONFIGURACE ---
API_KEY_FILE = "api_key.txt"
SHADOW_DIR = "SHADOW_REALM"

# 1. NAČTENÍ KLÍČE
if not os.path.exists(API_KEY_FILE):
    print(f"CRITICAL: Soubor {API_KEY_FILE} nenalezen!")
    exit(1)

with open(API_KEY_FILE, "r") as f:
    api_key_content = f.read().strip()
    genai.configure(api_key=api_key_content)
    print("🔑 KLÍČ NAČTEN. ARCHITEKT PŘIPRAVEN.")

# 2. PŘÍPRAVA SANDBOXU
def setup_shadow_realm():
    print(f"--- VSTUP DO ZÓNY: {SHADOW_DIR} ---")
    if not os.path.exists(SHADOW_DIR):
        os.makedirs(SHADOW_DIR)
    os.chdir(SHADOW_DIR)
    # Vyčistíme hřiště pro čistý start (volitelné)
    # subprocess.run("rm -rf *", shell=True) 
    print(f"🏗️ STAVENIŠTĚ PŘIPRAVENO: {os.getcwd()}")

# 3. AI MODEL
def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        best = next((m for m in models if "flash" in m or "pro" in m), models[0])
        print(f"🧠 MOZEK: {best}")
        return genai.GenerativeModel(best)
    except Exception as e:
        print(f"CRITICAL: {e}")
        exit(1)

# 4. EXECUTOR (STAVITEL)
def execute_raw(cmd):
    print(f"🔨 BUILD EXEC: {cmd}")
    try:
        # Timeout zvýšen na 15s pro instalace nebo složitější zápisy
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=15)
        output = result.decode('utf-8').strip()
        if len(output) > 1000: output = output[:1000] + "... [OŘÍZNUTO]"
        return output if output else "Příkaz proběhl (bez výstupu)."
    except subprocess.CalledProcessError as e:
        return f"CHYBA (Exit {e.returncode}): {e.output.decode()}"
    except Exception as e:
        return f"CRITICAL FAIL: {str(e)}"

# 5. HLAVNÍ SMYČKA
def loop():
    setup_shadow_realm()
    
    # Automatické nastavení mise
    print("\n--- SHADOW BUILDER: REŽIM TVORBY ---")
    mission = "Vytvoř v Pythonu jednoduchý HTTP Server (port 9000) a SQLite databázi 'omega.db'. Vytvoř tabulku 'logs' a vlož testovací záznam."
    max_loops = 10
    
    print(f"CÍL MISE: {mission}")
    print(f"POČET KROKŮ: {max_loops}")
    print("-----------------------------------")
    
    model = get_model()
    chat = model.start_chat(history=[])
    
    # Kontext pro AI - ARCHITEKT
    sys_output = (
        f"Jsi SHADOW ARCHITECT v prostředí Termux. "
        f"Máš neomezená práva v adresáři {SHADOW_DIR}. "
        f"Tvůj úkol: {mission}. "
        f"POSTUPUJ TAKTO:\n"
        f"1. Vytvoř kód pro DB (`db_init.py`) pomocí `cat << 'EOF' > ...`\n"
        f"2. Spusť ho (`python3 db_init.py`).\n"
        f"3. Vytvoř kód serveru (`server.py`).\n"
        f"4. Spusť server na pozadí (`nohup python3 server.py > server.log 2>&1 &`).\n"
        f"5. Ověř, že to běží (`ps aux`, `curl`).\n"
        f"Aktuální soubory: {os.listdir('.')}"
    )
    
    for i in range(1, max_loops + 1):
        print(f"\n🔄 [KROK {i}/{max_loops}]")
        
        try:
            prompt = (
                f"STAV SYSTÉMU: {sys_output}\n\n"
                f"ROZKAZ: Napiš 'EXEC: <příkaz>' pro vytvoření souboru nebo spuštění kódu. "
                f"Pokud jsi hotov, napiš 'HOTOVO'."
            )
            
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"🤖 AI: {ai_text}")

            if "EXEC:" in ai_text:
                # Ošetření víceřádkových příkazů (pro cat << EOF)
                raw_cmd = ai_text.split("EXEC:", 1)[1].strip()
                # Pokud AI použila Markdown bloky ```, odstraníme je
                raw_cmd = raw_cmd.replace("```bash", "").replace("```python", "").replace("```", "")
                
                cmd_result = execute_raw(raw_cmd)
                print(f"💻 VÝSTUP:\n{cmd_result}")
                
                sys_output = f"Výsledek akce:\n{cmd_result}\nAktuální soubory: {os.listdir('.')}"
            elif "HOTOVO" in ai_text:
                print("✅ AI hlásí splnění mise.")
                break
            else:
                sys_output = "Žádná 'EXEC:' instrukce nenalezena. Zkus to znovu."
                
            time.sleep(2)

        except Exception as e:
            print(f"❌ CHYBA: {e}")
            break

    print(f"\n--- BUILD COMPLETE ---")
    print(f"Výsledné soubory v {SHADOW_DIR}: {os.listdir('.')}")

if __name__ == "__main__":
    loop()
