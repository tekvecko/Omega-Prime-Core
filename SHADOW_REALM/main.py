
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Načtení proměnných prostředí
load_dotenv()

# Konfigurace API klíče
try:
    genai.configure(api_key=os.environ["API_KEY"])
except KeyError:
    print("Chyba: API_KEY není nastaven v prostředí. Vytvořte .env soubor s obsahem API_KEY='VÁŠ_KLÍČ'")
    exit()

# Vytvoření modelu
model = genai.GenerativeModel('gemini-pro')

# Generování obsahu
prompt = "Explain the importance of switching from the PaLM API to the Gemini API."
response = model.generate_content(prompt)

# Tisk výsledku
print(response.text)
