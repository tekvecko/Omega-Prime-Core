from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Evo Server is running!"

@app.route('/status')
def status():
    return jsonify({"status": "OK", "version": "1.1"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True) # BG
