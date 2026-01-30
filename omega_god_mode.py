import os
import sys
import time
import threading
import subprocess
import json
import logging
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

# --- KONFIGURACE ---
HOST_IP = "0.0.0.0"
PORT = 5000
ROOT_DIR = os.path.expanduser("~/OmegaCore")
SHADOW_REALM = os.path.join(ROOT_DIR, "SHADOW_REALM")

# --- GLOBAL STATE ---
system_state = {
    "status": "WAITING_FOR_LINK",
    "cpu_load": 0,
    "active_modules": [],
    "logs": [],
    "connection_verified": False
}

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) # Ticho v konzoli, vše jde do GUI

# --- HTML TEMPLATE (Frontend v roce 2026) ---
HTML_GUI = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMEGA NEXUS // GOD MODE</title>
    <style>
        :root { --neon: #00ff41; --dark: #0d0d0d; --dim: #003b00; --alert: #ff0000; }
        body { background-color: var(--dark); color: var(--neon); font-family: 'Courier New', monospace; margin: 0; padding: 20px; overflow: hidden; }
        #overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--dark); z-index: 99; display: flex; justify-content: center; align-items: center; flex-direction: column; }
        .btn-large { border: 2px solid var(--neon); background: transparent; color: var(--neon); padding: 20px 40px; font-size: 24px; cursor: pointer; text-transform: uppercase; letter-spacing: 2px; transition: 0.3s; }
        .btn-large:hover { background: var(--neon); color: var(--dark); box-shadow: 0 0 20px var(--neon); }
        
        /* Main UI */
        #main-ui { display: none; height: 95vh; display: grid; grid-template-columns: 250px 1fr 300px; gap: 10px; }
        .panel { border: 1px solid var(--dim); padding: 10px; overflow-y: auto; background: rgba(0,20,0,0.3); }
        h3 { border-bottom: 1px solid var(--neon); margin-top: 0; }
        
        .log-entry { margin-bottom: 5px; border-left: 2px solid var(--dim); padding-left: 5px; font-size: 14px; }
        .log-sys { color: #888; }
        .log-chat { color: #fff; }
        
        #chat-input { width: 98%; background: #000; border: 1px solid var(--neon); color: var(--neon); padding: 10px; margin-top: 10px; font-family: monospace; }
        
        .module-card { border: 1px solid #333; padding: 10px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; }
        .status-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; }
        .dot-green { background-color: var(--neon); box-shadow: 0 0 5px var(--neon); }
        .dot-red { background-color: #555; }
    </style>
</head>
<body>

    <div id="overlay">
        <h1>OMEGA PRIME OS [v2026]</h1>
        <p>SECURE CONNECTION REQUIRED</p>
        <button class="btn-large" onclick="verifyConnection()">[ CONFIRM UPLINK ]</button>
    </div>

    <div id="main-ui" style="display:none;">
        <div class="panel">
            <h3>ACTIVE MODULES</h3>
            <div id="module-list">
                <div class="module-card">
                    <span>NEXUS CORE</span> <span class="status-dot dot-green"></span>
                </div>
                <div class="module-card">
                    <span>MERCURY</span> <span id="merc-dot" class="status-dot dot-red"></span>
                </div>
            </div>
            <br>
            <h3>CONTROLS</h3>
            <button onclick="sendCommand('TOGGLE_MERCURY')" style="width:100%; border:1px solid var(--neon); background:black; color:var(--neon); padding:5px; cursor:pointer;">TOGGLE MERCURY</button>
            <br><br>
            <button onclick="sendCommand('CLEAN_LOGS')" style="width:100%; border:1px solid var(--neon); background:black; color:var(--neon); padding:5px; cursor:pointer;">PURGE LOGS</button>
        </div>

        <div class="panel" style="display:flex; flex-direction:column;">
            <h3>TERMINAL / CHAT</h3>
            <div id="console-output" style="flex-grow:1; overflow-y:scroll;"></div>
            <input type="text" id="chat-input" placeholder="Enter command or talk to Omega..." onkeypress="handleInput(event)">
        </div>

        <div class="panel">
            <h3>TELEMETRY</h3>
            <div id="telemetry">Waiting for data...</div>
            <br>
            <h3>FILE SYSTEM</h3>
            <pre id="file-tree" style="font-size:10px;">Loading...</pre>
        </div>
    </div>

    <script>
        // --- 2026 LOGIC ---
        function verifyConnection() {
            fetch('/confirm_connection', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        document.getElementById('overlay').style.display = 'none';
                        document.getElementById('main-ui').style.display = 'grid';
                        startTelemetry();
                    }
                });
        }

        function handleInput(e) {
            if (e.key === 'Enter') {
                let val = document.getElementById('chat-input').value;
                sendCommand(val);
                document.getElementById('chat-input').value = '';
            }
        }

        function sendCommand(cmd) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: cmd})
            });
            // Optimistic update
            addLog("USER", cmd);
        }

        function startTelemetry() {
            setInterval(() => {
                fetch('/api/sync')
                    .then(r => r.json())
                    .then(data => {
                        // Update Logs
                        const consoleDiv = document.getElementById('console-output');
                        consoleDiv.innerHTML = ""; 
                        data.logs.forEach(l => {
                            let color = l.type === 'USER' ? '#fff' : '#00ff41';
                            if (l.type === 'ERROR') color = 'red';
                            consoleDiv.innerHTML += `<div class="log-entry" style="color:${color}">[${l.time}] ${l.msg}</div>`;
                        });
                        consoleDiv.scrollTop = consoleDiv.scrollHeight;

                        // Update Mercury Status
                        let mercDot = document.getElementById('merc-dot');
                        if (data.mercury_active) {
                            mercDot.className = "status-dot dot-green";
                        } else {
                            mercDot.className = "status-dot dot-red";
                        }

                        // Update Telemetry
                        document.getElementById('telemetry').innerText = 
                            `RAM: ${data.ram}MB\nUPTIME: ${data.uptime}s\nSTATUS: ONLINE`;
                            
                        // Files
                        document.getElementById('file-tree').innerText = data.files.join("\\n");
                    });
            }, 1000);
        }

        function addLog(type, msg) {
            // Placeholder for instant feedback
        }
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---

