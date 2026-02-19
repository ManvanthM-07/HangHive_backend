from sqlalchemy import Column, Integer, String
from db import Base
from dotenv import load_dotenv
load_dotenv()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # plaintext per user instructions
