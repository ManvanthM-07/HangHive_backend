import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def reset_remote_table():
    url = os.getenv('DATABASE_URL')
    try:
        conn = psycopg2.connect(url)
        conn.autocommit = True
        cur = conn.cursor()
        print("Dropping 'users' table if it exists...")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")
        print("Table dropped successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_remote_table()
