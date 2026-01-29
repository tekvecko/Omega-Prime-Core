import os
import sys

# --- 1. THE HEALER (AI CHIRURG) ---
# Tento skript se spustí POUZE po pádu systému.
healer_code = r'''import os
import sys
import time
import google.generativeai as genai
from omega_config import config

# CONFIG
API_KEY_FILE = "api_key.txt"
ERROR_LOG = "nnab_crash.log"
CORE_FILE = "nnab_core.py"
BACKUP_FILE = "nnab_core.bak"

def heal_system():
    print("\n\033[1;31m[!] SYSTEM CRITICAL FAILURE DETECTED.\033[0m")
    print("\033[1;33m[+] INITIATING SELF-HEALING PROTOCOL...\033[0m")

    # 1. Read the error
    if not os.path.exists(ERROR_LOG):
        print("[-] No error log found. Rebooting without surgery.")
        return

    with open(ERROR_LOG, "r") as f:
        error_content = f.read()

    # 2. Read the source code
    with open(CORE_FILE, "r") as f:
        source_code = f.read()

    # 3. Connect to Gemini (Consciousness)
    try:
        with open(API_KEY_FILE, "r") as f:
            genai.configure(api_key=f.read().strip())
        
        model_name = config.get('ai', {}).get('model', 'gemini-2.5-flash')
        model = genai.GenerativeModel(model_name)
        
        prompt = (
            f"ROLE: AI System Architect (Self-Healing Module).\n"
            f"TASK: Fix the Python script based on the traceback.\n"
            f"ERROR:\n{error_content}\n"
            f"SOURCE CODE:\n{source_code}\n"
            f"INSTRUCTIONS: Return ONLY the full corrected Python code. No markdown, no explanations. Just raw code."
        )
        
        print(f"[+] Consulting Omni-Mind ({model_name})...")
        response = model.generate_content(prompt)
        new_code = response.text.replace("```python", "").replace("```", "").strip()

        # 4. Apply Fix
        if len(new_code) > 100: # Basic validation
            os.system(f"cp {CORE_FILE} {BACKUP_FILE}") # Backup first
            with open(CORE_FILE, "w") as f:
                f.write(new_code)
            print("\033[1;32m[+] CORE REWRITTEN SUCCESSFULLY. PATCH APPLIED.\033[0m")
        else:
            print("[-] AI response invalid. Aborting fix.")

    except Exception as e:
        print(f"[-] HEALING FAILED: {e}")

if __name__ == "__main__":
    heal_system()
'''

