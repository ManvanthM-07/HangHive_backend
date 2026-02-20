import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def diagnose():
    raw_url = os.getenv('DATABASE_URL')
    if not raw_url:
        print("Error: DATABASE_URL not found in .env")
        return

    print(f"Testing URL from .env: {raw_url}")
    
    # Try 1: Current URL
    try:
        conn = psycopg2.connect(raw_url)
        print("SUCCESS: Connected to the database provided in .env!")
        conn.close()
        return
    except psycopg2.OperationalError as e:
        print(f"FAILED (Current URL): {e}")
        if 'database "hanghive" does not exist' in str(e):
            print("\nAttempting logic: Trying default Supabase database name 'postgres'...")
            # Try 2: Replace /hanghive with /postgres
            new_url = raw_url.rsplit('/', 1)[0] + '/postgres'
            try:
                conn = psycopg2.connect(new_url)
                print(f"SUCCESS: Connected to {new_url}!")
                print("\nCONCLUSION: Your Supabase credentials are correct, but the database name is wrong.")
                print("Your Supabase server uses 'postgres' as the database name, not 'hanghive'.")
                conn.close()
            except Exception as e2:
                print(f"FAILED (Default URL): {e2}")
        else:
            print("\nThe error is not related to the database name. Please check your credentials or network.")

if __name__ == "__main__":
    diagnose()
