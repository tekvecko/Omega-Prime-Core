
from flask import Flask, request, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__)
DB_NAME = 'omega.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, message TEXT)')

@app.route('/')
def home():
    return "<h1>OMEGA SERVER ONLINE</h1><p>Use /log to post data.</p><p><a href='/view'>VIEW LOGS</a></p>"

@app.route('/log', methods=['POST'])
def log_msg():
    data = request.json
    msg = data.get('message', 'No message')
    now = datetime.datetime.now().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('INSERT INTO logs VALUES (?, ?)', (now, msg))
    return jsonify({"status": "ok"})

@app.route('/view')
def view_logs():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC').fetchall()
    html = '<table border="1"><tr><th>Time</th><th>Message</th></tr>'
    for r in rows:
        html += f'<tr><td>{r[0]}</td><td>{r[1]}</td></tr>'
    return html + '</table>'

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
