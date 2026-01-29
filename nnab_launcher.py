import os, time, subprocess

def loop():
    while True:
        print("\033[1;34m[LAUNCHER] Startuji OMEGA Jádro...\033[0m")
        # Spustí jádro a čeká na výsledek
        exit_code = os.system("python3 nnab_core.py 2> nnab_crash.log")
        
        if exit_code != 0:
            print(f"\033[1;31m⚠️ CRASH DETECTED (Code {exit_code})\033[0m")
            # Spustí lékaře
            os.system("python3 nnab_healer.py")
            time.sleep(2)
        else:
            print("[LAUNCHER] Systém ukončen uživatelem.")
            break

if __name__ == "__main__":
    loop()
