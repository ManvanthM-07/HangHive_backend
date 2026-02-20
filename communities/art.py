from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
from communities.work import ConnectionManager

router = APIRouter(tags=["art"])

# ─── Art context definitions ──────────────────────────────────────────────────
ART_CONTEXTS = {
    "studio":    {"label": "🎨 Studio",    "description": "For digital and traditional creation"},
    "gallery":   {"label": "🖼️ Gallery",   "description": "Showcase and critique work"},
    "exhibition": {"label": "🏛️ Exhibition", "description": "Global art events and showcases"},
    "sketch":    {"label": "✏️ Sketchpad",  "description": "Quick doodles and brainstorming"},
}

class ArtConnectionManager(ConnectionManager):
    pass

art_manager = ArtConnectionManager()

# ─── HTML UI (Simplified Template) ─────────────────────────────────────────────
def get_art_html():
    from communities.work import html
    # Theming for Art (Pink/Yellow/Cyan mix)
    themed_html = html.replace("--primary:      #4f6ef7;", "--primary:      #ec4899;")
    themed_html = themed_html.replace("--primary-dark: #3b55d4;", "--primary-dark: #be185d;")
    themed_html = themed_html.replace("Work Community", "Art Collective")
    themed_html = themed_html.replace("Work Chat", "Art Network")
    themed_html = themed_html.replace("👋 Welcome to Work", "🎨 Welcome to the Collective")
    themed_html = themed_html.replace("Select your work context", "Select your creative frequency")
    
    # Inject Art Contexts into JS
    import json
    contexts_js = f"var CTX_META = {json.dumps({k: {'label': v['label'], 'color': '#ec4899'} for k, v in ART_CONTEXTS.items()})};"
    themed_html = themed_html.replace("var CTX_META = {", contexts_js + " //")
    
    # Fix paths
    themed_html = themed_html.replace("/ws/work/", "/ws/art/")
    
    return themed_html

@router.get("/art")
async def get():
    return HTMLResponse(get_art_html())

@router.websocket("/ws/art/{room_id}/{client_id}")
async def art_websocket(
    websocket: WebSocket,
    room_id: str,
    client_id: int,
    username: str = "Artist",
):
    parts = room_id.split("_", 1)
    context = parts[1] if len(parts) == 2 else ""
    if context not in ART_CONTEXTS:
        await websocket.accept()
        await websocket.send_json({"type": "error", "content": "Invalid art context."})
        await websocket.close()
        return

    await art_manager.connect(websocket, client_id, room_id, username)
    await art_manager.broadcast({"type": "system", "content": f"{username} entered the {ART_CONTEXTS[context]['label']}"}, room_id)
    
    try:
        while True:
            text = await websocket.receive_text()
            await art_manager.broadcast({"type": "chat", "sender_id": client_id, "sender_name": username, "content": text}, room_id)
    except WebSocketDisconnect:
        art_manager.disconnect(websocket, client_id, room_id)
        await art_manager.broadcast({"type": "system", "content": f"{username} left the collective"}, room_id)
