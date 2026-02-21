import os
import sys
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Add backend to path to import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from models import Community, MediaItem, Message

load_dotenv()

def seed_school_data():
    db = SessionLocal()
    try:
        # Find any Work community
        work_comm = db.query(Community).filter(Community.purpose.ilike('work')).first()
        
        if not work_comm:
            print("No Work community found. Please create a community with purpose 'Work' first.")
            return

        print(f"Found Work Community: {work_comm.name} (ID: {work_comm.id})")

        # Sample School Items (Teacher/Student)
        school_items = [
            # Teacher Hub
            {
                "title": "Semester 1 Mathematics Curriculum",
                "url": "https://www.khanacademy.org/math",
                "type": "school-teacher"
            },
            {
                "title": "Advanced Physics Lecture Notes",
                "url": "https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/",
                "type": "school-teacher"
            },
            # Student Space
            {
                "title": "Calculus II Assignment #4",
                "url": "https://www.overleaf.com/project",
                "type": "school-student"
            },
            {
                "title": "Student Science Fair Handbook",
                "url": "https://www.societyforscience.org/isef/",
                "type": "school-student"
            }
        ]

        # Add items if they don't exist for this community
        for item_data in school_items:
            exists = db.query(MediaItem).filter(
                MediaItem.community_id == work_comm.id,
                MediaItem.title == item_data["title"]
            ).first()
            
            if not exists:
                new_item = MediaItem(
                    title=item_data["title"],
                    url=item_data["url"],
                    type=item_data["type"],
                    owner_id=work_comm.owner_id,
                    community_id=work_comm.id
                )
                db.add(new_item)
                print(f"Added School Item: {item_data['title']} ({item_data['type']})")

        db.commit()
        print("School seeding complete!")

    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_school_data()
