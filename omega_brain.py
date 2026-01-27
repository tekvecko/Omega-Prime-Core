import os
import sys
import json
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-2.0-flash-exp"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# PŘESNÁ MAPA EXISTUJÍCÍCH SOUBORŮ
# Aby si AI nevymýšlela, musíme jí říct, co SKUTEČNĚ existuje.
REALITY_CONTEXT = """
Jsi 'Omega' (AI Agent v Termuxu).
TOTO JSOU JEDINÉ EXISTUJÍCÍ SOUBORY (NEVYMÝŠLEJ SI JINÉ):
- ./omega_dashboard.py (běžící server)
- ./project_manager.py (správa designu)
- ./spinner.sh (animace)
- ./run_guard.sh (spouštěč)
- ./omega_modules/ (složka: 01_cleaner.py, 11_ar_shave.py, atd.)

PRAVIDLA CHOVÁNÍ (STRIKTNÍ):
1. Pokud máš něco udělat (např. 'analyzuj jádro'), NEVOLEJ neexistující skript (jako 'core_analyzer.py').
2. Místo toho VYGENERUJ NOVÝ Python skript, který tu analýzu provede (např. otevře soubory a přečte je).
3. NIKDY nepoužívej 'sudo' (jsi v Termuxu).
4. Výstup musí být ČISTÝ KÓD (Python nebo Bash). Žádné markdowny.
"""

def clean_response(text):
    text = text.replace("```bash", "").replace("```python", "").replace("```", "")
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        s = line.strip()
        # Filtrace keců okolo
        if s.lower().startswith("here is") or s.lower().startswith("python:") or s.lower().startswith("bash:"): continue
        clean_lines.append(line)
    return "\n".join(clean_lines).strip()

def query_gemini(prompt):
    if not API_KEY:
        print("echo 'CRITICAL: CHYBÍ API KLÍČ'")
        sys.exit(1)

    full_prompt = REALITY_CONTEXT + "\nUŽIVATEL CHCE: " + prompt + "\n\nVYGENERUJ KÓD PRO TENTO ÚKOL:"

    data = {"contents": [{"parts": [{"text": full_prompt}]}]}

    try:
        req = urllib.request.Request(URL, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            if 'candidates' in result:
                print(clean_response(result['candidates'][0]['content']['parts'][0]['text']))
            else:
                print("echo 'AI ERROR: Prázdná odpověď'")
    except Exception as e:
        print(f"echo 'CONNECTION ERROR: {e}'")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    query_gemini(sys.argv[1])
