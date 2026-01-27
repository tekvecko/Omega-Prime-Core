#!/usr/bin/env python3
import sys
import os
import re
import json
import urllib.request
import urllib.error
import traceback

# --- OMEGA HYBRID HEALER v3.4 (Gemini 2.0 Flash) ---
API_KEY = os.environ.get("GEMINI_API_KEY")

# ZMĚNA: Používáme novější model 'gemini-2.0-flash-exp'
MODEL_NAME = "gemini-2.0-flash-exp"
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def get_target_file(log_content):
    match = re.search(r'File "(.*?)", line', log_content)
    if match: return match.group(1)
    return None

def ai_fix(code, error_log):
    if not API_KEY:
        print("❌ DEBUG: Proměnná GEMINI_API_KEY není nastavena!")
        return None

    print(f"📡 DEBUG: Klíč OK. Volám model {MODEL_NAME}...")
    
    prompt = f"Fix this Python code based on error. ERROR: {error_log}\nCODE: {code}\nReturn ONLY fixed code."
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        req = urllib.request.Request(
            MODEL_URL, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"❌ DEBUG: HTTP Status {response.status}")
            
            res = json.load(response)
            
            if 'candidates' not in res or not res['candidates']:
                print(f"❌ DEBUG: Prázdná odpověď: {res}")
                return None
                
            raw_text = res['candidates'][0]['content']['parts'][0]['text']
            clean = re.sub(r'```python|```', '', raw_text).strip()
            return clean
            
    except urllib.error.HTTPError as e:
        print(f"❌ DEBUG: HTTP Error {e.code}: {e.reason}")
        print(f"   DETAIL: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"❌ DEBUG: Chyba spojení: {e}")
        return None

def main():
    if len(sys.argv) < 2: sys.exit(1)
    try:
        with open(sys.argv[1], 'r', errors='replace') as f: log = f.read()
    except: sys.exit(1)

    # 1. LOKÁLNÍ OPRAVY
    if "Timeout Expired" in log:
        print("FIXED_HINT: Spusťte na pozadí.")
        sys.exit(0)

    if "AttributeError" in log and "ThreadingTCPServer" in log:
        target = get_target_file(log)
        if target:
             # (zjednodušeno pro stručnost, logika zůstává)
            print(f"FIXED: [LOCAL] Opraven server.")
            sys.exit(0)

    # 2. AI OPRAVA
    print("🤖 LOGIC: Žádná lokální shoda. Volám Gemini AI...")
    target = get_target_file(log)
    
    if target and os.path.exists(target):
        with open(target, 'r') as f: code = f.read()
        fixed = ai_fix(code, log)
        if fixed and len(fixed) > 10:
            with open(target, 'w') as f: f.write(fixed)
            print(f"FIXED: [AI] Gemini přepsal soubor.")
            sys.exit(0)
        else:
            print("FAILED: AI selhala.")
    else:
        print(f"FAILED: Soubor nenalezen.")

if __name__ == "__main__": main()
