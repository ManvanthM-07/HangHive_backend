import os
from fastapi import APIRouter, HTTPException
from typing import List, Dict

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

@router.get("/system-nodes", response_model=List[Dict])
def list_system_communities():
    """
    Scans the communities/ folder for .py files and returns them as available nodes.
    Excludes __init__.py and this file itself (create_own.py).
    """
    communities = []
    try:
        if not os.path.exists(COMMUNITIES_DIR):
            return []

        for filename in os.listdir(COMMUNITIES_DIR):
            if filename.endswith(".py") and filename not in ["__init__.py", "create_own.py"]:
                purpose = filename.replace(".py", "")
                name = purpose.capitalize()
                communities.append({
                    "id": f"system_{purpose}",
                    "name": name,
                    "purpose": purpose,
                    "visibility": "public",
                    "description": f"Official HangHive {name} community node.",
                    "owner_id": 0  # 0 indicates system-owned
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return communities
