from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
from chat import router as chat_router
from routes.signup import router as signup_router
from routes.login import router as login_router
from routes.communities import router as communities_router
from communities.create_own import router as system_communities_router
from voice import router as voice_router
from video import router as video_router
from communities.work import router as work_router
from communities.art import router as art_router
from communities.gaming import router as gaming_router
from communities.study import router as study_router
from communities.friends import router as friends_router
from db import engine, Base
import models

# ─── Database Initialization ──────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HangHive API", version="1.0.1")

@app.get("/debug-routes")
def debug_routes():
    return [route.path for route in app.routes]

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allow the Vite dev server, local origins, and all Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173",
        "https://hanghive.vercel.app",
        "https://hang-hive-wlf4.vercel.app",
    ],
    allow_origin_regex="https://hanghive-.*\.vercel\.app", # Support all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rooms = {}

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(signup_router)
app.include_router(login_router)
app.include_router(communities_router)
app.include_router(system_communities_router, prefix="/system-communities")
app.include_router(chat_router)    # /ws/{room_id}/{client_id}  (WebSocket)
app.include_router(voice_router)   # /ws/voice/*
app.include_router(video_router)   # /ws/video/*

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HangHive - Connect & Collaborate</title>
    <style>
        :root {
            --primary: #5865F2;
            --bg-dark: #36393f;
            --bg-sidebar: #2f3136;
            --bg-channels: #202225;
            --text-header: #ffffff;
            --text-muted: #b9bbbe;
            --input-bg: #40444b;
            --accent: #3ba55d;
        }

        body, html {
            height: 100%;
            margin: 0;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--bg-dark);
            color: white;
            overflow: hidden;
        }

        /* ─── Auth Overlay ────────────────────────────────── */
        #auth-overlay {
            position: fixed;
            inset: 0;
            background: #2f3136;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }

        .auth-card {
            background: #36393f;
            padding: 2rem;
            border-radius: 8px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }

        .auth-card h2 { margin-bottom: 1.5rem; text-align: center; }
        .auth-input {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            background: #202225;
            border: none;
            color: white;
            border-radius: 3px;
        }

        .btn-auth {
            width: 100%;
            padding: 10px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-weight: bold;
        }

        .toggle-auth {
            text-align: center;
            margin-top: 15px;
            font-size: 0.85rem;
            color: var(--text-muted);
            cursor: pointer;
        }

        /* ─── Work Context Overlay ────────────────────────── */
        #work-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.85);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1500;
            backdrop-filter: blur(4px);
        }

        .work-card {
            background: #36393f;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            max-width: 500px;
            width: 90%;
        }

        .work-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }

        .work-option {
            background: #40444b;
            padding: 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
        }

        .work-option:hover {
            background: var(--primary);
            transform: translateY(-2px);
        }

        .work-option h3 { margin: 10px 0 5px; font-size: 1.1rem; }
        .work-option p { font-size: 0.8rem; color: var(--text-muted); margin: 0; }

        /* ─── Main App Layout ────────────────────────────── */
        #app-container {
            display: none;
            height: 100%;
            flex-direction: row;
        }

        #guild-sidebar {
            width: 72px;
            background: var(--bg-channels);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 12px;
            gap: 8px;
        }

        .guild-icon {
            width: 48px;
            height: 48px;
            background: #36393f;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: border-radius 0.2s, background 0.2s;
            font-size: 20px;
        }

        .guild-icon:hover {
            border-radius: 30%;
            background: var(--primary);
        }

        .guild-icon.active {
            border-radius: 30%;
            background: var(--primary);
        }

        #room-sidebar {
            width: 240px;
            background: var(--bg-sidebar);
            display: flex;
            flex-direction: column;
        }

        #room-sidebar header {
            padding: 15px;
            font-weight: bold;
            border-bottom: 1px solid rgba(0,0,0,0.2);
        }

        .channel-item {
            padding: 8px 10px;
            margin: 2px 8px;
            border-radius: 4px;
            cursor: pointer;
            color: var(--text-muted);
            font-size: 15px;
        }

        .channel-item:hover {
            background: #393d43;
            color: white;
        }

        .channel-item.active {
            background: #393d43;
            color: white;
        }

        #main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg-dark);
        }

        #chat-header {
            padding: 10px 15px;
            border-bottom: 1px solid rgba(0,0,0,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        #message-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            display: flex;
            gap: 15px;
        }

        .avatar {
            width: 40px;
            height: 40px;
            background: #5865F2;
            border-radius: 50%;
            flex-shrink: 0;
        }

        .msg-body { display: flex; flex-direction: column; }
        .msg-user { font-weight: bold; font-size: 0.95rem; margin-bottom: 4px; }
        .msg-text { color: #dcddde; font-size: 0.9rem; }

        #input-container {
            padding: 0 20px 24px;
        }

        #msg-input {
            width: 100%;
            background: var(--input-bg);
            border: none;
            padding: 11px;
            color: white;
            border-radius: 8px;
            outline: none;
        }

        /* ─── Media Controls ────────────────────────────── */
        #media-bar {
            background: rgba(0,0,0,0.3);
            display: flex;
            padding: 10px;
            gap: 10px;
        }

        .media-btn {
            background: #4f545c;
            border: none;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
        }

        .media-btn.active {
            background: var(--accent);
        }

        #video-grid {
            display: none;
            padding: 10px;
            background: #000;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            max-height: 300px;
            overflow-y: auto;
        }

        .video-box {
            background: #202225;
            aspect-ratio: 16/9;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }

        .video-label {
            position: absolute;
            bottom: 5px;
            left: 5px;
            background: rgba(0,0,0,0.5);
            padding: 2px 6px;
            font-size: 12px;
        }

    </style>
