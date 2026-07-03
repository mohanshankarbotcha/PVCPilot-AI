from fastapi import WebSocket
from typing import Dict, List, Set
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        # Maps subscription topic names to lists of connected WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        # Maps user ID strings to individual WebSockets
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str, subscriptions: List[str]):
        await websocket.accept()
        self.user_connections[user_id] = websocket
        for topic in subscriptions:
            self.active_connections[topic].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        for topic in list(self.active_connections.keys()):
            if websocket in self.active_connections[topic]:
                self.active_connections[topic].remove(websocket)

    async def send_personal_message(self, message: dict, user_id: str):
        websocket = self.user_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception:
                # Handle disconnected websocket
                self.disconnect(websocket, user_id)

    async def broadcast_to_topic(self, topic: str, message: dict):
        disconnected = set()
        for websocket in self.active_connections.get(topic, []):
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)
                
        # Clean up dead connections
        for ws in disconnected:
            for t in self.active_connections:
                if ws in self.active_connections[t]:
                    self.active_connections[t].remove(ws)
                    
manager = ConnectionManager()
