from sqlalchemy import text
from db import engine

def add_created_at():
    with engine.connect() as conn:
        print("Checking media_items table for created_at column...")
        try:
            # PostgreSQL syntax to add column if it doesn't exist
            conn.execute(text("ALTER TABLE media_items ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
            conn.commit()
            print("Successfully added 'created_at' column to 'media_items' table!")
        except Exception as e:
            print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_created_at()
