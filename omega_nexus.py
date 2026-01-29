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

# --- GLOBAL STAV ---
CONTEXT = []
AUTONOMY = False
MAX_AUTO_STEPS = 10
JOBS = {}
LOG_DIR = "nexus_logs"

if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

# --- BARVY ---
R, G, Y, C, M, W, X = "\033[1;31m", "\033[1;32m", "\033[1;33m", "\033[1;36m", "\033[1;35m", "\033[1;37m", "\033[0m"

def get_dashboard():
    user = getpass.getuser()
    active_jobs = len(JOBS)
    col = G if active_jobs > 0 else C
    return f"{C}USER:{X}{user} | {C}JOBS:{col}{active_jobs}{X}"

def print_banner():
    os.system("clear")
    print(f"{C}╔════════════════════════════════════════════╗{X}")
    print(f"{C}║  OMEGA NEXUS v7.0: AGENTIC FEEDBACK LOOP   ║{X}")
    print(f"{C}╚════════════════════════════════════════════╝{X}")
    print(f" {get_dashboard()}")
    print(f" AI: {W}{MODEL_NAME}{X} | Auto: {M if AUTONOMY else Y}{AUTONOMY}{X}")
    print(f"{C}──────────────────────────────────────────────{X}\n")

# --- PROCESY ---
def run_background(cmd_list):
    job_id = len(JOBS) + 1
    log_path = os.path.join(LOG_DIR, f"job_{job_id}.log")
    try:
        f = open(log_path, "w")
        p = subprocess.Popen(cmd_list, stdout=f, stderr=subprocess.STDOUT, text=True, cwd=os.getcwd())
        JOBS[job_id] = {"proc": p, "log": f, "cmd": " ".join(cmd_list)}
        return True, job_id
    except Exception as e: return False, str(e)

def run_realtime(cmd_list):
    master, slave = os.openpty()
    try:
        p = subprocess.Popen(cmd_list, stdout=slave, stderr=slave, close_fds=True, text=True)
        os.close(slave)
        output_log = []
        while True:
            try:
                r, _, _ = select.select([master], [], [], 0.1)
                if r:
                    data = os.read(master, 1024).decode(errors='replace')
                    if not data: break
                    print(data, end='', flush=True)
                    output_log.append(data)
                elif p.poll() is not None: break
            except OSError: break
        p.wait()
        return p.returncode, "".join(output_log)
    except Exception as e:
        os.close(master)
        return 1, str(e)

# --- AI MOZEK ---
def ai_think(prompt, feedback=False):
    global CONTEXT
    if feedback:
        sys_msg = """Jsi OMEGA. Analyzuj výsledek. Pokud chyba -> oprav. Pokud OK -> další krok. Pokud hotovo -> jen text."""
    else:
        sys_msg = """Jsi OMEGA. Plánuj kroky. Generuj kód (bash/python). Pokud server -> [BACKGROUND]."""

    msgs = [{'role': 'user', 'parts': [sys_msg]}] + CONTEXT + [{'role': 'user', 'parts': [prompt]}]
    print(f"{C}Thinking...{X}", end="\r")
    try:
        resp = model.generate_content(msgs).text
        CONTEXT.append({'role': 'user', 'parts': [prompt]})
        CONTEXT.append({'role': 'model', 'parts': [resp]})
        if len(CONTEXT) > 15: CONTEXT = CONTEXT[-15:]
        return resp
    except: return "AI Error"

# --- AGENTIC LOOP ---
def agent_loop(initial_prompt):
    current_prompt = initial_prompt
    is_feedback = False
    step_count = 0
    
    while True:
        response = ai_think(current_prompt, feedback=is_feedback)
        print(f"\n{C}AI:{X} {response}")
        
        blocks = re.findall(r"```(bash|python|sh)?\n(.*?)```", response, re.DOTALL)
        if not blocks:
            print(f"\n{G}>>> DOKONČENO.{X}")
            break
            
        step_count += 1
        if step_count > MAX_AUTO_STEPS: break

        execution_results = []
        for lang, code in blocks:
            lang = lang.strip().lower() or "bash"
            print(f"\n{Y}--- KROK {step_count}: {lang} ---{X}")
            print('\n'.join(code.split('\n')[:3]) + "...")
            
            action = 'y'
            if not AUTONOMY:
                action = input(f"{W}[Enter]=Spustit | [b]=Pozadí | [n]=Skip: {X}").lower()
            
            if action == 'n': continue
            is_bg = (action == 'b') or ("server" in code and AUTONOMY)
            
            if is_bg:
                if "python" in lang:
                    with open("omega_staging.py", "w") as f: f.write(code)
                    ok, jid = run_background(['python3', 'omega_staging.py'])
                else:
                    ok, jid = run_background(['/data/data/com.termux/files/usr/bin/bash', '-c', code])
                msg = f"BG Job {jid}" if ok else "BG Error"
                print(f"{G if ok else R}✔ {msg}{X}")
                execution_results.append(msg)
            else:
                print(f"{G}>>> RUNNING...{X}")
                if "python" in lang:
                    with open("omega_staging.py", "w") as f: f.write(code)
                    rc, out = run_realtime(['python3', 'omega_staging.py'])
                else:
                    rc, out = run_realtime(['/data/data/com.termux/files/usr/bin/bash', '-c', code])
                
                status = "OK" if rc == 0 else f"ERR {rc}"
                print(f"{G if rc==0 else R}>>> {status}{X}")
                clean_out = out[-2000:] if len(out) > 2000 else out
                execution_results.append(f"Status: {status}\nOut:\n{clean_out}")

        current_prompt = "VÝSLEDKY:\n" + "\n".join(execution_results) + "\nCo dál?"
        is_feedback = True

def main():
    global AUTONOMY
    print_banner()
    while True:
        try:
            p = input(f"\n{G}OMEGA > {X}")
            if p.lower() in ['exit','x']: break
            if p.lower() == 'jobs': 
                for jid, j in JOBS.items(): print(f"[{jid}] {j['cmd'][:30]}")
                continue
            if p.lower().startswith('kill '):
                try: 
                    jid = int(p.split()[1])
                    os.kill(JOBS[jid]['proc'].pid, signal.SIGKILL)
                    del JOBS[jid]
                    print("Killed.")
                except: pass
                continue
            if p.lower() == 'auto': AUTONOMY = not AUTONOMY; print_banner(); continue
            if p.lower() == 'clear': print_banner(); continue
            if not p: continue
            
            agent_loop(p)
            
        except KeyboardInterrupt: print("\nPaused.")

if __name__ == "__main__": main()
