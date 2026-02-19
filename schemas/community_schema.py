from pydantic import BaseModel
from typing import Optional

class CommunityBase(BaseModel):
    name: str
    purpose: str
    visibility: str
    description: Optional[str] = None

class CommunityCreate(CommunityBase):
    pass

class CommunityResponse(CommunityBase):
    id: int
    owner_id: int
    access_code: Optional[str] = None  # Exposed only for private communities

    class Config:
        from_attributes = True
