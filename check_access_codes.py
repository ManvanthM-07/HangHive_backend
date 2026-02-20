from sqlalchemy.orm import Session
from db import SessionLocal
from models import Community

def check_communities():
    db: Session = SessionLocal()
    try:
        communities = db.query(Community).all()
        print(f"Total communities: {len(communities)}")
        for c in communities:
            print(f"ID: {c.id}, Name: {c.name}, Visibility: {c.visibility}, Access Code: {c.access_code}")
    finally:
        db.close()

if __name__ == "__main__":
    check_communities()
