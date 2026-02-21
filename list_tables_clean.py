import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def list_tables_clean():
    url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE';
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    print(f"{'TABLE NAME':<25} | {'ROWS':<10}")
    print("-" * 40)
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"{table:<25} | {count:<10}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    list_tables_clean()
