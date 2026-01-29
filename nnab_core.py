import os, curses, time

# --- KONFIGURACE ---
TL, TR, BL, BR = '\u256d', '\u256e', '\u2570', '\u2571'
HL, VL = '\u2500', '\u2502'

MENUS = {
    "MAIN": [
        ('1', "NET HUNTER", "SUB:NET", 4),
        ('2', "AI CORE", "SUB:AI", 5),
        ('3', "TOOLS", "SUB:TOOLS", 6),
        ('4', "SERVER", "SUB:SERVER", 2),
        ('5', "SCRIPT RUNNER", "SELECT_SCRIPT", 4),
        ('X', "EXIT", "EXIT", 3)
    ],
    "NET": [
        ('1', "SCAN LAN", "CMD:python3 omega_lan_reaper.py", 4),
        ('2', "INSPECT IP", "INP:IP Adresa:|python3 omega_inspector.py {}", 4),
        ('3', "PING GOOGLE", "CMD:ping -c 3 8.8.8.8", 4),
        ('B', "BACK", "BACK", 3)
    ],
    "AI": [
        ('1', "AUTONOMY", "CMD:python3 omega_shadow_node.py", 5),
        ('2', "FOCUS TASK", "CMD:python3 omega_focus.py", 5),
        ('B', "BACK", "BACK", 3)
    ],
    "TOOLS": [
        ('1', "PACKAGES", "SUB:PKG", 6),
        ('2', "FACTORY", "CMD:python3 omega_factory.py", 6),
        ('3', "GIT BACKUP", "CMD:git add . && git commit -m 'Save' && git push", 6),
        ('8', "SYS CHECK", "CMD:python3 omega_vitality.py", 1),
        ('B', "BACK", "BACK", 3)
    ],
    "PKG": [
        ('1', "SEARCH", "INP:Hledat:|pkg search {}", 6),
        ('2', "INSTALL", "INP:Instalovat:|pkg install -y {}", 2),
        ('3', "UPDATE", "CMD:pkg update -y && pkg upgrade -y", 6),
        ('4', "PIP INSTALL", "INP:Pip Package:|pip install {}", 5),
        ('B', "BACK", "BACK", 3)
    ],
    "SERVER": [
        ('1', "START WEB", "CMD:find ~/OmegaCore -name manage.py -exec python3 {} runserver 0.0.0.0:8000 \\; -quit", 2),
        ('2', "DASHBOARD", "CMD:python3 server.py", 4),
        ('B', "BACK", "BACK", 3)
    ]
}

def draw_btn(s, y, x, w, label, key, color_id, is_sel):
    attr = curses.color_pair(2)|curses.A_BOLD if is_sel else curses.color_pair(color_id)|curses.A_BOLD
    try:
        s.addstr(y, x, TL + HL*(w-2) + TR, attr)
        lbl_len = w - 6; clean = label[:lbl_len].center(lbl_len)
        s.addstr(y+1, x, VL, attr)
        s.addstr(y+1, x+2, f"[{key}]", attr|curses.A_DIM)
        s.addstr(y+1, x+w-len(clean)-2, clean, attr)
        s.addstr(y+1, x+w-1, VL, attr)
        s.addstr(y+2, x, BL + HL*(w-2) + BR, attr)
        if is_sel: s.addstr(y+1, x+w-2, "◄", attr|curses.A_BLINK)
    except: pass

def get_input(s, prompt):
    try:
        h, w = s.getmaxyx()
        if h < 4: return ""
        curses.echo(); curses.curs_set(1)
        bx, by = w//2 - 15, h//2 - 2
        s.attron(curses.color_pair(2)); s.border()
        s.addstr(by, bx+2, prompt)
        inp = s.getstr(by+1, bx+2, 20).decode()
        curses.noecho(); curses.curs_set(0)
        return inp
    except:
        curses.noecho(); curses.curs_set(0)
        return ""

def show_file_selector(s):
    path = os.path.expanduser("~/OmegaCore")
    try:
        files = [f for f in os.listdir(path) if f.endswith(".py") and not f.startswith("nnab_")]
        files.sort()
    except: files = []
    if not files: return None

    sel = 0
    s.nodelay(0)
    
    while True:
        try:
            h, w = s.getmaxyx()
            if h < 10: raise Exception("Small")
            
            box_w = min(40, w-4); box_h = min(15, h-4)
            by, bx = (h-box_h)//2, (w-box_w)//2
            
            s.erase()
            s.attron(curses.color_pair(6)); s.border()
            s.addstr(by, bx+2, f" [ SPUSTIT SKRIPT ] ", curses.color_pair(4)|curses.A_BOLD)
            
            for i, f in enumerate(files):
                if i >= box_h-2: break
                style = curses.color_pair(2)|curses.A_REVERSE if i == sel else curses.color_pair(6)
                s.addstr(by+i+1, bx+2, f" {f[:30]} ".ljust(box_w-4), style)
                
            s.refresh()
            k = s.getch()
            
            if k == curses.KEY_UP: sel = max(0, sel - 1)
            elif k == curses.KEY_DOWN: sel = min(len(files)-1, sel + 1)
            elif k in [10, 13]: s.nodelay(1); return files[sel]
            elif k == 27: s.nodelay(1); return None
            elif k == curses.KEY_RESIZE: continue
        except:
            s.erase(); s.addstr(0,0,"OTOČ TELEFON"); s.refresh(); time.sleep(0.5)

