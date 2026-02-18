import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";
import Peer from "simple-peer";

const socket = io("http://localhost:5000");

function VoiceChannel() {
  const peersRef = useRef([]);
  const localStream = useRef();
  const [joined, setJoined] = useState(false);

  const joinCall = async () => {
    localStream.current = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });

    socket.emit("join-voice-room", "room1");
    setJoined(true);
  };

  useEffect(() => {
    socket.on("existing-users", (users) => {
      users.forEach((userId) => {
        const peer = createPeer(userId, localStream.current);
        peersRef.current.push({ peer, userId });
      });
    });

    socket.on("user-joined", (userId) => {
      const peer = addPeer(userId, localStream.current);
      peersRef.current.push({ peer, userId });
    });

    socket.on("webrtc-signal", ({ from, signal }) => {
      const item = peersRef.current.find((p) => p.userId === from);
      if (item) {
        item.peer.signal(signal);
      }
    });
  }, []);

  function createPeer(userToSignal, stream) {
    const peer = new Peer({
      initiator: true,
      trickle: false,
      stream,
    });

    peer.on("signal", (signal) => {
      socket.emit("webrtc-signal", {
        targetId: userToSignal,
        signal,
      });
    });

    peer.on("stream", (remoteStream) => {
      const audio = document.createElement("audio");
      audio.srcObject = remoteStream;
      audio.play();
    });

    return peer;
  }

  function addPeer(incomingId, stream) {
    const peer = new Peer({
      initiator: false,
      trickle: false,
      stream,
    });

    peer.on("signal", (signal) => {
      socket.emit("webrtc-signal", {
        targetId: incomingId,
        signal,
      });
    });

    peer.on("stream", (remoteStream) => {
      const audio = document.createElement("audio");
      audio.srcObject = remoteStream;
      audio.play();
    });

    return peer;
  }

  return (
    <div style={{ padding: 50 }}>
      {!joined ? (
        <button onClick={joinCall}>Join Voice Channel</button>
      ) : (
        <h2>🎤 You are in Voice Channel</h2>
      )}
    </div>
  );
}

export default VoiceChannel;
