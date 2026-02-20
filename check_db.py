import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('hanghive.db')
        cursor = conn.cursor()
        
        print("--- Tables ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            print(t[0])
            
        if ('users',) in tables:
            print("\n--- Users Table ---")
            cursor.execute("SELECT id, username, email FROM users;")
            users = cursor.fetchall()
            if not users:
                print("No users found.")
            for u in users:
                print(u)
        else:
            print("\nUsers table does not exist!")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