</head>
<body>

    <!-- Auth Module -->
    <div id="auth-overlay">
        <div class="auth-card" id="login-form">
            <h2>HangHive Login</h2>
            <input type="email" id="login-email" class="auth-input" placeholder="Email">
            <input type="password" id="login-pass" class="auth-input" placeholder="Password">
            <button class="btn-auth" onclick="handleLogin()">Login</button>
            <div class="toggle-auth" onclick="toggleAuth(true)">Need an account? Signup</div>
        </div>
        <div class="auth-card" id="signup-form" style="display:none">
            <h2>Create Account</h2>
            <input type="text" id="signup-user" class="auth-input" placeholder="Username">
            <input type="email" id="signup-email" class="auth-input" placeholder="Email">
            <input type="password" id="signup-pass" class="auth-input" placeholder="Password">
            <button class="btn-auth" onclick="handleSignup()">Signup</button>
            <div class="toggle-auth" onclick="toggleAuth(false)">Back to Login</div>
        </div>
    </div>

    <!-- Work Context Module -->
    <div id="work-overlay">
        <div class="work-card">
            <h2>Select Work Community</h2>
            <p style="color:var(--text-muted)">Choose the environment you're working in today</p>
            <div class="work-grid">
                <div class="work-option" onclick="selectWorkContext('school')">
                    <span style="font-size: 2rem;">🏫</span>
                    <h3>School</h3>
                    <p>For students & teachers</p>
                </div>
                <div class="work-option" onclick="selectWorkContext('college')">
                    <span style="font-size: 2rem;">🎓</span>
                    <h3>College</h3>
                    <p>For faculty & researchers</p>
                </div>
                <div class="work-option" onclick="selectWorkContext('office')">
                    <span style="font-size: 2rem;">💼</span>
                    <h3>Office</h3>
                    <p>For professional teams</p>
                </div>
                <div class="work-option" onclick="selectWorkContext('personal')">
                    <span style="font-size: 2rem;">🏠</span>
                    <h3>Personal</h3>
                    <p>For solo projects</p>
                </div>
            </div>
            <button class="btn-auth" style="margin-top: 20px; background: #ed4245;" onclick="closeWorkOverlay()">Cancel</button>
        </div>
    </div>

    <!-- App Module -->
    <div id="app-container">
        <!-- Guilds (Communities) -->
        <div id="guild-sidebar">
            <div class="guild-icon active" onclick="switchCommunity('general')" title="General Lounge">G</div>
            <div class="guild-icon" onclick="switchCommunity('art')" title="Art Exhibition">A</div>
            <div class="guild-icon" onclick="switchCommunity('gaming')" title="Gaming Room">🎮</div>
            <div class="guild-icon" onclick="switchCommunity('friends')" title="Friends Hub">F</div>
            <div class="guild-icon" onclick="switchCommunity('study')" title="Study Group">S</div>
            <div class="guild-icon" onclick="switchCommunity('work')" title="Work Desk">💼</div>
        </div>

        <!-- Rooms (Channels) -->
        <div id="room-sidebar">
            <header id="comm-name">General Lounge</header>
            <div id="channel-list">
                <div class="channel-item active"># main-chat</div>
            </div>
            
            <!-- User Status -->
            <div style="margin-top:auto; padding: 10px; background: #292b2f; display: flex; align-items: center; gap: 10px;">
                <div class="avatar" style="width:32px; height:32px;"></div>
                <div style="font-size: 13px; font-weight: bold;" id="user-display">Anonymous</div>
            </div>
        </div>

        <!-- Main Chat Area -->
        <div id="main-content">
            <header id="chat-header">
                <div style="font-weight: bold;"># main-chat</div>
                <div id="media-bar">
                    <button class="media-btn" id="voice-btn" onclick="toggleVoice()">🎙️ Voice</button>
                    <button class="media-btn" id="video-btn" onclick="toggleVideo()">📹 Video</button>
                </div>
            </header>

            <div id="video-grid"></div>

            <div id="message-area"></div>

            <div id="input-container">
                <input type="text" id="msg-input" placeholder="Message #main-chat" onkeydown="if(event.key==='Enter') sendMsg()">
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let activeRoom = 'general';
        let wsChat = null;
        let wsVoice = null;
        let wsVideo = null;

        function toggleAuth(isSignup) {
            document.getElementById('login-form').style.display = isSignup ? 'none' : 'block';
            document.getElementById('signup-form').style.display = isSignup ? 'block' : 'none';
        }

        async function handleSignup() {
            const username = document.getElementById('signup-user').value;
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-pass').value;

            try {
                const res = await fetch('/signup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, email, password})
                });
                if (res.ok) {
                    alert('Signup successful! Please login.');
                    toggleAuth(false);
                } else {
                    const err = await res.json();
                    alert(err.detail);
                }
            } catch (e) { alert('Signup failed'); }
        }

        async function handleLogin() {
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-pass').value;

            try {
                const res = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, password})
                });
                if (res.ok) {
                    currentUser = await res.json();
                    startApp();
                } else {
                    const err = await res.json();
                    alert(err.detail);
                }
            } catch (e) { alert('Login failed'); }
        }

        function startApp() {
            document.getElementById('auth-overlay').style.display = 'none';
            document.getElementById('app-container').style.display = 'flex';
            document.getElementById('user-display').textContent = currentUser.username;
            connectChat();
        }

        function switchCommunity(id) {
            if (id === 'work') {
                document.getElementById('work-overlay').style.display = 'flex';
                return;
            }
            if (activeRoom === id) return;
            activeRoom = id;
            updateAppView(id);
        }

        function selectWorkContext(ctx) {
            activeRoom = `work_${ctx}`;
            document.getElementById('work-overlay').style.display = 'none';
            updateAppView(`Work: ${ctx.charAt(0).toUpperCase() + ctx.slice(1)}`);
        }

        function closeWorkOverlay() {
            document.getElementById('work-overlay').style.display = 'none';
        }

        function updateAppView(displayName) {
            // Update UI
            document.getElementById('comm-name').textContent = displayName;
            
            // Reconnect Chat
            if (wsChat) wsChat.close();
            document.getElementById('message-area').innerHTML = '';
            
            // Update Guild active states
            document.querySelectorAll('.guild-icon').forEach(icon => {
                const title = icon.title.toLowerCase();
                icon.classList.toggle('active', title.includes(activeRoom.split('_')[0]));
            });

            connectChat();
            
            // Close media if open
            if (wsVoice) toggleVoice();
            if (wsVideo) toggleVideo();
        }

        function connectChat() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            wsChat = new WebSocket(`${protocol}//${window.location.host}/ws/${activeRoom}/${currentUser.id}`);
            
            wsChat.onmessage = (event) => {
                const data = JSON.parse(event.data);
                appendMessage(data);
            };
        }

        function sendMsg() {
            const input = document.getElementById('msg-input');
            if (input.value && wsChat) {
                wsChat.send(input.value);
                input.value = '';
            }
        }

        function appendMessage(data) {
            const area = document.getElementById('message-area');
            const msg = document.createElement('div');
            msg.className = 'message';
            
            if (data.type === 'system') {
                msg.innerHTML = `<div class="msg-body"><div class="msg-text" style="color:var(--text-muted)"><i>${data.content}</i></div></div>`;
            } else {
                const isMe = data.sender == currentUser.id;
                msg.innerHTML = `
                    <div class="avatar" style="background:${isMe ? '#3ba55d' : '#5865F2'}"></div>
                    <div class="msg-body">
                        <div class="msg-user">${isMe ? 'You' : ('User #' + data.sender)}</div>
                        <div class="msg-text">${data.content}</div>
                    </div>
                `;
            }
            area.appendChild(msg);
            area.scrollTop = area.scrollHeight;
        }

        // ─── WebRTC Voice & Video Implementation ──────────────────────────
        let peerConn = null;
        let localStream = null;

        const rtcConfig = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

        async function toggleVoice() {
            const btn = document.getElementById('voice-btn');
            if (!wsVoice) {
                try {
                    localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    wsVoice = new WebSocket(`${protocol}//${window.location.host}/ws/voice/${activeRoom}/${currentUser.id}?username=${currentUser.username}`);
                    
                    wsVoice.onopen = () => {
                        btn.classList.add('active');
                        appendMessage({type: 'system', content: 'Voice channel joined. (Real-time signaling active)'});
                    };

                    wsVoice.onmessage = async (e) => {
                        const signal = JSON.parse(e.data);
                        handleSignaling(signal, wsVoice);
                    };

                    wsVoice.onclose = () => {
                        btn.classList.remove('active');
                        if (peerConn) peerConn.close();
                        if (localStream) localStream.getTracks().forEach(t => t.stop());
                        wsVoice = null;
                    };
                } catch (err) { alert('Could not access microphone'); }
            } else {
                wsVoice.close();
            }
        }

        async function toggleVideo() {
            const btn = document.getElementById('video-btn');
            const grid = document.getElementById('video-grid');
            if (!wsVideo) {
                try {
                    localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    wsVideo = new WebSocket(`${protocol}//${window.location.host}/ws/video/${activeRoom}/${currentUser.id}?username=${currentUser.username}`);
                    
                    grid.style.display = 'grid';
                    grid.innerHTML = `<div class="video-box" id="local-vbox">
                        <video id="localVideo" autoplay muted playsinline style="width:100%; border-radius:4px;"></video>
                        <div class="video-label">You</div>
                    </div>`;
                    document.getElementById('localVideo').srcObject = localStream;

                    wsVideo.onopen = () => {
                        btn.classList.add('active');
                        appendMessage({type: 'system', content: 'Video call started.'});
                    };

                    wsVideo.onmessage = async (e) => {
                        const signal = JSON.parse(e.data);
                        handleSignaling(signal, wsVideo);
                    };

                    wsVideo.onclose = () => {
                        btn.classList.remove('active');
                        grid.style.display = 'none';
                        if (peerConn) peerConn.close();
                        if (localStream) localStream.getTracks().forEach(t => t.stop());
                        wsVideo = null;
                    };
                } catch (err) { alert('Could not access camera/mic'); }
            } else {
                wsVideo.close();
            }
        }

        async function handleSignaling(signal, ws) {
            if (signal.type === 'video_participants' || signal.type === 'voice_participants') return;

            if (!peerConn) {
                peerConn = new RTCPeerConnection(rtcConfig);
                localStream.getTracks().forEach(track => peerConn.addTrack(track, localStream));
                
                peerConn.onicecandidate = (e) => {
                    if (e.candidate) ws.send(JSON.stringify({ type: 'ice', candidate: e.candidate }));
                };

                peerConn.ontrack = (e) => {
                    if (ws === wsVideo) {
                        let remoteVideo = document.getElementById('remoteVideo');
                        if (!remoteVideo) {
                            const vbox = document.createElement('div');
                            vbox.className = 'video-box';
                            vbox.innerHTML = `<video id="remoteVideo" autoplay playsinline style="width:100%; border-radius:4px;"></video><div class="video-label">Peer</div>`;
                            document.getElementById('video-grid').appendChild(vbox);
                            remoteVideo = document.getElementById('remoteVideo');
                        }
                        remoteVideo.srcObject = e.streams[0];
                    }
                };
            }

            if (signal.offer) {
                await peerConn.setRemoteDescription(new RTCSessionDescription(signal.offer));
                const answer = await peerConn.createAnswer();
                await peerConn.setLocalDescription(answer);
                ws.send(JSON.stringify({ answer: peerConn.localDescription }));
            } else if (signal.answer) {
                await peerConn.setRemoteDescription(new RTCSessionDescription(signal.answer));
            } else if (signal.candidate) {
                try { await peerConn.addIceCandidate(new RTCIceCandidate(signal.candidate)); } catch (e) {}
            }
        }
    </script>
</body>
</html>
"""
