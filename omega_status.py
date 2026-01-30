import os
import sys

# Dynamic import setup
sys.path.append(os.path.expanduser("~/OmegaCore"))

try:
    from omega_config import config
except ImportError:
    print("❌ Critical: Config not found.")
    sys.exit(1)

def check_status():
    version = config.get('system_version', 1.0)
    codename = config.get('codename', 'Unknown')
    caps = config.get('gen2_capabilities', [])
    
    print("\n🖥️  OMEGA PRIME SYSTEM STATUS")
    print("=============================")
    print(f"🔹 Version:    {version}")
    print(f"🔹 Codename:   {codename}")
    print(f"🔹 Model:      {config.get('ai', {}).get('model', 'Unknown')}")
    
    if version >= 2.0:
        print("\n🚀 GENERATION 2 ACTIVE")
        print(f"   Capabilities Loaded: {len(caps)}")
        for cap in caps:
            print(f"   - {cap}")
    else:
        print("\n⚠️  Running in LEGACY mode (Gen 1)")

if __name__ == "__main__":
    check_status()
