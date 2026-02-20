from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter(prefix="/users", tags=["users"])

# ─── In-memory user store ──────────────────────────────────────────────────────
users_db: dict = {}  # email -> user_dict


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/create", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    """Register a new user."""
    if user.email in users_db:
        raise HTTPException(status_code=409, detail="A user with that email already exists.")
    new_user = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "password": user.password,   # stored plaintext per project spec
    }
    users_db[user.email] = new_user
    return UserResponse(id=new_user["id"], username=new_user["username"], email=new_user["email"])


@router.post("/login", response_model=UserResponse)
def login_user(credentials: UserLogin):
    """Authenticate an existing user."""
    stored = users_db.get(credentials.email)
    if not stored or stored["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return UserResponse(id=stored["id"], username=stored["username"], email=stored["email"])


@router.get("/all", response_model=List[UserResponse])
def get_all_users():
    """Return a list of all registered users."""
    return [
        UserResponse(id=u["id"], username=u["username"], email=u["email"])
        for u in users_db.values()
    ]


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str):
    """Return a single user by ID."""
    for u in users_db.values():
        if u["id"] == user_id:
            return UserResponse(id=u["id"], username=u["username"], email=u["email"])
    raise HTTPException(status_code=404, detail="User not found.")
