#!/usr/bin/env python3
import subprocess
import json
import time
import os
import sys

class OmegaAgent:
    def __init__(self):
        self.logfile = "omega_data.log"

    def _exec(self, cmd, bg=False):
        """Spouští příkazy bezpečně s timeoutem."""
        try:
            if bg:
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return "Proces spuštěn na pozadí."
            
            # Timeout 3s zabrání zaseknutí (Fix pro Timeout Expired)
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
            return res.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Chyba: Proces neodpovídá (Timeout)."
        except Exception as e:
            return f"Chyba: {e}"

    # 1. VITALS: Rychlá telemetrie
    def f_vitals(self):
        raw = self._exec("termux-battery-status")
        try:
            d = json.loads(raw)
            return f"BAT: {d.get('percentage')}% | TEMP: {d.get('temperature')}C | PLUG: {d.get('plugged')}"
        except:
            return "Termux API nedostupné."

    # 2. VOX: Asynchronní TTS
    def f_vox(self):
        self._exec("termux-tts-speak 'Omega system listening'", bg=True)
        return "Audio inicializováno."

    # 3. UPLINK: Rychlý scan sítě
    def f_uplink(self):
        ip = self._exec("ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | head -n 1")
        return f"IP ADDR: {ip}" if ip else "Sít nedostupná."

    # 4. SCRIBE: Logger schránky
    def f_scribe(self):
        txt = self._exec("termux-clipboard-get")
        if txt and "Chyba" not in txt:
            with open(self.logfile, "a") as f:
                f.write(f"[{time.ctime()}] {txt}\n")
            return f"Uloženo ({len(txt)} znaků)."
        return "Schránka prázdná."

    # 5. OPTICS: Kamera (na pozadí, aby neblokovala)
    def f_optics(self):
        fname = f"cam_{int(time.time())}.jpg"
        self._exec(f"termux-camera-photo -c 0 {fname}", bg=True)
        return f"Požadavek na snímek odeslán: {fname}"

    def run(self):
        print("=== OMEGA SYSTEM (Termux Edition) ===")
        print("[1] Vitals  [2] Vox     [3] Uplink")
        print("[4] Scribe  [5] Optics  [0] Exit")
        
        while True:
            try:
                sel = input("\nOMEGA> ").strip()
                if sel == '1': print(self.f_vitals())
                elif sel == '2': print(self.f_vox())
                elif sel == '3': print(self.f_uplink())
                elif sel == '4': print(self.f_scribe())
                elif sel == '5': print(self.f_optics())
                elif sel == '0': break
            except (KeyboardInterrupt, EOFError):
                break

if __name__ == "__main__":
    OmegaAgent().run()
