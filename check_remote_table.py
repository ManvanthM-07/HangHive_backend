import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_remote_table():
    url = os.getenv('DATABASE_URL')
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');")
        exists = cur.fetchone()[0]
        print(f"Table 'users' exists: {exists}")
        
        if exists:
            cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users';")
            columns = cur.fetchall()
            print("Columns:")
            for col in columns:
                print(f" - {col[0]} ({col[1]})")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_remote_table()
