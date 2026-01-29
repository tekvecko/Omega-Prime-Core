import os
import sys

# 1. INSTALACE TMUX
print("⏳ [1/3] Instaluji TMUX (Split-screen engine)...")
os.system("pkg install tmux -y > /dev/null 2>&1")

# 2. VYTVOŘENÍ PANELU
print("⏳ [2/3] Generuji Omega Panel...")
panel_code = r"""
import os
import curses

COMMANDS = {
    '1': ("Start Server", "cd ~/OmegaCore/SHADOW_REALM && python3 manage.py runserver"),
    '2': ("AI Autonomy", "cd ~/OmegaCore && python3 omega_shadow_node.py"),
    '3': ("Check Logs", "cd ~/OmegaCore && python3 omega_logger.py repair"),
    '4': ("Git Backup", "cd ~/OmegaCore && git add . && git commit -m 'QuickSave' && git push"),
    'x': ("EXIT", "exit"),
    'c': ("Clear Top", "clear"),
}

def send_command(cmd):
    os.system("tmux send-keys -t omega:0.0 C-c")
    os.system(f"tmux send-keys -t omega:0.0 '{cmd}' C-m")

def draw_menu(stdscr):
    curses.curs_set(0); stdscr.nodelay(1); stdscr.timeout(100)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(0, 2, " [ OMEGA PRIME COCKPIT ] ", curses.color_pair(2))
        
        y, x = 2, 2
        for key, (lbl, _) in COMMANDS.items():
            if x + len(lbl) + 10 > w: y+=1; x=2
            stdscr.addstr(y, x, f"[{key.upper()}] {lbl}", curses.color_pair(1))
            x += len(lbl) + 8
            
        stdscr.refresh()
        try:
            key = stdscr.getkey()
            if key == 'x': os.system("tmux kill-session -t omega"); break
            if key in COMMANDS: send_command(COMMANDS[key][1])
        except: pass

if __name__ == "__main__":
    curses.wrapper(draw_menu)
"""
with open("omega_panel.py", "w") as f:
    f.write(panel_code.strip())

# 3. AKTUALIZACE GONEXUS
print("⏳ [3/3] Přepisuji spouštěč gonexus...")
gonexus_path = os.path.join(os.environ["PREFIX"], "bin", "gonexus")
launcher_code = """#!/bin/bash
tmux kill-session -t omega 2>/dev/null
tmux new-session -d -s omega
tmux split-window -v -l 10
tmux send-keys -t omega:0.1 "python3 ~/OmegaCore/omega_panel.py" C-m
tmux send-keys -t omega:0.0 "cd ~/OmegaCore/SHADOW_REALM" C-m
tmux send-keys -t omega:0.0 "clear" C-m
tmux send-keys -t omega:0.0 "echo '✅ OMEGA COCKPIT ONLINE.'" C-m
tmux attach -t omega
"""
with open(gonexus_path, "w") as f:
    f.write(launcher_code)

os.system(f"chmod +x {gonexus_path}")

print("\n✅ HOTOVO. Rozhraní je nainstalováno.")
print("👉 Napiš: gonexus")
