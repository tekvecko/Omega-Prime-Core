from flask import Flask, request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) # Suppress default Flask logs

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'])
def trap(path):
    ip = request.remote_addr
    method = request.method
    full_path = request.full_path
    headers = dict(request.headers)
    
    print(f"[TRAP] Connection from: {ip}")
    print(f"[TRAP] Method: {method}")
    print(f"[TRAP] Path: {full_path}")
    print(f"[TRAP] Headers: {headers}")
    try:
        data = request.get_data(as_text=True)
        if data:
            print(f"[TRAP] Body:\n{data}")
    except Exception:
        pass # Ignore if body is not text
    print("-" * 40)
    
    return "OK", 200

if __name__ == '__main__':
    print(">>> OMEGA Trap Server running on http://0.0.0.0:8080")
    print(">>> Waiting for connections...")
    app.run(host='0.0.0.0', port=8080)
