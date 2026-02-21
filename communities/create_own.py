import os
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from db import get_db
from models import Community

# Import the community routers
from .art import router as art_router
from .gaming import router as gaming_router
from .study import router as study_router
from .friends import router as friends_router
from .work import router as work_router

router = APIRouter(tags=["system-communities"])

# Include the routers here to centralize the communities folder
router.include_router(art_router, prefix="/art")
router.include_router(gaming_router, prefix="/gaming")
router.include_router(study_router, prefix="/study")
router.include_router(friends_router, prefix="/friends")
router.include_router(work_router, prefix="/work")

# Path to the communities folder relative to this file
COMMUNITIES_DIR = os.path.dirname(os.path.abspath(__file__))

# Definitions for system communities so they can be seeded
SYSTEM_COMMUNITY_DEFS = [
    {"purpose": "art",     "name": "HangHive Art Collective",       "description": "Official HangHive Art community node."},
    {"purpose": "gaming",  "name": "HangHive Gaming Arena",         "description": "Official HangHive Gaming community node."},
    {"purpose": "study",   "name": "HangHive Study Hub",            "description": "Official HangHive Study community node."},
    {"purpose": "friends", "name": "HangHive Friends Lounge",       "description": "Official HangHive Friends community node."},
    {"purpose": "work",    "name": "HangHive Work Network",         "description": "Official HangHive Work community node."},
]


def get_or_create_system_community(purpose: str, name: str, description: str, db: Session) -> Community:
    """
    Get the system community from the DB by purpose, or create it if it doesn't exist.
    System communities are identified by owner_id=0 and the given purpose.
    """
    community = db.query(Community).filter(
        Community.owner_id == 0,
        Community.purpose == purpose
    ).first()

    if not community:
        community = Community(
            name=name,
            purpose=purpose,
            visibility="public",
            description=description,
            owner_id=0,
            access_code=None  # System communities don't need an access code
        )
        db.add(community)
        db.commit()
        db.refresh(community)

    return community


@router.get("/system-nodes", response_model=List[Dict])
def list_system_communities(db: Session = Depends(get_db)):
    """
    Returns the system communities with their REAL database integer IDs.
    Seeds them into the database on first call if they don't yet exist.
    """
    result = []
    for defn in SYSTEM_COMMUNITY_DEFS:
        try:
            community = get_or_create_system_community(
                purpose=defn["purpose"],
                name=defn["name"],
                description=defn["description"],
                db=db
            )
            result.append({
                "id": community.id,           # Real integer DB ID
                "name": community.name,
                "purpose": community.purpose,
                "visibility": community.visibility,
                "description": community.description,
                "owner_id": community.owner_id,
            })
        except Exception as e:
            # Fallback: don't crash the whole endpoint if one community fails
            print(f"[SYSTEM_COMMUNITY] Error seeding {defn['purpose']}: {e}")

    return result
