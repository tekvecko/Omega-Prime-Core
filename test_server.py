from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Server is running!'

@app.route('/api/data')
def get_data():
    payload = {
        'id': 42,
        'user': 'OMEGA',
        'status': 'operational'
    }
    return jsonify(payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
