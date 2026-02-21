from db import SessionLocal
import models

db = SessionLocal()
try:
    users = db.query(models.User).all()
    comms = db.query(models.Community).all()
    media = db.query(models.MediaItem).all()

    print("=== USERS ===")
    for u in users:
        print(f"ID: {u.id}, Name: {u.username}")

    print("\n=== COMMUNITIES ===")
    for c in comms:
        print(f"ID: {c.id}, Name: {c.name}, Owner: {c.owner_id}")

    print("\n=== MEDIA ITEMS ===")
    for m in media:
        print(f"ID: {m.id}, Title: {m.title}, Owner: {m.owner_id}, Comm: {m.community_id}")

except Exception as e:
    print(f"ERROR: {e}")
finally:
    db.close()
