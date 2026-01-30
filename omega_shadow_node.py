import os
import time
import sys
import random
import json
from datetime import datetime

# Dynamic Path Setup
sys.path.append(os.path.expanduser("~/OmegaCore"))

# Safe Import of Config
try:
    from omega_config import config
except ImportError:
    print("❌ CRITICAL CORE ERROR: Config missing.")
    sys.exit(1)

# Constants
SHADOW_REALM = os.path.expanduser("~/OmegaCore/SHADOW_REALM")
VERSION = config.get('system_version', 1.0)

def log_event(message, level="INFO"):
    """Logs events to console and Shadow Realm."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    print(formatted_msg)
    
    # Gen 2 Capability: Persistent Logging in Shadow Realm
    if level in ["WARNING", "ERROR", "SYSTEM"]:
        try:
            log_path = os.path.join(SHADOW_REALM, "omega_core.log")
            with open(log_path, "a") as f:
                f.write(formatted_msg + "\n")
        except Exception:
            pass # Never crash the core loop due to logging

def core_loop():
    print(f"\n🔵 OMEGA NEXUS v{VERSION} INITIALIZED")
    print("========================================")
    
    if VERSION < 2.0:
        log_event("Running in LEGACY MODE. Upgrade recommended.", "WARNING")
    else:
        log_event("Generation 2 Protocols: ENGAGED", "SYSTEM")

    # The Heartbeat
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            
            # 1. Check Config Updates (Dynamic Reload Simulation)
            current_model = config.get('ai', {}).get('model', 'Unknown')
            
            # 2. Simulated Autonomous Task (Placeholder for future expansion)
            # In Gen 3, this will pull jobs from a queue.
            if cycle_count % 5 == 0:
                log_event(f"Heartbeat Cycle {cycle_count}. Integrity: 100%. Model: {current_model}", "INFO")
                
            # 3. Shadow Realm Maintenance
            if cycle_count % 20 == 0:
                log_event("Performing Shadow Realm cleanup check...", "MAINTENANCE")
                # (Logic to clean old temp files would go here)

            # Sleep to prevent CPU locking
            time.sleep(3)

        except KeyboardInterrupt:
            log_event("User interrupt detected. Shutting down Nexus.", "SYSTEM")
            break
        except Exception as e:
            log_event(f"Unhandled Exception: {e}", "ERROR")
            time.sleep(5) # Cooldown before restart

if __name__ == "__main__":
    # Ensure Shadow Realm exists
    if not os.path.exists(SHADOW_REALM):
        os.makedirs(SHADOW_REALM)
    
    core_loop()
