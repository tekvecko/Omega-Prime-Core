import os, sys, subprocess, re, time, shutil, datetime, getpass, select, signal

# --- ZÁVISLOSTI ---
try:
    import google.generativeai as genai
    from omega_config import config
except ImportError:
    try: from omega_config import config
    except: config = {}

# --- KONFIGURACE ---
MODEL_NAME = config.get('ai', {}).get('model', 'gemini-2.5-flash')
API_KEY = config.get('api', {}).get('key')
if not API_KEY and os.path.exists("api_key.txt"):
    with open("api_key.txt", "r") as f: API_KEY = f.read().strip()
if not API_KEY: sys.exit("CRITICAL: Chybí API KEY.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# --- GLOBAL ---
CONTEXT = []
AUTONOMY = False
MAX_AUTO_STEPS = 15
JOBS = {}
LAST_CMD = ""
LOG_DIR = "nexus_logs"
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

# --- BARVY ---
R, G, Y, C, M, W, X = "\033[1;31m", "\033[1;32m", "\033[1;33m", "\033[1;36m", "\033[1;35m", "\033[1;37m", "\033[0m"

def print_banner():
    os.system("clear")
    print(f"{C}╔════════════════════════════════════════════╗{X}")
    print(f"{C}║  OMEGA NEXUS v11.0: ANTI-LOOP PROTOCOL     ║{X}")
    print(f"{C}╚════════════════════════════════════════════╝{X}")
    act_jobs = sum(1 for j in JOBS.values() if j['proc'].poll() is None)
    print(f" JOBS: {G if act_jobs>0 else C}{act_jobs}{X} running | AI: {MODEL_NAME}")
    print(f"{C}──────────────────────────────────────────────{X}\n")

# --- PROCESS ENGINE ---
def run_background(cmd_list):
    jid = len(JOBS) + 1
    log = os.path.join(LOG_DIR, f"job_{jid}.log")
    try:
        f = open(log, "w")
        env = os.environ.copy(); env["PYTHONUNBUFFERED"] = "1"
        p = subprocess.Popen(cmd_list, stdout=f, stderr=subprocess.STDOUT, text=True, cwd=os.getcwd(), env=env)
        JOBS[jid] = {"proc": p, "log": f, "cmd": " ".join(cmd_list)}
        time.sleep(0.5)
        if p.poll() is not None: return True, jid, "DONE"
        return True, jid, "RUNNING"
    except Exception as e: return False, str(e), "ERR"

def run_realtime(cmd_list):
    master, slave = os.openpty()
    try:
        p = subprocess.Popen(cmd_list, stdout=slave, stderr=slave, close_fds=True, text=True)
        os.close(slave)
        out_log = []
        while True:
            try:
                r, _, _ = select.select([master], [], [], 0.1)
                if r:
                    d = os.read(master, 1024).decode(errors='replace')
                    if not d: break
                    print(d, end='', flush=True)
                    out_log.append(d)
                elif p.poll() is not None: break
            except: break
        p.wait()
        return p.returncode, "".join(out_log)
    except Exception as e:
        os.close(master)
        return 1, str(e)

# --- DETEKCE SERVERU ---
def is_server_command(code):
    code = code.lower()
    blocking_keywords = ["flask run", "run_server", "http.server", "uvicorn", "gunicorn", "# bg"]
    if any(k in code for k in blocking_keywords): return True
    if "python" in code and "server.py" in code: return True
    return False

# --- AI BRAIN (ANTI-LOOP LOGIC) ---
def ai_think(prompt, mode="NORMAL"):
    global CONTEXT
    print(f"\n{C}{'-'*20} OMEGA PŘEMÝŠLÍ {'-'*20}{X}")
    
    # SYSTEM PROMPT S PRAVIDLEM PROTI SMYČKÁM
    base = """
    Jsi OMEGA (Termux Automation).
    PRAVIDLA:
    1. Generuj POUZE spustitelný kód. Žádné texty do bloků kódu.
    2. Servery spouštěj VŽDY na pozadí (# BG).
    
    CRITICAL PROTOCOL (ANTI-LOOP):
    3. Pokud provedeš test (curl) a ten projde (vrátí data/200 OK), NESMÍŠ ho opakovat.
    4. Jakmile server běží a je otestován, napiš pouze "MISSION COMPLETE" a negeneruj žádný kód.
    5. NEVYMÝŠLEJ si nové endpointy pro testování, pokud to nebylo v zadání.
    """
    
    if mode == "FEEDBACK": sys_msg = base + "Analyzuj výsledek. Pokud je výsledek OK, ukonči práci."
    elif mode == "TASK": sys_msg = base + "Jsi ARCHITEKT. Proveď úkol efektivně. Testuj jen JEDNOU."
    else: sys_msg = base

    if len(CONTEXT) > 8: CONTEXT = CONTEXT[-8:]
    msgs = [{'role': 'user', 'parts': [sys_msg]}] + CONTEXT + [{'role': 'user', 'parts': [prompt]}]
    try:
        resp = model.generate_content(msgs).text
        if mode != "FEEDBACK":
            CONTEXT.append({'role': 'user', 'parts': [prompt]})
            CONTEXT.append({'role': 'model', 'parts': [resp]})
        return resp
    except: return "AI Error"

# --- AGENT LOOP ---
def agent_loop(init_prompt):
    global LAST_CMD
    curr_prompt = init_prompt
    is_feedback = False
    steps = 0
    
    while True:
        resp = ai_think(curr_prompt, mode="FEEDBACK" if is_feedback else "TASK")
        
        # Detekce konce
        if "MISSION COMPLETE" in resp or "DOKONČENO" in resp:
            print(f"\n{G}>>> OMEGA HLÁSÍ HOTOVO.{X}")
            print(f"{C}AI:{X} {resp}")
            break

        print(f"\n{C}PLÁN:{X}\n{resp}")
        
        blocks = re.findall(r"```(bash|python|sh)?\n(.*?)```", resp, re.DOTALL)
        if not blocks:
            print(f"\n{G}>>> ŽÁDNÝ DALŠÍ KÓD (KONEC).{X}"); break
            
        steps += 1
        if steps > MAX_AUTO_STEPS: break
        
        exec_results = []
        for lang, code in blocks:
            # 1. Filtr halucinací
            if "HTTP/1.1" in code or "Error:" in code[:20]: continue
            
            # 2. Filtr smyček (Deduplikace)
            if code.strip() == LAST_CMD:
                print(f"{R}⚠ DETEKOVÁNA SMYČKA (Opakovaný příkaz). Ukončuji autonomii.{X}")
                return # Konec smyčky
            LAST_CMD = code.strip()

            lang = lang.strip().lower() or "bash"
            print(f"\n{Y}>>> KROK {steps}: {lang}{X}")
            
            # --- THE ENFORCER ---
            must_be_bg = is_server_command(code)
            
            act = 'y'
            if not AUTONOMY:
                if must_be_bg:
                    print(f"{M}⚠ DETEKOVÁN SERVER -> VYNUCUJI POZADÍ{X}")
                    act = 'b'
                    time.sleep(1)
                else:
                    act = input(f"{W}[Enter]=Run | [b]=BG | [n]=Skip: {X}").lower()
            
            if act == 'n': continue
            is_bg = (act == 'b') or (must_be_bg and AUTONOMY)
            
            if "python" in lang:
                with open("omega_staging.py", "w") as f: f.write(code)
                cmd = ['python3', 'omega_staging.py']
            else:
                cmd = ['/data/data/com.termux/files/usr/bin/bash', '-c', code]

            if is_bg:
                ok, jid, status = run_background(cmd)
                if status == "RUNNING":
                    msg = f"Server běží na pozadí (Job {jid})."
                    print(f"{G}✔ {msg}{X}")
                    time.sleep(2)
                else:
                    msg = f"Úloha dokončena (Job {jid})."
                    print(f"{G}✔ {msg}{X}")
                exec_results.append(msg)
            else:
                rc, out = run_realtime(cmd)
                status = "OK" if rc == 0 else f"ERR {rc}"
                exec_results.append(f"Status: {status}\nOut:\n{out[-800:]}")

        curr_prompt = "VÝSLEDKY:\n" + "\n".join(exec_results) + "\nPokud je Status: OK, napiš MISSION COMPLETE. Jinak pokračuj."
        is_feedback = True

def main():
    global AUTONOMY
    print_banner()
    while True:
        try:
            p = input(f"\n{G}OMEGA > {X}")
            if not p: continue
            if p.lower() in ['exit','x']: os.system("pkill -f python"); break
            if p.lower() == 'reset': os.system("pkill -f python"); os.execv(sys.executable, ['python3'] + sys.argv)
            if p.lower() == 'jobs': 
                 for j,d in JOBS.items(): 
                    s = "RUN" if d['proc'].poll() is None else "END"
                    print(f"[{j}] {s} | {d['cmd'][:40]}")
                 continue
            if p.lower() == 'auto': AUTONOMY = not AUTONOMY; print_banner(); continue
            
            mode = "TASK" if p.startswith("@") else "NORMAL"
            if mode == "TASK": agent_loop(p)
            else:
                r = ai_think(p)
                print(r)
        except KeyboardInterrupt: print("\nPaused.")
        except Exception as e: print(f"Err: {e}")

if __name__ == "__main__": main()
