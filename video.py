from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict

router = APIRouter(prefix="/ws/video", tags=["video"])

class VideoConnectionManager:
    def __init__(self):
        # room_id -> {client_id: (websocket, username)}
        self.active_connections: Dict[str, Dict[str, tuple]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, client_id: str, username: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][client_id] = (websocket, username)

    def disconnect(self, room_id: str, client_id: str):
        if room_id in self.active_connections:
            if client_id in self.active_connections[room_id]:
                del self.active_connections[room_id][client_id]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def send_to_client(self, message: dict, room_id: str, target_client: str):
        if room_id in self.active_connections:
            if target_client in self.active_connections[room_id]:
                conn, name = self.active_connections[room_id][target_client]
                await conn.send_json(message)

    async def broadcast(self, message: dict, room_id: str, exclude_client: str = None):
        if room_id in self.active_connections:
            for c_id, (conn, name) in self.active_connections[room_id].items():
                if c_id != exclude_client:
                    await conn.send_json(message)

    def get_participants(self, room_id: str):
        if room_id in self.active_connections:
            return [{"id": c_id, "name": name} for c_id, (conn, name) in self.active_connections[room_id].items()]
        return []

manager = VideoConnectionManager()

@router.websocket("/{room_id}/{client_id}")
async def video_websocket_endpoint(websocket: WebSocket, room_id: str, client_id: str, username: str = "Anonymous"):
    await manager.connect(websocket, room_id, client_id, username)
    
    participants = manager.get_participants(room_id)
    await manager.broadcast(
        {"type": "video_participants", "participants": participants},
        room_id
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            target = data.get("target")
            if target:
                await manager.send_to_client(data, room_id, target)
            else:
                await manager.broadcast(data, room_id, exclude_client=client_id)
    except WebSocketDisconnect:
        manager.disconnect(room_id, client_id)
        participants = manager.get_participants(room_id)
        await manager.broadcast(
            {"type": "video_participants", "participants": participants},
            room_id
        )
