import sqlite3
import os

def check_full_db():
    db_file = 'hanghive.db'
    if not os.path.exists(db_file):
        print(f"Error: {db_file} not found!")
        return

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"--- Database: {os.path.abspath(db_file)} ---")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables found: {[t[0] for t in tables]}")
            
        for table_name in [t[0] for t in tables]:
            print(f"\n--- Content of '{table_name}' ---")
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            if not rows:
                print("Table is empty.")
            else:
                for row in rows:
                    print(row)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_full_db()
