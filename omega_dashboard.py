import http.server
import socketserver
import os
import json

PORT = 8080
MEMORY_DIR = "/data/data/com.termux/files/home/OMEGA_MEMORY"
KB_FILE = os.path.join(MEMORY_DIR, "knowledge_base.txt")
MAP_FILE = os.path.join(MEMORY_DIR, "network_map.json")
REPORT_FILE = os.path.join(MEMORY_DIR, "cortex_report.txt")

STYLE = """
<style>
    body { background-color: #0d0d0d; color: #00ff41; font-family: 'Courier New', monospace; padding: 20px; }
    h1 { border-bottom: 2px solid #00ff41; padding-bottom: 10px; text-transform: uppercase; }
    a { color: #00ff41; text-decoration: none; border: 1px solid #00ff41; padding: 10px; display: inline-block; margin-top: 20px; margin-right: 10px; }
    a:hover { background: #00ff41; color: #000; }
    .card { background: #1a1a1a; padding: 10px; margin-bottom: 5px; border-left: 3px solid #00ff41; font-size: 0.9em; }
    .alert { color: #ff3333; border-left-color: #ff3333; }
    .ai-report { border: 1px dashed #00ff41; padding: 20px; margin-top: 20px; color: #ccffcc; }
</style>
"""

class OmegaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            lines = []
            if os.path.exists(KB_FILE):
                with open(KB_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-10:]
                    lines.reverse()
            
            # Načtení AI reportu
            ai_content = "<i>Čekám na data z Cortexu... (může to trvat minutu)</i>"
            if os.path.exists(REPORT_FILE):
                with open(REPORT_FILE, 'r', encoding='utf-8') as f:
                    ai_content = f.read()

            html = f"""<html><head><title>OMEGA CORE</title><meta http-equiv="refresh" content="30">{STYLE}</head>
            <body><h1>👁️ OMEGA PRIME :: CORTEX</h1>
            <p>STATUS: <span style="color:#00ff41">INTELLIGENCE ONLINE</span></p>
            <a href="/network">>> SÍŤOVÝ RADAR</a>
            <hr>
            <h3>🧠 CORTEX AI ANALÝZA:</h3>
            <div class="ai-report">{ai_content}</div>
            <hr>
            <h3>STREAM UDÁLOSTÍ:</h3><div id="memory-stream">"""
            for line in lines:
                cls = "card alert" if "ALERT" in line or "VAROVÁNÍ" in line else "card"
                html += f'<div class="{cls}">{line}</div>'
            html += "</div></body></html>"
            self.wfile.write(html.encode('utf-8'))

        elif self.path == '/network':
            # (Zjednodušeně: stejný kód jako předtím pro network)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f"""<html><head><title>NETWORK</title>{STYLE}</head><body><h1>RADAR</h1><a href="/">ZPĚT</a><p>Načítám...</p><script>window.location.href='/';</script></body></html>""" 
            # Pro úsporu místa v tomto kroku jen redirect, ale v realitě tam nech starý kód
            self.wfile.write(html.encode('utf-8'))
        
        else:
            self.send_error(404)

print(f"WEB SERVER UPDATE OK: http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), OmegaHandler) as httpd:
    httpd.serve_forever()