def main(s):
    curses.curs_set(0); s.nodelay(1); s.timeout(100); s.keypad(True)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.start_color()
    for i, c in enumerate([curses.COLOR_CYAN, curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_MAGENTA, curses.COLOR_WHITE]):
        curses.init_pair(i+1, c, curses.COLOR_BLACK)

    stack = ["MAIN"]; cur = 0
    
    while True:
        try:
            h, w = s.getmaxyx()
            if h < 5 or w < 20:
                s.erase(); s.addstr(0, 0, " PAUSED ", curses.color_pair(3)|curses.A_REVERSE); s.refresh(); time.sleep(0.2); continue

            mid = stack[-1]; items = MENUS.get(mid, MENUS["MAIN"])
            s.erase()
            s.addstr(0, 1, f" OMEGA: {mid} ", curses.color_pair(4)|curses.A_BOLD)
            
            bh = 3; bw = min(24, (w//2)-2) if w > 50 else w-4
            cc = 2 if w > 50 else 1
            sy = 2; sx = (w - (cc*bw)) // 2
            
            for i, (k, l, cmd, col) in enumerate(items):
                r, c = i//cc, i%cc
                y, x = sy + r*bh, sx + c*(bw+2)
                if y+bh < h: draw_btn(s, y, x, bw, l, k, col, (i==cur))

            s.refresh()
            k = s.getch(); act = None
            
            if k==curses.KEY_UP: cur=max(0, cur-cc)
            elif k==curses.KEY_DOWN: cur=min(len(items)-1, cur+cc)
            elif k==curses.KEY_LEFT: cur=max(0, cur-1)
            elif k==curses.KEY_RIGHT: cur=min(len(items)-1, cur+1)
            elif k in [10,13]: act=items[cur]
            elif k==curses.KEY_MOUSE:
                try:
                    _,mx,my,_,_=curses.getmouse()
                    for i in range(len(items)):
                        r,c=i//cc,i%cc; by,bx=sy+r*bh,sx+c*(bw+2)
                        if by<=my<by+bh and bx<=mx<bx+bw: cur=i; act=items[cur]
                except: pass
                
            if act:
                _, l, a, _ = act
                if h > 5:
                    r,c=cur//cc,cur%cc; draw_btn(s, sy+r*bh, sx+c*(bw+2), bw, l, act[0], 2, True)
                    s.refresh(); curses.napms(100)
                
                p, d = a.split(':', 1) if ':' in a else (a, "")
                
                if p=="EXIT": break
                elif p=="BACK": 
                    if len(stack)>1: stack.pop(); cur=0
                elif p=="SUB": stack.append(d); cur=0
                
                # --- VYLEPŠENÉ SPUŠTĚNÍ SKRIPTŮ ---
                elif p=="SELECT_SCRIPT":
                    scr = show_file_selector(s)
                    if scr:
                        # 1. CD do správné složky
                        # 2. Hezká hlavička
                        # 3. Spuštění
                        # 4. Pauza na čtení (read)
                        cmd = (
                            f"cd ~/OmegaCore && "
                            f"echo -e '\\n\\033[1;33m[OMEGA] SPOUŠTÍM: {scr}...\\033[0m' && "
                            f"echo '--------------------------------' && "
                            f"python3 {scr}; "
                            f"echo -e '\\n--------------------------------'; "
                            f"echo -e '\\033[1;32m[HOTOVO] Stiskni ENTER pro návrat...\\033[0m'; "
                            f"read"
                        )
                        os.system("tmux send-keys -t nnab:0.0 C-c 'clear' C-m")
                        os.system(f"tmux send-keys -t nnab:0.0 \"{cmd}\" C-m")
                
                elif p=="CMD":
                    # Také přidáme pauzu pro běžné příkazy, abys viděl výsledek
                    f_cmd = d if "cd " in d else f"cd ~/OmegaCore && {d}"
                    full_cmd = f"{f_cmd}; echo -e '\\n\\033[1;30m[ENTER = ZPĚT]\\033[0m'; read"
                    
                    os.system("tmux send-keys -t nnab:0.0 C-c 'clear' C-m")
                    os.system(f"tmux send-keys -t nnab:0.0 \"{full_cmd}\" C-m")
                    
                elif p=="INP":
                    pr, cm = d.split('|'); s.nodelay(0)
                    v = get_input(s, pr); s.nodelay(1)
                    if v:
                        fin = cm.replace("{}", v)
                        # I zde přidáme pauzu
                        cmd_wait = f"cd ~/OmegaCore && {fin}; echo -e '\\n[ENTER]'; read"
                        os.system(f"tmux send-keys -t nnab:0.0 \"{cmd_wait}\" C-m")

        except Exception as e: pass

if __name__ == "__main__":
    os.environ["TERM"] = "xterm-256color"
    try: curses.wrapper(main)
    except: pass
