from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base
from dotenv import load_dotenv
load_dotenv()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # plaintext per user instructions

    messages = relationship("Message", back_populates="sender")

class Community(Base):
    __tablename__ = "communities_table" # Using a distinct name to avoid conflicts

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    purpose = Column(String) # "personal", "others", etc.
    visibility = Column(String) # "public", "private"
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, nullable=True)  # nullable so system communities (owner_id=0) don't violate FK
    access_code = Column(String, nullable=True, unique=True, index=True)  # Random code for private communities

class MediaItem(Base):
    __tablename__ = "media_items"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # "video", "image", "audio"
    url = Column(String)   # URL to the media file
    title = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    community_id = Column(Integer, ForeignKey("communities_table.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User")
    community = relationship("Community")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    sender_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(String, index=True) # e.g. "commId-roomId"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", back_populates="messages")
