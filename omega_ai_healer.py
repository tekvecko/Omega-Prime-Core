#!/usr/bin/env python3
import sys
import os
import re
import json
import urllib.request

# --- OMEGA AI HEALER v2.0 (Gemini Integration) ---
# Cíl: Odeslat chybu a kód do LLM -> Získat opravu -> Přepsat soubor

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

def extract_filename_from_log(log_content):
    """Najde jméno souboru, který způsobil pád (hledá v Tracebacku)."""
    # Hledá: File "/cesta/k/souboru.py", line X
    match = re.search(r'File "(.*?)", line', log_content)
    if match:
        return match.group(1)
    return None

def call_gemini_fix(code, error_log):
    """Odešle prompt do Gemini API."""
    if not API_KEY:
        return None, "MISSING_API_KEY"

    prompt = f"""
    Jsi expertní Python debugger. Mám tento chybový log a tento kód.
    
    CHYBA:
    {error_log}
    
    KÓD:
    {code}
    
    ÚKOL:
    Oprav kód tak, aby chyba zmizela. 
    Vrať POUZE kompletní opravený Python kód. 
    Žádné vysvětlování, žádné markdown značky navíc, jen čistý kód (nebo kód v ```python bloku).
    """

    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        req = urllib.request.Request(
            MODEL_URL, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            return result['candidates'][0]['content']['parts'][0]['text'], "OK"
    except Exception as e:
        return None, str(e)

def clean_code_block(raw_text):
    """Očistí odpověď od Markdown značek (```python ... ```)."""
    # Pokud je tam ```python, vezmeme to uvnitř
    match = re.search(r'```python\n(.*?)```', raw_text, re.DOTALL)
    if match:
        return match.group(1)
    # Zkusíme obecný blok
    match = re.search(r'```\n(.*?)```', raw_text, re.DOTALL)
    if match:
        return match.group(1)
    # Jinak vrátíme celý text (doufáme, že model poslechl a poslal jen kód)
    return raw_text

def main():
    if len(sys.argv) < 2:
        print("NO_INPUT")
        sys.exit(1)

    log_file = sys.argv[1]
    
    try:
        with open(log_file, 'r', errors='replace') as f:
            log_content = f.read()
    except:
        print("LOG_READ_ERROR")
        sys.exit(1)

    # 1. Analýza logu - hledáme soubor
    target_file = extract_filename_from_log(log_content)
    if not target_file or not os.path.exists(target_file):
        # Pokud nevíme, jaký soubor opravit, končíme
        print(f"TARGET_UNKNOWN (File: {target_file})")
        sys.exit(1)

    print(f"🎯 CÍL: {os.path.basename(target_file)}")

    # 2. Načtení rozbitého kódu
    with open(target_file, 'r') as f:
        broken_code = f.read()

    # 3. Volání Doktora (Gemini)
    print("🤖 Odesílám data do Gemini k opravě...")
    fixed_code_raw, status = call_gemini_fix(broken_code, log_content)

    if status != "OK":
        print(f"API_ERROR: {status}")
        sys.exit(1)

    # 4. Aplikace "Léku"
    final_code = clean_code_block(fixed_code_raw)
    
    # Bezpečnostní kontrola - neukládat prázdný soubor
    if len(final_code) < 10:
        print("FIX_FAILED (Received empty code)")
        sys.exit(1)

    with open(target_file, 'w') as f:
        f.write(final_code)

    print(f"FIXED: Soubor {os.path.basename(target_file)} byl přepsán AI opravou.")

if __name__ == "__main__":
    main()
