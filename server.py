
from flask import Flask

# Vytvoření instance Flask aplikace
app = Flask(__name__)

# Definice hlavní (root) cesty '/'
@app.route('/')
def omega_home():
    return "OMEGA SERVER IS RUNNING"

# Spuštění serveru, pokud je skript spuštěn přímo
if __name__ == '__main__':
    # '0.0.0.0' zpřístupní server zvenčí kontejneru/stroje
    app.run(host='0.0.0.0', port=5000)
