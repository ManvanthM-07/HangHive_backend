from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import MediaItem
from schemas.media_schema import MediaItemCreate, MediaItemResponse

from chat import manager

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/", response_model=MediaItemResponse)
async def create_media(media: MediaItemCreate, db: Session = Depends(get_db)):
    print(f"[MEDIA_DEBUG] Received upload request: {media.model_dump()}")
    db_media = MediaItem(**media.model_dump())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    
    # Broadcast to the community in real-time
    try:
        await manager.broadcast_to_community(
            str(db_media.community_id), 
            {
                "type": "new_media", 
                "media_type": db_media.type,
                "title": db_media.title,
                "sender_name": "System" # Or fetch username if needed
            }
        )
    except Exception as e:
        print(f"[MEDIA_DEBUG] Failed to broadcast new media: {e}")

    return db_media

@router.get("/{community_id}", response_model=List[MediaItemResponse])
def list_media(community_id: int, type: str = None, db: Session = Depends(get_db)):
    query = db.query(MediaItem).filter(MediaItem.community_id == community_id)
    if type:
        query = query.filter(MediaItem.type == type)
    return query.all()
