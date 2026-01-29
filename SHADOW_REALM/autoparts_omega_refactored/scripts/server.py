from flask import Flask, request, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__)
# Zde je změna: Pokud Nexus neřekne jinak, použij 'omega.db'
DB_NAME = os.environ.get('OMEGA_DB_PATH', 'omega.db')

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, message TEXT)')

@app.route('/')
def home():
    # Zobrazíme, kterou databázi zrovna používáme
    db_label = DB_NAME.replace(".db", "").upper()
    return f"""
    <html>
    <head>
        <title>OMEGA {db_label}</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body {{ background-color: #0d0d0d; color: #00ff41; font-family: monospace; padding: 20px; }}
            h1 {{ border-bottom: 1px solid #00ff41; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #333; padding: 10px; text-align: left; }}
            th {{ background-color: #1a1a1a; color: #fff; }}
            .timestamp {{ color: #888; }}
            .highlight {{ color: #fff; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>👁️ OMEGA: {db_label}</h1>
        <p>Status: <span style="color:lime">ONLINE</span> | DB: {DB_NAME}</p>
        <h2>📡 ZACHYCENÉ PŘENOSY</h2>
        <table>
            <tr><th>ČAS</th><th>ZPRÁVA</th></tr>
            %ROWS%
        </table>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard_view():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 20').fetchall()
    
    table_rows = ""
    for r in rows:
        time, msg = r
        if "LAN REAPER" in msg:
            msg = msg.replace("[", "<br><span class='highlight'>").replace("]", "</span>")
            msg = msg.replace("'", "").replace(",", "<br>")
        table_rows += f"<tr><td class='timestamp'>{time.split('T')[1][:8]}</td><td>{msg}</td></tr>"

    return home().replace("%ROWS%", table_rows)

@app.route('/log', methods=['POST'])
def log_msg():
    data = request.json
    msg = data.get('message', 'No message')
    now = datetime.datetime.now().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('INSERT INTO logs VALUES (?, ?)', (now, msg))
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
