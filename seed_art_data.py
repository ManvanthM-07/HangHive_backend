import os
import sys
from sqlalchemy.orm import Session
from db import SessionLocal, engine
import models
from datetime import datetime

def seed():
    db = SessionLocal()
    try:
        # 1. Find the Art Community (or create one if it doesn't exist)
        art_comm = db.query(models.Community).filter(models.Community.purpose == 'art').first()
        if not art_comm:
            print("No Art community found. Please create one in the app first.")
            return

        print(f"Seeding Art Community: {art_comm.name} (ID: {art_comm.id})")

        # 2. Add Media Items
        sample_media = [
            # Exhibition (Images)
            {
                "type": "image",
                "title": "Neon Cyberpunk Cityscape",
                "url": "https://images.unsplash.com/photo-1605142859862-978be7eba909?auto=format&fit=crop&q=80&w=1000",
                "owner_id": art_comm.owner_id,
                "community_id": art_comm.id
            },
            {
                "type": "image",
                "title": "Abstract Fluidity",
                "url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&q=80&w=1000",
                "owner_id": art_comm.owner_id,
                "community_id": art_comm.id
            },
            # Shorts (Videos)
            {
                "type": "video",
                "title": "Abstract Motion Graphics",
                "url": "https://assets.mixkit.co/videos/preview/mixkit-abstract-motion-graphics-of-a-sphere-32433-large.mp4",
                "owner_id": art_comm.owner_id,
                "community_id": art_comm.id
            },
             {
                "type": "video",
                "title": "Cyberpunk Portrait",
                "url": "https://assets.mixkit.co/videos/preview/mixkit-cyberpunk-look-of-a-woman-at-night-with-neon-lights-42939-large.mp4",
                "owner_id": art_comm.owner_id,
                "community_id": art_comm.id
            },
            # Studio (Audio)
            {
                "type": "audio",
                "title": "Lofi Hip Hop Beat",
                "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                "owner_id": art_comm.owner_id,
                "community_id": art_comm.id
            },
            {
                "type": "audio",
                "title": "Chill Synthwave",
                "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
                "owner_id": art_comm.owner_id,
                "community_id": art_comm.id
            }
        ]

        for item_data in sample_media:
            # Check if exists
            exists = db.query(models.MediaItem).filter(models.MediaItem.url == item_data["url"]).first()
            if not exists:
                item = models.MediaItem(**item_data)
                db.add(item)
                print(f"Added Media: {item_data['title']}")

        # 3. Add Welcome Messages
        room_id = f"{art_comm.id}-lobby"
        sample_messages = [
            "Welcome to the Art Community! 🎨",
            "This is the landing grid where you can explore different formats.",
            "Check out the Exhibition tab for our latest gallery.",
            "Or drop some beats in the Studio! 🎵"
        ]

        for content in sample_messages:
            exists = db.query(models.Message).filter(models.Message.content == content, models.Message.room_id == room_id).first()
            if not exists:
                msg = models.Message(content=content, sender_id=art_comm.owner_id, room_id=room_id)
                db.add(msg)
                print(f"Added Message: {content}")

        db.commit()
        print("Seeding complete!")

    except Exception as e:
        print(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
