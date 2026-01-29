import google.generativeai as genai
import os

# Barvy
GREEN = "\033[1;32m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
RESET = "\033[0m"

API_KEY_FILE = "api_key.txt"

def scan_models():
    print(f"\n{CYAN}--- OMEGA MODEL SCANNER ---{RESET}")
    
    if not os.path.exists(API_KEY_FILE):
        print(f"{RED}Chybí api_key.txt!{RESET}")
        return

    try:
        with open(API_KEY_FILE, "r") as f:
            key = f.read().strip()
            genai.configure(api_key=key)
        
        print("Dotazuji se serverů Google...")
        
        valid_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                valid_models.append(m.name)

        if not valid_models:
            print(f"{RED}Nebyly nalezeny žádné modely! Zkontroluj API klíč.{RESET}")
        else:
            print(f"\n{GREEN}✅ NALEZENÉ FUNKČNÍ MODELY:{RESET}")
            for model in valid_models:
                # Ořízneme 'models/' pro čistší název
                clean_name = model.replace("models/", "")
                print(f"   - {clean_name}")
            
            print(f"\n{CYAN}DOPORUČENÍ:{RESET}")
            print("Vyber jeden z výše uvedených a zapiš ho do 'omega_config.py'.")

    except Exception as e:
        print(f"{RED}CHYBA PŘIPOJENÍ: {e}{RESET}")
        print("Tip: Zkus 'pip install --upgrade google-generativeai'")

if __name__ == "__main__":
    scan_models()
