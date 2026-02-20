import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def list_all_tables():
    url = os.getenv('DATABASE_URL')
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        print("--- All Tables in Public Schema ---")
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog');
        """)
        tables = cur.fetchall()
        for t in tables:
            print(f"Schema: {t[0]} | Table: {t[1]}")
            
        cur.execute("SELECT current_database(), current_schema();")
        db_info = cur.fetchone()
        print(f"\nCurrent DB: {db_info[0]} | Current Schema: {db_info[1]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all_tables()
