import sqlite3

def get_connection(db_name):
    return sqlite3.connect(db_name, timeout=10)

# --- LEVEL 1: SECURITY (Parametrizované dotazy) ---
def secure_login(db_name, user, password):
    con = get_connection(db_name)
    try:
        cur = con.cursor()
        # Správné řešení: Žádný regex, jen '?'
        cur.execute("SELECT * FROM users WHERE user = ? AND pass = ?", (user, password))
        return cur.fetchone() is not None
    finally:
        con.close()

# --- LEVEL 2: CONCURRENCY (Zamykání) ---
def transfer_funds(db_name, from_id, to_id, amount):
    con = get_connection(db_name)
    try:
        # Správné řešení: BEGIN IMMEDIATE zamkne DB
        con.execute("BEGIN IMMEDIATE")
        cur = con.cursor()
        
        cur.execute("SELECT balance FROM accounts WHERE id = ?", (from_id,))
        row = cur.fetchone()
        if not row or row[0] < amount:
            con.rollback()
            return False
            
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_id))
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_id))
        
        con.commit()
        return True
    except:
        con.rollback()
        raise
    finally:
        con.close()

# --- LEVEL 3: SELF HEALING (Lazy Init) ---
def log_event(db_name, message):
    con = get_connection(db_name)
    try:
        con.execute("INSERT INTO logs VALUES (?)", (message,))
        con.commit()
    except sqlite3.OperationalError:
        # Správné řešení: Zachycení chyby a oprava tabulky
        con.execute("CREATE TABLE IF NOT EXISTS logs (msg TEXT)")
        con.execute("INSERT INTO logs VALUES (?)", (message,))
        con.commit()
    finally:
        con.close()

# --- LEVEL 4: ATOMICITY (Rollback) ---
def batch_process(db_name, operations):
    con = get_connection(db_name)
    try:
        con.execute("BEGIN IMMEDIATE")
        cur = con.cursor()
        
        for op in operations:
            action, arg1, arg2, val = op
            if action == 'MOVE':
                cur.execute("UPDATE inventory SET qty = qty - ? WHERE item = ?", (val, arg1))
                cur.execute("UPDATE inventory SET qty = qty + ? WHERE item = ?", (val, arg2))
            elif action == 'CRASH_MODE':
                raise Exception("Simulated Crash")
                
        con.commit() # Commit jen když vše projde
    except Exception as e:
        con.rollback() # Rollback při jakékoliv chybě
        raise e
    finally:
        con.close()
