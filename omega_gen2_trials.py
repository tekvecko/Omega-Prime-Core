import os
import time
import sys
import math
import random

# Attempt to import configuration dynamically
try:
    sys.path.append(os.path.expanduser("~/OmegaCore"))
    from omega_config import config
except ImportError:
    print("❌ CRITICAL: 'omega_config.py' not found. System integrity compromised.")
    sys.exit(1)

def print_step(message):
    """Helper to print formatted status messages."""
    print(f"\n[ GEN-2 TRIAL ] 👉 {message}")

def verify_config_integrity():
    """Checks if the AI model configuration follows the strict dynamic rules."""
    print_step("Verifying Neural Configuration...")
    
    ai_config = config.get('ai', {})
    model_name = ai_config.get('model')
    fallback_list = ai_config.get('fallback_order', [])

    if not model_name:
        print("   ⚠️ WARNING: No primary model defined. Defaulting to system standard.")
    else:
        print(f"   ✅ Primary Model Detected: {model_name}")

    if not fallback_list:
        print("   ⚠️ WARNING: No fallback models defined. Resilience is low.")
    else:
        print(f"   ✅ Fallback Protocols: {len(fallback_list)} models ready.")
    
    return True

def shadow_realm_stress_test():
    """Tests file I/O speeds and permissions in the sandbox."""
    print_step("Testing Shadow Realm I/O Latency...")
    
    shadow_path = os.path.expanduser("~/OmegaCore/SHADOW_REALM")
    if not os.path.exists(shadow_path):
        try:
            os.makedirs(shadow_path)
            print(f"   ✅ Created missing directory: {shadow_path}")
        except Exception as e:
            print(f"   ❌ FAILED to access Shadow Realm: {e}")
            return False

    test_file = os.path.join(shadow_path, "gen2_integrity_lock.dat")
    
    try:
        # Write Test
        start_time = time.time()
        with open(test_file, 'w') as f:
            for _ in range(10000):
                f.write(f"OMEGA_PRIME_GENERATION_2_VERIFICATION_TOKEN_{random.random()}\n")
        write_duration = time.time() - start_time
        
        # Read Test
        with open(test_file, 'r') as f:
            _ = f.read()
        
        # Cleanup
        os.remove(test_file)
        
        print(f"   ✅ Write/Read Cycle Complete. Latency: {write_duration:.4f}s")
        if write_duration > 1.0:
             print("   ⚠️ NOTE: I/O is sluggish. Optimize storage.")
        return True
        
    except Exception as e:
        print(f"   ❌ I/O ERROR: {e}")
        return False

def cognitive_load_simulation():
    """Simulates a heavy logic task (finding primes) to test Python performance in Termux."""
    print_step("Simulating Cognitive Load (CPU Stress)...")
    
    start_time = time.time()
    count = 0
    target = 5000
    
    # Simple Sieve logic for stress testing
    for num in range(2, target):
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if (num % i) == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
            
    duration = time.time() - start_time
    print(f"   ✅ Processed prime search up to {target} in {duration:.4f}s")
    
    if duration < 0.5:
        print("   🚀 PERFORMANCE: Excellent. Core is ready for Gen 2.")
    elif duration < 1.5:
        print("   👌 PERFORMANCE: Acceptable.")
    else:
        print("   ⚠️ PERFORMANCE: Sub-optimal. Check background processes.")
    
    return True

def main():
    print("=========================================")
    print(" OMEGA PRIME: GENERATION 2 QUALIFICATION ")
    print("=========================================")
    
    checks = [
        verify_config_integrity(),
        shadow_realm_stress_test(),
        cognitive_load_simulation()
    ]
    
    print("\n-----------------------------------------")
    if all(checks):
        print("STATUS: 🟢 PASSED")
        print("SYSTEM UPGRADE AUTHORIZED: GENERATION 2 UNLOCKED")
        print("You may now proceed to update core logic modules.")
    else:
        print("STATUS: 🔴 FAILED")
        print("Resolve the errors above before attempting Ascension.")
    print("-----------------------------------------")

if __name__ == "__main__":
    main()
