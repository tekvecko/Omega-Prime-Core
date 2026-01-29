import os
from flask import Flask, render_template_string

# --- KONFIGURACE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "nohup.out")

app = Flask(__name__)

# --- HTML ŠABLONA (CYBERPUNK STYLE) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ω OMEGA DASHBOARD</title>
    <meta http-equiv="refresh" content="5"> <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background-color: #0d1117; color: #00ff41; font-family: 'Courier New', monospace; padding: 20px; }
        h1 { border-bottom: 2px solid #00ff41; padding-bottom: 10px; }
        .status { color: #00bfff; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: left; }
        th { background-color: #161b22; color: #ff0055; }
        tr:nth-child(even) { background-color: #0d1117; }
        tr:nth-child(odd) { background-color: #161b22; }
        .time { color: #8b949e; width: 150px; }
        .error { color: #ff0055; }
        .info { color: #00ff41; }
        .warning { color: #f1e05a; }
    </style>
</head>
<body>
    <h1>👁️ OMEGA PRIME: <span class="status">ONLINE</span></h1>
    <p>Lokace jádra: {{ base_dir }}</p>
    
    <table>
        <thead>
            <tr>
                <th>RAW LOG DATA</th>
            </tr>
        </thead>
        <tbody>
            {% for line in logs %}
            <tr>
                <td>
                    {% if "ERROR" in line or "CHYBA" in line or "Traceback" in line %}
                        <span class="error">{{ line }}</span>
                    {% elif "VAROVÁNÍ" in line or "WARNING" in line %}
                        <span class="warning">{{ line }}</span>
                    {% else %}
                        <span class="info">{{ line }}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route('/')
@app.route('/dashboard')
def dashboard():
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            # Čteme posledních 50 řádků
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
                logs = [line.strip() for line in reversed(lines[-50:])] # Od nejnovějšího
        except Exception as e:
            logs = [f"❌ CHYBA ČTENÍ LOGU: {e}"]
    else:
        logs = ["⚠️ Log soubor zatím neexistuje (Systém spí nebo nebyl spuštěn)."]

    return render_template_string(HTML_TEMPLATE, logs=logs, base_dir=BASE_DIR)

if __name__ == '__main__':
    # Spuštění na všech rozhraních, port 5000
    print("   [SERVER] Startuji Dashboard na portu 5000...")
    app.run(host='0.0.0.0', port=5000)
