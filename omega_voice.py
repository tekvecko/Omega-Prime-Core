import os
import subprocess
import sys

# Konfigurace
USE_VOICE = True  # Změň na False, pokud chceš ticho

def speak(text):
    """Přečte text nahlas pomocí Termux API"""
    if not USE_VOICE:
        return

    # Zkusíme zavolat termux-tts-speak
    try:
        # Použijeme 'nohup' a '&', aby mluvení neblokovalo systém
        subprocess.Popen(
            ["termux-tts-speak", text], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
    except Exception:
        # Pokud API chybí, jen ignorujeme (nebude mluvit)
        pass

if __name__ == "__main__":
    speak("Omega Voice System Online")
