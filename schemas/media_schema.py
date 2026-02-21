from pydantic import BaseModel
from typing import Optional

class MediaItemBase(BaseModel):
    type: str  # "video", "image", "audio"
    url: str
    title: str
    owner_id: int
    community_id: int

class MediaItemCreate(MediaItemBase):
    pass

class MediaItemResponse(MediaItemBase):
    id: int

    class Config:
        from_attributes = True
