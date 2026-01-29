import os

# 1. HEALER (Lékař)
healer = r'''import os, sys, google.generativeai as genai
from omega_config import config
API="api_key.txt"; LOG="nnab_crash.log"; CORE="nnab_core.py"
def heal():
 if not os.path.exists(LOG): return
 with open(LOG,"r") as f: err=f.read()
 if not err.strip(): return
 try:
  with open(API,"r") as f: genai.configure(api_key=f.read().strip())
  m=genai.GenerativeModel(config.get('ai',{}).get('model','gemini-2.5-flash'))
  res=m.generate_content(f"Fix Python code based on error:\nERR:\n{err}\nCODE:\n{open(CORE).read()}\nOUT:Raw code only")
  fix=res.text.replace("```python","").replace("```","").strip()
  if len(fix)>50: 
   with open(CORE,"w") as f: f.write(fix)
   print("REPAIRED.")
 except: pass
if __name__=="__main__": heal()
'''

# 2. CORE (Panel)
core = r'''import os, curses, time
CMD=[('1',"SERVER","python3 manage.py runserver"),('2',"SABOTAGE","python3 sabotage.py"),('X',"EXIT","exit")]
def main(s):
 curses.curs_set(0); s.nodelay(1); s.timeout(100); curses.start_color()
 curses.init_pair(1,curses.COLOR_GREEN,0); curses.init_pair(2,0,curses.COLOR_GREEN)
 while True:
  s.clear(); h,w=s.getmaxyx()
  s.addstr(0,0,"[ NNAB SYSTEM ]".center(w),curses.color_pair(2))
  y=2
  for k,l,c in CMD:
   if y<h: s.addstr(y,2,f"[{k}] {l}"); y+=2
  k=s.getch()
  if k!=-1:
   c=chr(k).upper()
   for key,lbl,cmd in CMD:
    if c==key:
     if c=='X': return
     os.system("tmux send-keys -t nnab:0.0 C-c")
     os.system(f"tmux send-keys -t nnab:0.0 '{cmd}' C-m")
     s.addstr(h-1,0,f">> SENT: {lbl}",curses.color_pair(1))
     s.refresh(); curses.napms(200)
if __name__=="__main__": curses.wrapper(main)
'''

# 3. BOOT (Spouštěč)
boot = r'''#!/bin/bash
tmux kill-session -t nnab 2>/dev/null
tmux new-session -d -s nnab
tmux set-option -t nnab status-position top
tmux split-window -v -l 20
tmux send-keys -t nnab:0.1 "while true; do python3 nnab_core.py 2> nnab_crash.log; if [ \$? -ne 0 ]; then python3 nnab_healer.py; sleep 2; else break; fi; done; exit" C-m
tmux send-keys -t nnab:0.0 "cd ~/OmegaCore/SHADOW_REALM; clear; echo SYSTEM READY" C-m
tmux attach -t nnab
'''

with open("nnab_healer.py","w") as f: f.write(healer)
with open("nnab_core.py","w") as f: f.write(core)
with open("nnab_boot.sh","w") as f: f.write(boot)
print("INSTALLED.")

