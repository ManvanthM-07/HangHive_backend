from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
from communities.work import ConnectionManager

router = APIRouter(tags=["gaming"])

# ─── Gaming context definitions ────────────────────────────────────────────────
GAMING_CONTEXTS = {
    "lobby":      {"label": "🎮 Lobby",       "description": "General gaming chat and LFG"},
    "matchmaking": {"label": "⚔️ Matchmaking", "description": "Ranked and competitive play"},
    "retro":      {"label": "🕹️ Retro",       "description": "Classic gaming and emulators"},
    "tournament": {"label": "🏆 Tournament",  "description": "Live events and scrims"},
}

class GamingConnectionManager(ConnectionManager):
    pass

gaming_manager = GamingConnectionManager()

def get_gaming_html():
    from communities.work import html
    # Theming for Gaming (Green/Neon)
    themed_html = html.replace("--primary:      #4f6ef7;", "--primary:      #22c55e;")
    themed_html = themed_html.replace("--primary-dark: #3b55d4;", "--primary-dark: #15803d;")
    themed_html = themed_html.replace("Work Community", "Gaming Nexus")
    themed_html = themed_html.replace("Work Chat", "Gaming Comms")
    themed_html = themed_html.replace("👋 Welcome to Work", "🎮 Welcome to the Nexus")
    themed_html = themed_html.replace("Select your work context", "Select your gaming zone")
    
    import json
    contexts_js = f"var CTX_META = {json.dumps({k: {'label': v['label'], 'color': '#22c55e'} for k, v in GAMING_CONTEXTS.items()})};"
    themed_html = themed_html.replace("var CTX_META = {", contexts_js + " //")
    
    themed_html = themed_html.replace("/ws/work/", "/ws/gaming/")
    
    return themed_html

@router.get("/gaming")
async def get():
    return HTMLResponse(get_gaming_html())

@router.websocket("/ws/gaming/{room_id}/{client_id}")
async def gaming_websocket(
    websocket: WebSocket,
    room_id: str,
    client_id: int,
    username: str = "Gamer",
):
    parts = room_id.split("_", 1)
    context = parts[1] if len(parts) == 2 else ""
    if context not in GAMING_CONTEXTS:
        await websocket.accept()
        await websocket.send_json({"type": "error", "content": "Invalid gaming context."})
        await websocket.close()
        return

    await gaming_manager.connect(websocket, client_id, room_id, username)
    await gaming_manager.broadcast({"type": "system", "content": f"{username} joined the {GAMING_CONTEXTS[context]['label']}"}, room_id)
    
    try:
        while True:
            text = await websocket.receive_text()
            await gaming_manager.broadcast({"type": "chat", "sender_id": client_id, "sender_name": username, "content": text}, room_id)
    except WebSocketDisconnect:
        gaming_manager.disconnect(websocket, client_id, room_id)
        await gaming_manager.broadcast({"type": "system", "content": f"{username} left the lobby"}, room_id)
