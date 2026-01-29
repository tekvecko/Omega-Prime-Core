
import subprocess
import sys
import os

# Cílový adresář
target_dir = "/data/data/com.termux/files/home/OmegaCore/SHADOW_REALM"
os.chdir(target_dir)

# Analýza: Kód v main.py již používá nový 'google.genai' syntax.
# 'requirements.txt' neomezuje verzi.
# Úkolem je nyní zajistit, že prostředí je aktuální a kód je funkční.

# Krok 3: Aktualizace balíčků podle requirements.txt, zejména 'google-generativeai'.
print("--- Aktualizace balíčku google-generativeai na nejnovější verzi ---")

# Použití sys.executable -m pip je robustnější způsob
command = [sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai"]
result = subprocess.run(command, capture_output=True, text=True, check=False)

if result.returncode == 0:
    print(result.stdout)
    print("--- Balíček google-generativeai byl úspěšně aktualizován. ---")
else:
    print("--- Chyba při aktualizaci balíčku: ---")
    print(result.stderr)

print("\n--- Analýza: Prostředí je připraveno. Další krok: spuštění main.py pro ověření funkčnosti s novým API. ---")

