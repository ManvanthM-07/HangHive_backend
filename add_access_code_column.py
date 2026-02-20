import os
import secrets
import string
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL') or "sqlite:///./hanghive.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_access_code(length: int = 10) -> str:
    """Generate a random alphanumeric access code like HIVE-AB12CD34."""
    chars = string.ascii_uppercase + string.digits
    raw = ''.join(secrets.choice(chars) for _ in range(length))
    return f"HIVE-{raw[:4]}-{raw[4:8]}-{raw[8:]}"

def upgrade():
    db = SessionLocal()
    try:
        # Check if column exists
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='communities_table' AND column_name='access_code';"))
        if result.fetchone():
            print("Column 'access_code' already exists.")
        else:
            print("Adding 'access_code' column...")
            db.execute(text("ALTER TABLE communities_table ADD COLUMN access_code VARCHAR;"))
            db.execute(text("CREATE UNIQUE INDEX ix_communities_table_access_code ON communities_table (access_code);"))
            db.commit()
            print("Column added.")

        # Backfill existing communities
        print("Backfilling existing communities...")
        result = db.execute(text("SELECT id FROM communities_table WHERE access_code IS NULL;"))
        communities = result.fetchall()
        
        for row in communities:
            code = generate_access_code()
            db.execute(text("UPDATE communities_table SET access_code = :code WHERE id = :id"), {"code": code, "id": row[0]})
            print(f"Updated community {row[0]} with code {code}")
        
        db.commit()
        print("Migration complete.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    upgrade()
