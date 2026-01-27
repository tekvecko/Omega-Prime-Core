#!/usr/bin/env python3
import sys
import os
import re

# OMEGA HEALER v1.0
# Automatický opravář chyb na základě logů

if len(sys.argv) < 2:
    print("NO_INPUT")
    sys.exit(1)

log_file = sys.argv[1]

try:
    with open(log_file, 'r', errors='replace') as f:
        log_content = f.read()
except FileNotFoundError:
    print("LOG_NOT_FOUND")
    sys.exit(1)

# --- SCÉNÁŘ 1: Hallucinated Library (ThreadingTCPServer) ---
# Detekuje chybu, kdy si AI vymyslí neexistující server
if "AttributeError" in log_content and "'http.server' has no attribute 'ThreadingTCPServer'" in log_content:
    
    # Najde jméno souboru v chybovém výpisu
    match = re.search(r'File "(.*?)", line', log_content)
    if match:
        target_file = match.group(1)
        
        if os.path.exists(target_file):
            with open(target_file, 'r') as f:
                code = f.read()
            
            # Oprava: Nahradí neexistující TCPServer za HTTPServer
            new_code = code.replace("ThreadingTCPServer", "ThreadingHTTPServer")
            
            if code != new_code:
                with open(target_file, 'w') as f:
                    f.write(new_code)
                print(f"FIXED: Opraven 'ThreadingTCPServer' v souboru {os.path.basename(target_file)}")
                sys.exit(0)

print("NO_MATCH")