def add_system_log(msg, type="SYSTEM"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    system_state["logs"].append({"time": timestamp, "msg": msg, "type": type})
    # Keep log small
    if len(system_state["logs"]) > 50:
        system_state["logs"].pop(0)

def is_process_running(name):
    try:
        subprocess.check_output(["pgrep", "-f", name])
        return True
    except:
        return False

# --- FLASK ROUTES ---

@app.route('/')
def home():
    return render_template_string(HTML_GUI)

@app.route('/confirm_connection', methods=['POST'])
def confirm():
    system_state["connection_verified"] = True
    system_state["status"] = "CONNECTED"
    add_system_log("User Uplink Verified. God Mode UNLOCKED.", "SUCCESS")
    return jsonify({"success": True})

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    cmd = data.get('command', '')
    
    add_system_log(f"Processing: {cmd}", "USER")
    
    if cmd == "TOGGLE_MERCURY":
        if is_process_running("mercury_daemon.py"):
            os.system("pkill -f mercury_daemon.py")
            add_system_log("Stopping Mercury Agent...", "SYSTEM")
        else:
            os.system("nohup python ~/OmegaCore/mercury_daemon.py > /dev/null 2>&1 &")
            add_system_log("Mercury Agent Launching...", "SYSTEM")
            
    elif cmd == "CLEAN_LOGS":
        system_state["logs"] = []
        add_system_log("Log buffer purged.", "SYSTEM")
        
    else:
        # Generic Shell Command fallback (DANGEROUS but fun for God Mode)
        add_system_log(f"Executing raw command: {cmd}", "SYSTEM")
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            add_system_log(output.decode('utf-8').strip(), "OUTPUT")
        except Exception as e:
            add_system_log(f"Error: {e}", "ERROR")

    return jsonify({"status": "OK"})

@app.route('/api/sync')
def sync_state():
    # Gather real-time stats
    uptime = int(time.time() - start_time)
    merc_active = is_process_running("mercury_daemon.py")
    
    # Get file list
    files = []
    try:
        files = os.listdir(ROOT_DIR)
    except: pass

    return jsonify({
        "logs": system_state["logs"],
        "mercury_active": merc_active,
        "ram": 1024, # Simulace
        "uptime": uptime,
        "files": files
    })

# --- SELF HEAL & BOOT ---
def auto_healer():
    """Pozadí: kontroluje integritu."""
    while True:
        if not os.path.exists(SHADOW_REALM):
            os.makedirs(SHADOW_REALM)
            add_system_log("Shadow Realm recreated by Auto-Healer.", "WARNING")
        time.sleep(10)

if __name__ == "__main__":
    start_time = time.time()
    
    # Start Background Threads
    t = threading.Thread(target=auto_healer)
    t.daemon = True
    t.start()
    
    print(f"\n🔵 OMEGA GOD MODE INITIATED")
    print(f"🔗 OTEVŘI V PROHLÍŽEČI: http://127.0.0.1:{PORT}")
    print(f"⚠️  ČEKÁM NA POTVRZENÍ SPOJENÍ (Klikni na tlačítko na webu)...")
    
    add_system_log("Server initialized. Waiting for user handshake.", "SYSTEM")
    
    app.run(host=HOST_IP, port=PORT, debug=False)
