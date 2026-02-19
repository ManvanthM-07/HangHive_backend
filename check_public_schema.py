import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_public_users():
    url = os.getenv('DATABASE_URL')
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        print("--- Columns in public.users ---")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = 'users';
        """)
        columns = cur.fetchall()
        if not columns:
            print("public.users table does not exist.")
        else:
            for col in columns:
                print(f" - {col[0]} ({col[1]})")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_public_users()
