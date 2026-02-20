from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from models import User
from schemas.user_schema import UserCreate, UserResponse

router = APIRouter(tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        print(f"SIGNUP ATTEMPT: {user.username} | {user.email}")
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            print(f"SIGNUP FAILED: Email {user.email} already exists")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = User(
            username=user.username,
            email=user.email,
            password=user.password  # plaintext per user instructions
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"SIGNUP SUCCESS: {user.username}")
        return new_user
    except Exception as e:
        print(f"SIGNUP CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal database error: {str(e)}")
