import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def verify():
    url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'media_items' ORDER BY ordinal_position;")
    for row in cur.fetchall():
        print(f"COL: {row[0]}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    verify()
