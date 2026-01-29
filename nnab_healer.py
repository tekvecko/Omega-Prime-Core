import os, sys, google.generativeai as genai

# KONFIGURACE
API_KEY_FILE = "api_key.txt"
CRASH_LOG = "nnab_crash.log"
CORE_FILE = "nnab_core.py"

def heal():
    print(f"\033[1;33m[HEALER] Analýza pádu: {CRASH_LOG}...\033[0m")
    
    if not os.path.exists(CRASH_LOG):
        print("[HEALER] Žádný log. Restartuji.")
        return

    with open(CRASH_LOG, "r") as f: error_txt = f.read()
    if not error_txt.strip(): return

    try:
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, "r") as f: 
                genai.configure(api_key=f.read().strip())
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                print("[HEALER] Volám AI na opravu...")
                with open(CORE_FILE, "r") as f: src = f.read()
                
                prompt = f"Fix Python code based on error. Return ONLY code.\nERR:\n{error_txt}\nCODE:\n{src}"
                res = model.generate_content(prompt)
                fix = res.text.replace("```python","").replace("```","").strip()
                
                if len(fix) > 50:
                    with open(CORE_FILE, "w") as f: f.write(fix)
                    print("\033[1;32m[HEALER] ✅ OPRAVENO. RESTARTUJI.\033[0m")
    except Exception as e:
        print(f"[HEALER] Chyba AI: {e}")

if __name__ == "__main__":
    heal()
