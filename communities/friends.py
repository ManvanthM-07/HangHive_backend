from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
from communities.work import ConnectionManager

router = APIRouter(tags=["friends"])

# ─── Friends context definitions ────────────────────────────────────────────────
FRIENDS_CONTEXTS = {
    "lounge": {"label": "🛋️ Lounge", "description": "Casual chat and hangout"},
    "party":  {"label": "🎉 Party",  "description": "Live events and celebrations"},
    "meetup": {"label": "🍔 Meetup", "description": "Plan real-world gatherings"},
    "chill":  {"label": "🎵 Chill",  "description": "Listen to music and relax"},
}

class FriendsConnectionManager(ConnectionManager):
    pass

friends_manager = FriendsConnectionManager()

def get_friends_html():
    from communities.work import html
    # Theming for Friends (Purple/Indigo)
    themed_html = html.replace("--primary:      #4f6ef7;", "--primary:      #818cf8;")
    themed_html = themed_html.replace("--primary-dark: #3b55d4;", "--primary-dark: #6366f1;")
    themed_html = themed_html.replace("Work Community", "Friends Hub")
    themed_html = themed_html.replace("Work Chat", "Social Comms")
    themed_html = themed_html.replace("👋 Welcome to Work", "🤝 Welcome to the Hub")
    themed_html = themed_html.replace("Select your work context", "Select your social vibe")
    
    import json
    contexts_js = f"var CTX_META = {json.dumps({k: {'label': v['label'], 'color': '#818cf8'} for k, v in FRIENDS_CONTEXTS.items()})};"
    themed_html = themed_html.replace("var CTX_META = {", contexts_js + " //")
    
    themed_html = themed_html.replace("/ws/work/", "/ws/friends/")
    
    return themed_html

@router.get("/friends")
async def get():
    return HTMLResponse(get_friends_html())

@router.websocket("/ws/friends/{room_id}/{client_id}")
async def friends_websocket(
    websocket: WebSocket,
    room_id: str,
    client_id: int,
    username: str = "Friend",
):
    parts = room_id.split("_", 1)
    context = parts[1] if len(parts) == 2 else ""
    if context not in FRIENDS_CONTEXTS:
        await websocket.accept()
        await websocket.send_json({"type": "error", "content": "Invalid friends context."})
        await websocket.close()
        return

    await friends_manager.connect(websocket, client_id, room_id, username)
    await friends_manager.broadcast({"type": "system", "content": f"{username} joined the {FRIENDS_CONTEXTS[context]['label']}"}, room_id)
    
    try:
        while True:
            text = await websocket.receive_text()
            await friends_manager.broadcast({"type": "chat", "sender_id": client_id, "sender_name": username, "content": text}, room_id)
    except WebSocketDisconnect:
        friends_manager.disconnect(websocket, client_id, room_id)
        await friends_manager.broadcast({"type": "system", "content": f"{username} left the hub"}, room_id)
