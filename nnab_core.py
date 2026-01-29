import os, curses, time

# --- KONFIGURACE VZHLEDU ---
TL, TR, BL, BR = '\u256d', '\u256e', '\u2570', '\u2571'
HL, VL = '\u2500', '\u2502'

# --- DEFINICE BAREV ---
# 1=Cyan(Sys), 2=Green(Ok), 3=Red(Exit), 4=Yellow(Net), 5=Magenta(AI), 6=White(Tools)

COMMANDS = [
    ('1', "START SERVER", "find ~/OmegaCore -name manage.py -exec python3 {} runserver 0.0.0.0:8000 \\; -quit", 4),
    ('2', "AI AUTONOMY", "cd ~/OmegaCore && python3 omega_shadow_node.py", 5),
    ('H', "NET HUNTER", "cd ~/OmegaCore && python3 omega_lan_reaper.py", 4),
    ('I', "IP INSPECTOR", "cd ~/OmegaCore && python3 omega_inspector.py", 4),
    ('3', "QUICK FOCUS", "cd ~/OmegaCore && python3 omega_focus.py", 5),
    ('4', "PACKAGE MGR", "cd ~/OmegaCore && python3 omega_packages.py", 6),
    ('5', "WEB DASHBOARD", "cd ~/OmegaCore && python3 server.py", 4),
    ('6', "CODE FACTORY", "cd ~/OmegaCore && python3 omega_factory.py", 6),
    ('7', "LOG REPAIR", "cd ~/OmegaCore && python3 omega_logger.py repair", 1),
    ('8', "SYSTEM CHECK", "cd ~/OmegaCore && python3 omega_vitality.py", 1),
    ('9', "STRESS TEST", "cd ~/OmegaCore && python3 omega_stress_test.py", 1),
    ('0', "GIT BACKUP", "git add . && git commit -m 'OmegaSave' && git push", 6),
    ('X', "EXIT OMEGA", "exit", 3)
]

def draw_btn(s, y, x, w, h, label, key, color_id, is_sel):
    attr = curses.color_pair(2)|curses.A_BOLD if is_sel else curses.color_pair(color_id)|curses.A_BOLD
    try:
        s.addstr(y, x, TL + HL*(w-2) + TR, attr)
        for i in range(1, h-1): s.addstr(y+i, x, VL+" "*(w-2)+VL, attr)
        s.addstr(y+h-1, x, BL + HL*(w-2) + BR, attr)
        
        lbl_x = x + (w - len(label)) // 2
        s.addstr(y+1, x+2, f"[{key}]", attr|curses.A_DIM)
        s.addstr(y+2, lbl_x, label, attr)
        if is_sel: s.addstr(y+1, x+w-4, "●", attr)
    except: pass

def main(s):
    # SETUP
    curses.curs_set(0); s.nodelay(1); s.timeout(100); s.keypad(True)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.start_color()
    
    # PALETA
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    cur = 0
    offset = 0
    needs_redraw = True

    while True:
        if needs_redraw:
            s.erase()
            max_y, max_x = s.getmaxyx()
            s.addstr(0, 0, " [ OMEGA PRIME: INTEGRATED ] ".center(max_x), curses.color_pair(2)|curses.A_BOLD)

            btn_h = 4
            btn_w = min(38, max_x - 2)
            sx = (max_x - btn_w) // 2
            sy = 2
            
            # VÝPOČET SCROLLOVÁNÍ
            visible_count = (max_y - sy) // btn_h
            if visible_count < 1: visible_count = 1
            
            if cur < offset: offset = cur
            if cur >= offset + visible_count: offset = cur - visible_count + 1
            
            visible_cmds = COMMANDS[offset : offset + visible_count]
            
            for i, (k, l, cmd, col) in enumerate(visible_cmds):
                real_idx = offset + i
                y = sy + (i * btn_h)
                draw_btn(s, y, sx, btn_w, btn_h, l, k, col, (real_idx == cur))

            # SCROLL INDICATOR
            if len(COMMANDS) > visible_count:
                more = len(COMMANDS) - offset - visible_count
                msg = f" ▼ {more} MORE " if more > 0 else " ▲ END ▲ "
                try: s.addstr(max_y-1, max_x-len(msg)-1, msg, curses.color_pair(1))
                except: pass

            s.refresh()
            needs_redraw = False

        key = s.getch()

        if key != -1:
            needs_redraw = True
            run = None

            if key == curses.KEY_UP: cur = max(0, cur - 1)
            elif key == curses.KEY_DOWN: cur = min(len(COMMANDS)-1, cur + 1)
            elif key in [10, 13, curses.KEY_ENTER]: run = COMMANDS[cur]
            elif key == curses.KEY_RESIZE: needs_redraw = True
            
            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, _ = curses.getmouse()
                    row = (my - sy) // btn_h
                    if 0 <= row < visible_count:
                        tgt = offset + row
                        if tgt < len(COMMANDS):
                            cur = tgt
                            run = COMMANDS[cur]
                except: pass

            if run:
                k, l, c, col = run
                if k == 'X': break
                
                # FLASH EFEKT
                draw_btn(s, sy+((cur-offset)*btn_h), sx, btn_w, btn_h, l, k, col, True)
                s.refresh()
                curses.napms(150)
                
                # SPUŠTĚNÍ V HORNÍM OKNĚ
                os.system("tmux send-keys -t nnab:0.0 C-c")
                os.system("tmux send-keys -t nnab:0.0 'clear' C-m")
                os.system(f"tmux send-keys -t nnab:0.0 '{c}' C-m")
                
                # FOCUS FIX: Pokud je to Inspektor, musíme přepnout kurzor nahoru, abys mohl psát IP
                if k == 'I' or k == 'H':
                   os.system("tmux select-pane -t nnab:0.0")

if __name__ == "__main__":
    os.environ["TERM"] = "xterm-256color"
    try: curses.wrapper(main)
    except: pass

