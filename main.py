from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rooms = {}

@app.get("/")
def home():
    return {"message": "Group Voice Server Running"}

@app.post("/create-room")
def create_room():
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = {}
    return {"room_id": room_id}

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = {}

    rooms[room_id][user_id] = websocket

    # Notify existing users
    for uid, conn in rooms[room_id].items():
        if uid != user_id:
            await conn.send_json({
                "type": "new-user",
                "user_id": user_id
            })

    try:
        while True:
            data = await websocket.receive_json()
            target = data.get("target")

            if target in rooms[room_id]:
                await rooms[room_id][target].send_json(data)

    except WebSocketDisconnect:
        del rooms[room_id][user_id]

        for conn in rooms[room_id].values():
            await conn.send_json({
                "type": "user-left",
                "user_id": user_id
            })
