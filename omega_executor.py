import google.generativeai as genai
import subprocess
import time
import os
import sys

# --- KONFIGURACE ---
API_KEY_FILE = "api_key.txt"

# Bezpečnostní filtr (BLACKLIST)
FORBIDDEN_CMDS = ['rm ', 'mv ', 'chmod', 'chown', 'wget', 'curl', 'dd ', ':(){', 'reboot', 'shutdown']

# 1. Načtení klíče
if not os.path.exists(API_KEY_FILE):
    print("CRITICAL: Chybí api_key.txt")
    exit(1)
with open(API_KEY_FILE, "r") as f:
    genai.configure(api_key=f.read().strip())

# 2. Autodetekce modelu
def get_model():
    print("--- OMEGA: Inicializuji neurální spojení... ---")
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        best = next((m for m in models if "flash" in m or "pro" in m), models[0])
        print(f"✅ MOZEK: {best}")
        return genai.GenerativeModel(best)
    except:
        print("CRITICAL: Žádný model neodpovídá.")
        exit(1)

# 3. Funkce EXECUTOR
def execute_command(cmd):
    for bad in FORBIDDEN_CMDS:
        if bad in cmd:
            return f"SECURITY BLOCK: Příkaz '{cmd}' zakázán protokolem."
    
    print(f"⚡ RUNNING: {cmd}")
    try:
        # Timeout 5s, aby se nezasekl
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        output = result.decode('utf-8').strip()
        if len(output) > 800: output = output[:800] + "\n... [VÝSTUP OŘÍZNUT]"
        return output if output else "Příkaz proběhl (žádný textový výstup)."
    except subprocess.CalledProcessError as e:
        return f"CHYBA TERMINÁLU (Exit {e.returncode}): {e.output.decode()}"
    except Exception as e:
        return f"CHYBA EXEKUCE: {str(e)}"

# 4. HLAVNÍ SMYČKA S VSTUPEM UŽIVATELE
def loop():
    # A) Výběr parametrů mise
    print("\n--- OMEGA EXECUTOR v2: MISSION CONFIG ---")
    
    try:
        iter_input = input("1. Počet cyklů (Default 5): ").strip()
        max_loops = int(iter_input) if iter_input.isdigit() else 5
        
        mission_focus = input("2. OBLAST ZÁJMU (např. 'Síť', 'Baterie', 'Úložiště'): ").strip()
        if not mission_focus: mission_focus = "Celková diagnostika"
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit()

    # B) Start AI
    model = get_model()
    chat = model.start_chat(history=[])
    
    print(f"\n--- START MISE: {mission_focus} ({max_loops} kol) ---")
    
    # Prvotní kontext pro AI - DŮLEŽITÉ PRO ZAMĚŘENÍ
    sys_output = (
        f"START: Jsi OMEGA, terminálová AI v prostředí Termux (Android). "
        f"Uživatel ti zadal specifický úkol: '{mission_focus}'. "
        f"Nejdřív zjisti fakta pomocí příkazů. Nevymýšlej si data."
    )
    
    for i in range(1, max_loops + 1):
        print(f"\n🔄 [KOLO {i}/{max_loops}]")
        
        try:
            prompt = (
                f"SYSTÉM HLÁSÍ: {sys_output}\n\n"
                f"MOŽNOSTI:\n"
                f"A) Pokud potřebuješ data, napiš: 'EXEC: <příkaz>'\n"
                f"B) Pokud máš hotovo nebo chceš informovat uživatele, napiš jen text.\n"
                f"Buď stručný. Řeš pouze: {mission_focus}."
            )
            
            response = chat.send_message(prompt)
            ai_text = response.text.strip()
            print(f"🤖 AI: {ai_text}")

            if "EXEC:" in ai_text:
                cmd = ai_text.split("EXEC:")[1].strip().split('\n')[0]
                cmd_result = execute_command(cmd)
                print(f"💻 VÝSTUP:\n{cmd_result}")
                
                # Odeslání notifikace jen při akci
                subprocess.run(["termux-notification", "--title", f"OMEGA EXEC {i}", "--content", cmd], check=False)
                
                sys_output = f"Výsledek příkazu '{cmd}':\n{cmd_result}"
            else:
                sys_output = "Žádný příkaz. Čekám na další instrukce nebo ukončení."
                
            time.sleep(2)

        except Exception as e:
            print(f"❌ CRASH: {e}")
            break

    print(f"\n--- MISE '{mission_focus}' DOKONČENA ---")
    subprocess.run(["termux-notification", "--title", "OMEGA", "--content", "Mise dokončena."], check=False)

if __name__ == "__main__":
    loop()
