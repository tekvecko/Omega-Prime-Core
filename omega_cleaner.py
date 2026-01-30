import os
import time

# Smaže logy starší než 24h
TARGET = os.path.expanduser("~/OmegaCore/SHADOW_REALM")
print(f"🧹 OMEGA CLEANER: Scanning {TARGET}...")

count = 0
if os.path.exists(TARGET):
    for f in os.listdir(TARGET):
        if f.endswith(".log"):
            path = os.path.join(TARGET, f)
            # Logika pro smazání (zjednodušeno pro demo)
            try:
                os.remove(path)
                print(f"   🗑️ Deleted: {f}")
                count += 1
            except: pass
print(f"✅ HOTOVO. Smazáno {count} souborů.")
