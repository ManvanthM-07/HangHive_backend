from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from dotenv import load_dotenv
load_dotenv()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # plaintext per user instructions

    # Communities owned by this user
    owned_communities = relationship("Community", back_populates="owner")

class Community(Base):
    __tablename__ = "communities_table" # Using a distinct name to avoid conflicts

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    purpose = Column(String) # "personal", "others", etc.
    visibility = Column(String) # "public", "private"
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    access_code = Column(String, nullable=True, unique=True, index=True)  # Random code for private communities

    owner = relationship("User", back_populates="owned_communities")
