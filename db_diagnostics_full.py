import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def diagnose():
    url = os.getenv('DATABASE_URL')
    print(f"Connecting to: {url.split('@')[-1]}") # Log host part only
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        
        tables = ['users', 'communities_table', 'media_items', 'messages']
        for table in tables:
            cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');")
            exists = cur.fetchone()[0]
            print(f"Table '{table}': {'EXISTS' if exists else 'MISSING'}")
            
            if exists:
                cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position;")
                cols = cur.fetchall()
                print(f"  Columns: {', '.join([f'{c[0]} ({c[1]})' for c in cols])}")
                
                cur.execute(f"SELECT COUNT(*) FROM {table};")
                count = cur.fetchone()[0]
                print(f"  Row Count: {count}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
