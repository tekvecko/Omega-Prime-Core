import sqlite3
import os

# Změna: Čte proměnnou prostředí
DB_PATH = os.environ.get('OMEGA_DB_PATH', 'omega.db')

def think():
    print(f"   🧠 CORTEX: Analyzuji sektor {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("   ❌ Databáze neexistuje (zatím prázdná).")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
        
        # Zkusíme najít unikátní zařízení
        try:
            uniq = conn.execute("SELECT COUNT(DISTINCT message) FROM logs WHERE message LIKE '%LAN REAPER%'").fetchone()[0]
            info = f" | Unikátní scany: {uniq}"
        except:
            info = ""

        print(f"   📊 Záznamů: {count}{info}")
            
    except Exception as e:
        print(f"   ⚠️ Chyba cortexu: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    think()
