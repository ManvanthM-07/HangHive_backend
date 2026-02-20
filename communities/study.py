from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
from communities.work import ConnectionManager

router = APIRouter(tags=["study"])

# ─── Study context definitions ──────────────────────────────────────────────────
STUDY_CONTEXTS = {
    "library":   {"label": "📚 Library",    "description": "Quiet study and research"},
    "group":     {"label": "🤝 Group Study", "description": "Collaborative learning"},
    "tutoring":  {"label": "👨‍🏫 Tutoring",    "description": "Mentorship and teaching"},
    "research":  {"label": "🧪 Research",    "description": "Deep dives and data analysis"},
}

class StudyConnectionManager(ConnectionManager):
    pass

study_manager = StudyConnectionManager()

def get_study_html():
    from communities.work import html
    # Theming for Study (Cyan/Teal)
    themed_html = html.replace("--primary:      #4f6ef7;", "--primary:      #06b6d4;")
    themed_html = themed_html.replace("--primary-dark: #3b55d4;", "--primary-dark: #0891b2;")
    themed_html = themed_html.replace("Work Community", "Study Sphere")
    themed_html = themed_html.replace("Work Chat", "Study Comms")
    themed_html = themed_html.replace("👋 Welcome to Work", "📚 Welcome to the Sphere")
    themed_html = themed_html.replace("Select your work context", "Select your study environment")
    
    import json
    contexts_js = f"var CTX_META = {json.dumps({k: {'label': v['label'], 'color': '#06b6d4'} for k, v in STUDY_CONTEXTS.items()})};"
    themed_html = themed_html.replace("var CTX_META = {", contexts_js + " //")
    
    themed_html = themed_html.replace("/ws/work/", "/ws/study/")
    
    return themed_html

@router.get("/study")
async def get():
    return HTMLResponse(get_study_html())

@router.websocket("/ws/study/{room_id}/{client_id}")
async def study_websocket(
    websocket: WebSocket,
    room_id: str,
    client_id: int,
    username: str = "Scholar",
):
    parts = room_id.split("_", 1)
    context = parts[1] if len(parts) == 2 else ""
    if context not in STUDY_CONTEXTS:
        await websocket.accept()
        await websocket.send_json({"type": "error", "content": "Invalid study context."})
        await websocket.close()
        return

    await study_manager.connect(websocket, client_id, room_id, username)
    await study_manager.broadcast({"type": "system", "content": f"{username} entered the {STUDY_CONTEXTS[context]['label']}"}, room_id)
    
    try:
        while True:
            text = await websocket.receive_text()
            await study_manager.broadcast({"type": "chat", "sender_id": client_id, "sender_name": username, "content": text}, room_id)
    except WebSocketDisconnect:
        study_manager.disconnect(websocket, client_id, room_id)
        await study_manager.broadcast({"type": "system", "content": f"{username} left the sphere"}, room_id)
