import os
import curses
import time

# --- UNICODE ZNAKY PRO "ZAOBLENÉ" ROHY ---
TL = '\u256d' # ╭ Top-Left
TR = '\u256e' # ╮ Top-Right
BL = '\u2570' # ╰ Bottom-Left
BR = '\u2571' # ╯ Bottom-Right
HL = '\u2500' # ─ Horizontal Line
VL = '\u2502' # │ Vertical Line

# DEFINICE PŘÍKAZŮ
COMMANDS = [
    ('1', "START SERVER", "cd ~/OmegaCore/SHADOW_REALM && python3 manage.py runserver", 2),
    ('2', "AI AUTONOMY",  "cd ~/OmegaCore && python3 omega_shadow_node.py", 3),
    ('3', "CHECK LOGS",   "cd ~/OmegaCore && python3 omega_logger.py repair", 4),
    ('4', "GIT BACKUP",   "cd ~/OmegaCore && git add . && git commit -m 'RoundSave' && git push", 5),
    ('5', "SYSTEM INFO",  "cd ~/OmegaCore && python3 omega_vitality.py", 6),
    ('C', "CLEAR SCREEN", "clear", 1),
    ('X', "EXIT COCKPIT", "exit", 7)
]

def send_command(cmd):
    os.system("tmux send-keys -t omega:0.0 C-c")
    os.system(f"tmux send-keys -t omega:0.0 '{cmd}' C-m")

def draw_rounded_button(stdscr, y, x, w, label, key, color_pair, highlight=False):
    """Vykreslí 3-řádkové tlačítko se zaoblenými rohy"""
    style = curses.color_pair(color_pair)
    if highlight:
        style = style | curses.A_REVERSE | curses.A_BOLD
    else:
        style = style | curses.A_BOLD

    inner_w = w - 2
    text = f"[{key}] {label}"
    if len(text) > inner_w: text = text[:inner_w] # Ořezání kdyby byl text moc dlouhý

    try:
        # Řádek 1: Horní okraj ╭─────╮
        stdscr.addstr(y, x, TL + (HL * inner_w) + TR, style)
        # Řádek 2: Prostředek s textem │ Text │
        stdscr.addstr(y+1, x, VL + text.center(inner_w) + VL, style)
        # Řádek 3: Spodní okraj ╰─────╯
        stdscr.addstr(y+2, x, BL + (HL * inner_w) + BR, style)
    except curses.error:
        pass

def draw_menu(stdscr):
    # SETUP
    curses.curs_set(0); stdscr.nodelay(1); stdscr.timeout(100); stdscr.keypad(1)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    
    # BARVY
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN)

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        stdscr.addstr(0, 0, " [ OMEGA TOUCH v2 ] ".center(max_x), curses.color_pair(8)|curses.A_BOLD)

        # LAYOUT
        btn_height = 3 # Samotné tlačítko má 3 řádky
        gap = 1        # Mezera mezi nimi
        total_h = btn_height + gap
        
        btn_width = min(38, max_x - 2)
        start_x = (max_x - btn_width) // 2
        start_y = 2
        
        hit_areas = []
        current_y = start_y
        
        for key, label, cmd, color in COMMANDS:
            if current_y + btn_height < max_y:
                draw_rounded_button(stdscr, current_y, start_x, btn_width, label, key, color)
                # Hitbox je nyní vyšší (3 řádky)
                hit_areas.append((key, label, cmd, color, current_y, current_y + btn_height - 1, start_x, start_x + btn_width))
                current_y += total_h

        stdscr.refresh()

        # INPUT LOGIKA
        try:
            key_code = stdscr.getch()
            triggered_cmd = None; triggered_btn = None

            # Klávesnice
            if key_code != -1 and key_code != curses.KEY_MOUSE:
                char = chr(key_code).upper()
                for btn in hit_areas:
                    if char == btn[0]: triggered_cmd = btn[2]; triggered_btn = btn; break

            # Dotyk / Myš
            if key_code == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, _ = curses.getmouse()
                    for btn in hit_areas:
                        # Kontrola jestli dotyk padl do 3-řádkového boxu
                        if btn[4] <= my <= btn[5] and btn[6] <= mx <= btn[7]:
                            triggered_cmd = btn[2]; triggered_btn = btn; break
                except: pass

            # Akce
            if triggered_cmd:
                if triggered_btn:
                    # Vizuální odezva (flash celého boxu)
                    draw_rounded_button(stdscr, triggered_btn[4], triggered_btn[6], btn_width, triggered_btn[1], triggered_btn[0], triggered_btn[3], highlight=True)
                    stdscr.refresh(); curses.napms(150)

                if triggered_cmd == "exit": os.system("tmux kill-session -t omega"); break
                else: send_command(triggered_cmd)
        except: pass

if __name__ == "__main__":
    os.environ["TERM"] = "xterm-256color" # Důležité pro barvy a znaky
    curses.wrapper(draw_menu)
