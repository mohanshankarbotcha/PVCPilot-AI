from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import manager
import json

router = APIRouter(tags=["Real-time Sync"])

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = Query("user_default"),
    topics: str = Query("machine_status,alerts")
):
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    await manager.connect(websocket, user_id, topic_list)
    try:
        while True:
            # Maintain connection alive and listen for client messages
            data = await websocket.receive_text()
            # Simple Echo or Custom Request Handler
            message = json.loads(data)
            await websocket.send_json({"status": "received", "data": message})
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
