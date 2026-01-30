import json
import os
import time
import subprocess
from datetime import datetime

RULES_PATH = os.path.expanduser("~/OmegaCore/omega_rules.json")

class OmegaPolicy:
    def __init__(self):
        self.last_load = 0
        self.rules = {}
        self.refresh_rules()

    def refresh_rules(self):
        """Načte pravidla znovu, pokud se soubor změnil."""
        try:
            if os.path.exists(RULES_PATH):
                mtime = os.path.getmtime(RULES_PATH)
                if mtime > self.last_load:
                    with open(RULES_PATH, 'r') as f:
                        self.rules = json.load(f)
                    self.last_load = mtime
                    # print("   [POLICY] Rules updated from Codex.")
        except Exception as e:
            print(f"   [POLICY ERROR] Failed to load rules: {e}")

    def get_battery_level(self):
        """Získá stav baterie z Termux API (pokud je dostupné)."""
        try:
            result = subprocess.check_output(["termux-battery-status"], stderr=subprocess.DEVNULL)
            data = json.loads(result)
            return data.get("percentage", 100)
        except:
            return 100 # Pokud API nejde, předpokládáme 100%

    def can_run(self, module_name):
        """Hlavní rozhodovací funkce."""
        self.refresh_rules()
        
        # 1. Globální Kill-Switch
        if self.rules.get("global_system", {}).get("status") != "ACTIVE":
            return False, "GLOBAL_LOCKDOWN"

        # 2. Kontrola Baterie
        min_batt = self.rules["global_system"].get("min_battery_percent", 15)
        current_batt = self.get_battery_level()
        if current_batt < min_batt:
            return False, f"LOW_BATTERY ({current_batt}%)"

        # 3. Noční klid (Silent Hours)
        now_hour = datetime.now().hour
        start = self.rules["global_system"].get("silent_hours_start", 23)
        end = self.rules["global_system"].get("silent_hours_end", 6)
        
        # Logika pro čas přes půlnoc
        is_silent = False
        if start > end:
            if now_hour >= start or now_hour < end: is_silent = True
        else:
            if start <= now_hour < end: is_silent = True
            
        if is_silent:
            # Zde bychom mohli povolit výjimky, pro teď blokujeme
            pass 
            # return False, "SILENT_HOURS" (Vypnuto pro demo, odkomentuj pro aktivaci)

        # 4. Modulová oprávnění
        mod_rules = self.rules.get("modules", {}).get(module_name, {})
        if not mod_rules.get("allowed", True):
            return False, "MODULE_DISABLED"

        return True, "AUTHORIZED"

    def get_setting(self, module_name, key, default=None):
        """Získá specifické nastavení pro modul."""
        self.refresh_rules()
        return self.rules.get("modules", {}).get(module_name, {}).get(key, default)

# Singleton instance
policy = OmegaPolicy()
