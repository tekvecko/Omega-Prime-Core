import google.generativeai as genai
import subprocess
import time
import os

# --- KONFIGURACE ---
ITERATIONS = 5
API_KEY_FILE = "api_key.txt"
EVO_FILE = "evolution_log.txt"

# 1. Načtení klíče
if not os.path.exists(API_KEY_FILE):
    print("CRITICAL: Soubor api_key.txt neexistuje!")
    exit(1)

with open(API_KEY_FILE, "r") as f:
    API_KEY = f.read().strip()

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"CRITICAL: Chyba konfigurace API! {e}")
    exit(1)

# 2. Dynamické získání modelu
def get_best_model():
    print("--- OMEGA: Stahuji seznam dostupných mozků... ---")
    try:
        available_models = []
        # Projdeme všechny modely, které API nabízí
        for m in genai.list_models():
            # Hledáme jen ty, které umí chatovat (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                print(f"Nalezen kandidát: {m.name}")
        
        if not available_models:
            print("CRITICAL: API klíč je platný, ale žádný model nepodporuje chat!")
            exit(1)

        # Vybereme první vhodný (upřednostníme Flash nebo Pro, pokud jsou v seznamu)
        selected_model = available_models[0]
        for m in available_models:
            if "flash" in m or "pro" in m:
                selected_model = m
                break
        
        print(f"✅ VYBRÁNO: {selected_model}")
        return genai.GenerativeModel(selected_model)

    except Exception as e:
        print(f"CRITICAL: Nelze získat seznam modelů. {e}")
        exit(1)

# 3. Notifikace
def send_notification(step, content):
    title = f"OMEGA ACTION [{step}/{ITERATIONS}]"
    subprocess.run(["termux-notification", "--title", title, "--content", content], check=False)

# 4. Exekuce (Zápis)
def system_execute(action_text):
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] PROVEDENO: {action_text}"
    with open(EVO_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    return "Zápis do logu OK."

# 5. HLAVNÍ SMYČKA OUROBOROS
def loop():
    # Získáme model dynamicky
    model = get_best_model()
    
    print("\n--- OMEGA: AUTONOMOUS LOOP STARTED ---")
    feedback_payload = "START: Zahajuji test autonomie. Jaký je první krok?"
    
    # Start chatu
    chat = model.start_chat(history=[])

    for i in range(1, ITERATIONS + 1):
        print(f"\n🔄 KOLO {i}: Komunikace s AI...")
        
        try:
            # A) OMEGA -> GEMINI
            response = chat.send_message(
                f"Jsi systém OMEGA. Report: {feedback_payload}\n"
                f"PŘÍKAZ: Napiš jen jednu krátkou větu, co mám udělat teď. (Např: 'Zkontroluj X', 'Zapiš Y')."
            )
            ai_command = response.text.strip()
            print(f"🤖 ROZKAZ: {ai_command}")

            # B) OMEGA -> SYSTEM
            time.sleep(2)
            res = system_execute(ai_command)
            send_notification(i, ai_command)
            print(f"✅ AKCE: {res}")

            # C) SYSTEM -> OMEGA (Feedback)
            feedback_payload = f"Provedeno: '{ai_command}'. Výsledek: Úspěch. Co dál?"
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ CHYBA BĚHEM SMYČKY: {e}")
            break

    print("\n--- TEST DOKONČEN ---")
    send_notification("FINÁLE", "Autonomní smyčka ukončena.")

if __name__ == "__main__":
    loop()
