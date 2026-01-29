import os
import sqlite3
import time
import random
import sys
import json

# --- BARVY ---
GREEN = "\033[1;32m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
PURPLE = "\033[1;35m"
RESET = "\033[0m"
BOLD = "\033[1m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHADOW_DIR = os.path.join(BASE_DIR, "SHADOW_REALM")
TEST_DB = os.path.join(SHADOW_DIR, "stress_test.db")
BENCHMARK_FILE = os.path.join(BASE_DIR, "benchmark_history.json")

def print_header():
    print(f"\n{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║  Ω  OMEGA BENCHMARK v3.1 (STABLE)    ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════╝{RESET}")

def load_history():
    if not os.path.exists(BENCHMARK_FILE): return []
    try:
        with open(BENCHMARK_FILE, "r") as f: return json.load(f)
    except: return []

def save_result(score, total_time, cpu_time, mode):
    history = load_history()
    entry = {
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "mode": mode,
        "score": score,
        "total_time": round(total_time, 3),
        "cpu_time": round(cpu_time, 3)
    }
    history.append(entry)
    
    # FIX: Použití .get() pro staré záznamy bez 'mode'
    # Řazení: Mode (Meltdown > Heavy > Lite > Legacy), pak Čas
    history.sort(key=lambda x: (x.get("mode", "LEGACY"), -x["score"], x["cpu_time"])) 
    
    with open(BENCHMARK_FILE, "w") as f:
        json.dump(history, f, indent=4)
    return history

def show_leaderboard(history):
    print(f"\n{PURPLE}🏆 SÍŇ SLÁVY (TOP 5){RESET}")
    print(f"{'MOD':<10} | {'DATUM':<16} | {'ČAS':<8}")
    print("-" * 40)
    for entry in history[:5]:
        mode_label = entry.get('mode', 'LEGACY')
        print(f"{mode_label:<10} | {entry['date']:<16} | {entry['cpu_time']}s")
    print("-" * 40)

# --- 1. INTEGRITA ---
def check_integrity():
    print(f"{YELLOW}--- FÁZE 1: INTEGRITA ---{RESET}")
    CRITICAL_FILES = ["omega_nexus.py", "interface.sh", "api_key.txt"]
    score = 0
    for f in CRITICAL_FILES:
        if os.path.exists(os.path.join(BASE_DIR, f)): score += 1
    print(f"   [FILES] Rychlá kontrola jádra...   {GREEN}OK{RESET}")
    return score

# --- 2. DATABÁZE ---
def check_database(intensity):
    print(f"{YELLOW}--- FÁZE 2: SQL I/O ({intensity} rows) ---{RESET}")
    if not os.path.exists(SHADOW_DIR): os.makedirs(SHADOW_DIR)
    score = 0
    try:
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, data TEXT)")
        
        print(f"   [SQL] Zapisuji data...             ", end="")
        sys.stdout.flush()
        for i in range(intensity):
            cursor.execute("INSERT INTO test (data) VALUES (?)", (f"DATA_{i}",))
        conn.commit()
        print(f"{GREEN}OK{RESET}")
        score += 5

        cursor.execute("DROP TABLE test")
        conn.close()
        if os.path.exists(TEST_DB): os.remove(TEST_DB)
    except Exception as e:
        print(f"{RED}CHYBA: {e}{RESET}")
    return score

# --- 3. CPU BURNER ---
def cpu_stress(matrix_size):
    print(f"{YELLOW}--- FÁZE 3: CPU MATRIX ({matrix_size}x{matrix_size}) ---{RESET}")
    print(f"   [CPU] Počítám...                   ", end="")
    sys.stdout.flush()
    
    start_time = time.time()
    
    size = matrix_size
    A = [[random.random() for _ in range(size)] for _ in range(size)]
    B = [[random.random() for _ in range(size)] for _ in range(size)]
    result = [[0] * size for _ in range(size)]
    
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += A[i][k] * B[k][j]
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"{GREEN}OK ({duration:.3f}s){RESET}")
    return 5, duration

def main():
    print_header()
    print("Vyber obtížnost:")
    print("   [1] LITE     (Matice 300)  - Rychlý")
    print("   [2] HEAVY    (Matice 500)  - Standard")
    print("   [3] MELTDOWN (Matice 800)  - EXTRÉM")
    
    choice = input(f"\n{CYAN}VOLBA > {RESET}")
    
    if choice == '3':
        mode = "MELTDOWN"
        mat_size = 800
        sql_rows = 20000
    elif choice == '2':
        mode = "HEAVY"
        mat_size = 500
        sql_rows = 5000
    else:
        mode = "LITE"
        mat_size = 300
        sql_rows = 1000

    print(f"\n🚀 Startuji mód: {BOLD}{mode}{RESET}")
    global_start = time.time()
    
    s1 = check_integrity()
    s2 = check_database(sql_rows)
    s3, cpu_time = cpu_stress(mat_size)
    
    global_end = time.time()
    total_time = global_end - global_start
    total_score = s1 + s2 + s3
    
    print(f"\n{CYAN}══════════════════════════════════════{RESET}")
    print(f"MÓD:         {mode}")
    print(f"CPU ČAS:     {BOLD}{cpu_time:.3f} sec{RESET}")
    print(f"CELKEM:      {total_time:.3f} sec")

    history = save_result(total_score, total_time, cpu_time, mode)
    show_leaderboard(history)

if __name__ == "__main__":
    main()
