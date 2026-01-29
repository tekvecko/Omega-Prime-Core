import os
import google.generativeai as genai
import re
from omega_config import config

# 1. KONFIGURACE
API_KEY_FILE = config.get('ai', {}).get('api_key_file', "api_key.txt")
MODEL_NAME = config.get('ai', {}).get('model', 'models/gemini-pro-latest')
OUTPUT_DIR = "SHADOW_REALM/Project_Genesis"

# 2. NAČTENÍ API
try:
    with open(API_KEY_FILE, "r") as f:
        genai.configure(api_key=f.read().strip())
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    exit(1)

def create_project_structure():
    print(f"\n🏭 OMEGA FACTORY: GENESIS PROTOCOL")
    print(f"   Model: {MODEL_NAME}")
    print(f"   Cíl: {OUTPUT_DIR}")
    
    project_desc = input("\n📝 Popiš detailně, jaký E-SHOP chceš (např. 'Prodej tenisek, Flask, SQLite, tmavý design'):\n> ")
    
    print("\n🧠 Generuji architekturu a kód (to může chvíli trvat)...")
    
    # Masivní prompt pro vytvoření více souborů najednou
    prompt = f"""
    Jsi Senior Python Developer. Vytvoř funkční prototyp e-shopu v Pythonu (Flask).
    Zadání: {project_desc}
    
    Musíš vygenerovat 3 soubory:
    1. app.py (Backend, SQLite modely, routy)
    2. templates/base.html (Hlavní šablona, CSS styl v <style>)
    3. templates/index.html (Domovská stránka s výpisem produktů)
    
    DŮLEŽITÉ: 
    Před každým souborem napiš přesně tento oddělovač:
    ### FILE: nazev_souboru ###
    
    Příklad:
    ### FILE: app.py ###
    ...kod...
    ### FILE: templates/base.html ###
    ...kod...
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
    except Exception as e:
        print(f"❌ Chyba generování: {e}")
        return

    # 3. PARSOVÁNÍ A ZÁPIS SOUBORŮ
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        os.makedirs(f"{OUTPUT_DIR}/templates")

    files = text.split("### FILE:")
    count = 0
    
    for f in files:
        if not f.strip(): continue
        
        # Rozdělení na název a obsah
        parts = f.strip().split("\n", 1)
        if len(parts) < 2: continue
        
        filename = parts[0].strip()
        content = parts[1].strip().replace("```python", "").replace("```html", "").replace("```", "")
        
        # Cesta k souboru
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Zápis
        with open(filepath, "w") as out:
            out.write(content)
        
        print(f"   ✅ Vytvořen: {filename}")
        count += 1

    print(f"\n✨ HOTOVO. Projekt vygenerován v: {OUTPUT_DIR}")
    print(f"   Spuštění: cd {OUTPUT_DIR} && python3 app.py")

if __name__ == "__main__":
    create_project_structure()
