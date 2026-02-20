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

        # If user is switching rooms, they might still be in the registry.
        # We allow them to move, as the disconnect cleanup might be slightly delayed.
        if client_id in self.user_registry:
            old_room = self.user_registry[client_id]
            if old_room != room_id:
                print(f"User {client_id} moving from {old_room} to {room_id}")

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

        # Only remove from registry if it's the same room (avoid clearing new connection)
        if client_id in self.user_registry and self.user_registry[client_id] == room_id:
            del self.user_registry[client_id]

    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.rooms:
            for connection in self.rooms[room_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{room_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: int, username: str = "Anonymous"):
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
