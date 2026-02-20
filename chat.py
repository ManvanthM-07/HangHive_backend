from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict

router = APIRouter(tags=["chat"])


class ConnectionManager:
    def __init__(self):
        # room_id -> list of (websocket, client_id) tuples
        self.rooms: Dict[str, List[WebSocket]] = {}
        # client_id -> current room_id
        self.user_registry: Dict[int, str] = {}

    async def connect(self, websocket: WebSocket, client_id: int, room_id: str):
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = []

        self.rooms[room_id].append(websocket)
        self.user_registry[client_id] = room_id

    def disconnect(self, websocket: WebSocket, client_id: int, room_id: str):
        if room_id in self.rooms:
            if websocket in self.rooms[room_id]:
                self.rooms[room_id].remove(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

        if client_id in self.user_registry and self.user_registry[client_id] == room_id:
            del self.user_registry[client_id]

    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.rooms:
            for connection in self.rooms[room_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{room_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: int, username: str = "Anonymous"):
    # Enforce one community at a time
    if client_id in manager.user_registry and manager.user_registry[client_id] != room_id:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "content": "You are already active in another community!"
        })
        await websocket.close()
        return

    await manager.connect(websocket, client_id, room_id)
    await manager.broadcast(
        {"type": "system", "content": f"{username} (User #{client_id}) joined {room_id}"},
        room_id
    )

    try:
        while True:
            data = await websocket.receive_text()
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