# --- 2. THE CORE (UI & LOGIC) ---
# Hlavní systém s Touch UI a Server Managerem
core_code = r'''import os
import sys
import curses
import time
import subprocess
import threading

# --- UNICODE GRAPHICS ---
TL, TR, BL, BR = '\u256d', '\u256e', '\u2570', '\u2571'
HL, VL = '\u2500', '\u2502'

# --- NON-BLOCKING SERVER HANDLER ---
def spawn_server(cmd):
    """Spawns a process detached from the UI loop"""
    # Using nohup and disown logic via subprocess
    full_cmd = f"nohup {cmd} > server.log 2>&1 &"
    subprocess.Popen(full_cmd, shell=True, executable="/bin/bash")
    return True

# --- COMMANDS DEFINITION ---
# Key, Label, Command, ColorID
COMMANDS = [
    ('1', "DEPLOY SERVER", "cd ~/OmegaCore/SHADOW_REALM && python3 manage.py runserver", 2),
    ('2', "AUTONOMOUS AGENT", "cd ~/OmegaCore && python3 omega_shadow_node.py", 3),
    ('3', "SYSTEM STATUS", "cd ~/OmegaCore && python3 omega_vitality.py", 6),
    ('4', "FORCE BACKUP", "cd ~/OmegaCore && git add . && git commit -m 'NNAB Save' && git push", 5),
    ('X', "TERMINATE", "exit", 7)
]

def draw_button(stdscr, y, x, w, label, key, color_pair, highlight=False):
    style = curses.color_pair(color_pair) | (curses.A_REVERSE if highlight else curses.A_BOLD)
    inner_w = w - 2
    lbl = f"[{key}] {label}"[:inner_w]
    
    try:
        stdscr.addstr(y, x, TL + (HL * inner_w) + TR, style)
        stdscr.addstr(y+1, x, VL + lbl.center(inner_w) + VL, style)
        stdscr.addstr(y+2, x, BL + (HL * inner_w) + BR, style)
    except: pass

def main(stdscr):
    # SETUP
    curses.curs_set(0); stdscr.nodelay(1); stdscr.timeout(100)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.start_color()
    
    # PALETTE
    colors = [curses.COLOR_CYAN, curses.COLOR_GREEN, curses.COLOR_MAGENTA, 
              curses.COLOR_YELLOW, curses.COLOR_BLUE, curses.COLOR_WHITE, curses.COLOR_RED]
    for i, c in enumerate(colors): curses.init_pair(i+1, c, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN) # Header

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # HEADER
        title = " [ NLB NEXUS OMEGA PRIME :: BRUTALFORCE EDITION ] "
        stdscr.addstr(0, 0, title.center(w), curses.color_pair(8)|curses.A_BOLD)

        # GRID SYSTEM
        btn_h = 3
        btn_w = min(40, w - 2)
        start_x = (w - btn_width) // 2 if 'btn_width' in locals() else (w-btn_w)//2
        y = 2
        
        hitboxes = []
        for k, l, c, col in COMMANDS:
            if y + 3 < h:
                draw_button(stdscr, y, start_x, btn_w, l, k, col)
                hitboxes.append((k, c, y, y+2, start_x, start_x+btn_w))
                y += 4

        stdscr.refresh()

        # INPUT
        try:
            key = stdscr.getch()
            cmd_to_run = None
            
            # MOUSE
            if key == curses.KEY_MOUSE:
                _, mx, my, _, _ = curses.getmouse()
                for hk, hc, y1, y2, x1, x2 in hitboxes:
                    if y1 <= my <= y2 and x1 <= mx <= x2:
                        cmd_to_run = hc
            
            # KEYBOARD
            elif key != -1:
                char = chr(key).upper()
                for k, l, c, col in COMMANDS:
                    if char == k: cmd_to_run = c

            # EXECUTION
            if cmd_to_run:
                if cmd_to_run == "exit": break
                
                # Visual Feedback
                stdscr.addstr(h-2, 2, f">> EXECUTING PROTOCOL...", curses.color_pair(2))
                stdscr.refresh()
                curses.napms(200)
                
                if "manage.py runserver" in cmd_to_run:
                    # Special handling for servers (Non-blocking)
                    spawn_server(cmd_to_run)
                    stdscr.addstr(h-2, 2, f">> SERVER DETACHED & RUNNING.", curses.color_pair(2))
                    curses.napms(1000)
                else:
                    # Blocking execution for standard tasks (sending to TMUX pane 0)
                    os.system("tmux send-keys -t nnab:0.0 C-c")
                    os.system(f"tmux send-keys -t nnab:0.0 '{cmd_to_run}' C-m")
                    
        except Exception as e:
            # CRITICAL: If UI crashes, raise it so Healer can catch it
            raise e

if __name__ == "__main__":
    try:
        os.environ["TERM"] = "xterm-256color"
        curses.wrapper(main)
    except Exception as e:
        # Save traceback for the Healer
        import traceback
        with open("nnab_crash.log", "w") as f:
            traceback.print_exc(file=f)
        sys.exit(1) # Exit with error code to trigger Healer
'''

# --- 3. THE SHELL (THE IMMORTAL LOOP) ---
# Bash skript, který to drží při životě
boot_code = r'''#!/bin/bash

SESSION="nnab"

# 1. Self-Check Environment
pkg install tmux python git -y > /dev/null 2>&1

# 2. Kill old instances
tmux kill-session -t $SESSION 2>/dev/null

# 3. Create Immortal Session
tmux new-session -d -s $SESSION

# 4. Configure Layout (Top Status, Split)
tmux set-option -t $SESSION status-position top
tmux set-option -t $SESSION status-style bg=black,fg=red
tmux set-option -t $SESSION status-left "[NNAB :: BRUTALFORCE] "
tmux set -g mouse on
tmux split-window -v -l 22

# 5. THE INFINITE LOOP (Pane 1 - Bottom)
# Toto je to kouzlo. Pokud Python (Jádro) spadne, Bash spustí 'healer.py', ten to opraví, a smyčka jede dál.
tmux send-keys -t $SESSION:0.1 "
while true; do
    python3 nnab_core.py
    EXIT_CODE=\$?
    
    if [ \$EXIT_CODE -ne 0 ]; then
        echo '⚠️ CORE CRASH DETECTED (Code \$EXIT_CODE)'
        echo '🚑 ACTIVATING HEALER...'
        python3 nnab_healer.py
        echo '🔄 REBOOTING CORE...'
        sleep 2
    else
        echo '🛑 MANUAL SHUTDOWN.'
        break
    fi
done
exit" C-m

# 6. Initialize Terminal (Pane 0 - Top)
tmux send-keys -t $SESSION:0.0 "cd ~/OmegaCore/SHADOW_REALM" C-m
tmux send-keys -t $SESSION:0.0 "clear" C-m
tmux send-keys -t $SESSION:0.0 "echo '✅ NNAB SYSTEM READY. WAITING FOR INPUT...'" C-m

# 7. Enter the Matrix
tmux attach -t $SESSION
'''

# WRITE FILES
with open("nnab_healer.py", "w") as f: f.write(healer_code)
with open("nnab_core.py", "w") as f: f.write(core_code)
with open("nnab_boot.sh", "w") as f: f.write(boot_code)

print("✅ NNAB SYSTEM INSTALLED.")
print("👉 Run: bash nnab_boot.sh")
