from flask import Flask

# Vytvoření instance aplikace Flask
app = Flask(__name__)

# Definice základní cesty (route)
@app.route('/')
def home():
    # Změněný text odpovědi
    return "Hot-Reload funguje! Server se sám aktualizoval. 🔥"

# Spuštění serveru
if __name__ == '__main__':
    # Spustí server na portu 5000 s aktivním debug režimem
    app.run(host='0.0.0.0', port=5000, debug=True)
