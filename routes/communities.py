from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
import string
from db import get_db
from models import Community, User
from schemas.community_schema import CommunityCreate, CommunityResponse

router = APIRouter(prefix="/communities", tags=["communities"])


def generate_access_code(length: int = 10) -> str:
    """Generate a random alphanumeric access code like HIVE-AB12CD34."""
    chars = string.ascii_uppercase + string.digits
    raw = ''.join(secrets.choice(chars) for _ in range(length))
    return f"HIVE-{raw[:4]}-{raw[4:8]}-{raw[8:]}"


@router.post("/", response_model=CommunityResponse)
def create_community(community: CommunityCreate, owner_id: int, db: Session = Depends(get_db)):
    # Verify owner exists
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="User not found")

    # Auto-generate a unique access code for private communities
    # (public communities also get a code so owners can always share it later)
    code = None
    for _ in range(10):  # retry loop for uniqueness
        candidate = generate_access_code()
        existing = db.query(Community).filter(Community.access_code == candidate).first()
        if not existing:
            code = candidate
            break

    if not code:
        raise HTTPException(status_code=500, detail="Could not generate a unique access code. Try again.")

    db_community = Community(**community.model_dump(), owner_id=owner_id, access_code=code)
    db.add(db_community)
    db.commit()
    db.refresh(db_community)
    return db_community


@router.get("/join/{access_code}", response_model=CommunityResponse)
def get_community_by_code(access_code: str, db: Session = Depends(get_db)):
    """Look up a community by its access code. Used by the Enter Code flow."""
    community = db.query(Community).filter(Community.access_code == access_code).first()
    if not community:
        raise HTTPException(status_code=404, detail="Invalid access code. No community found.")
    if community.visibility != "private":
        raise HTTPException(status_code=400, detail="This community is public — join it directly.")
    return community


@router.get("/", response_model=List[CommunityResponse])
def list_communities(visibility: Optional[str] = None, owner_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Community)
    if visibility:
        query = query.filter(Community.visibility == visibility)
    if owner_id:
        query = query.filter(Community.owner_id == owner_id)
    return query.all()


@router.get("/{community_id}", response_model=CommunityResponse)
def get_community(community_id: int, db: Session = Depends(get_db)):
    db_community = db.query(Community).filter(Community.id == community_id).first()
    if not db_community:
        raise HTTPException(status_code=404, detail="Community not found")
    return db_community
