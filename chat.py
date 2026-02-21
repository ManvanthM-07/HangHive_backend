import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from db import get_db, SessionLocal
import models
from datetime import datetime

router = APIRouter(tags=["chat"])

class ConnectionManager:
    def __init__(self):
        # room_id -> list of (websocket, client_id, username) dicts
        self.rooms: Dict[str, List[dict]] = {}
        # client_id -> current room_id
        self.user_registry: Dict[int, str] = {}

    async def connect(self, websocket: WebSocket, client_id: int, room_id: str, username: str):
        await websocket.accept()
        print(f"[CHAT_DEBUG] User {username} (#{client_id}) connected to {room_id}")

        if room_id not in self.rooms:
            self.rooms[room_id] = []

        # Remove stale connections
        before = len(self.rooms[room_id])
        self.rooms[room_id] = [c for c in self.rooms[room_id] if c["client_id"] != client_id]
        if len(self.rooms[room_id]) < before:
            print(f"[CHAT_DEBUG] Removed stale connection for user {client_id}")

        self.rooms[room_id].append({
            "websocket": websocket,
            "client_id": client_id,
            "username": username
        })
        self.user_registry[client_id] = room_id
        print(f"[CHAT_DEBUG] Room {room_id} now has {len(self.rooms[room_id])} members")

    def disconnect(self, websocket: WebSocket, client_id: int, room_id: str):
        if room_id in self.rooms:
            self.rooms[room_id] = [c for c in self.rooms[room_id] if c["websocket"] != websocket]
            print(f"[CHAT_DEBUG] User #{client_id} disconnected from {room_id}. Remaining: {len(self.rooms[room_id])}")
            if not self.rooms[room_id]:
                del self.rooms[room_id]

        if client_id in self.user_registry and self.user_registry[client_id] == room_id:
            del self.user_registry[client_id]

    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.rooms:
            print(f"[CHAT_DEBUG] Broadcasting to {room_id}: {message.get('type')}")
            for connection in self.rooms[room_id]:
                try:
                    await connection["websocket"].send_json(message)
                except Exception as e:
                    print(f"[CHAT_DEBUG] Failed to send to a client in {room_id}: {e}")

    async def broadcast_members(self, room_id: str):
        if room_id in self.rooms:
            members = [{"id": c["client_id"], "name": c["username"]} for c in self.rooms[room_id]]
            print(f"[CHAT_DEBUG] Broadcasting members for {room_id}: {members}")
            await self.broadcast({"type": "room_members", "members": members}, room_id)

    async def broadcast_to_community(self, community_id: str, message: dict):
        """Broadcasts a message to all rooms that start with the community_id prefix."""
        print(f"[CHAT_DEBUG] Community Broadcast to {community_id}: {message.get('type')}")
        for room_id, room_connections in self.rooms.items():
            if room_id.startswith(f"{community_id}-"):
                for connection in room_connections:
                    try:
                        await connection["websocket"].send_json(message)
                    except Exception as e:
                        print(f"[CHAT_DEBUG] Failed community broadcast to a client in {room_id}: {e}")

manager = ConnectionManager()

@router.websocket("/ws/{room_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: int, username: str = "Anonymous"):
    await manager.connect(websocket, client_id, room_id, username)
    
    # ─── Load Chat History ───
    db = SessionLocal()
    try:
        history = db.query(models.Message).filter(models.Message.room_id == room_id).order_by(models.Message.timestamp.desc()).limit(50).all()
        # History is in desc order, reverse for client
        for msg in reversed(history):
            await websocket.send_json({
                "type": "chat",
                "sender": msg.sender_id,
                "sender_name": msg.sender.username if msg.sender else "Unknown",
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            })
    except Exception as e:
        print(f"[CHAT_DEBUG] History load error: {e}")
    finally:
        db.close()

    await manager.broadcast(
        {"type": "system", "content": f"{username} joined {room_id}"},
        room_id
    )
    
    # Small delay to ensure client has registered onmessage before we broadcast
    await asyncio.sleep(1.0)
    await manager.broadcast_members(room_id)

    try:
        while True:
            data = await websocket.receive_text()
            
            # Check for control messages
            try:
                msg = json.loads(data)
                if isinstance(msg, dict) and msg.get("type") == "get_members":
                    print(f"[CHAT_DEBUG] Manual members request from {client_id}")
                    await manager.broadcast_members(room_id)
                    continue
            except:
                pass

            # Store in DB
            db = SessionLocal()
            try:
                new_msg = models.Message(content=data, sender_id=client_id, room_id=room_id)
                db.add(new_msg)
                db.commit()
            except Exception as e:
                print(f"[CHAT_DEBUG] Message save error: {e}")
            finally:
                db.close()

            await manager.broadcast(
                {
                    "type": "chat",
                    "sender": client_id,
                    "sender_name": username,
                    "content": data
                },
                room_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id, room_id)
        await manager.broadcast(
            {"type": "system", "content": f"{username} left {room_id}"},
            room_id
        )
        await manager.broadcast_members(room_id)
