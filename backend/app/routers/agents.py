from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
from datetime import datetime

from app.models.user import User
from app.models.agent_log import AgentLog
from app.schemas.agent import ChatRequest
from app.agents.coordinator_agent import CoordinatorAgent
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/agents", tags=["AI Agents"])
coordinator = CoordinatorAgent()

@router.get("/status")
async def get_agent_status(current_user: User = Depends(get_current_user)):
    return [
        {"name": "Coordinator Agent", "status": "active", "last_action": "Delegated maintenance warning", "tasks_completed": 12},
        {"name": "Production Planning Agent", "status": "idle", "last_action": "Completed shift rescheduling", "tasks_completed": 8},
        {"name": "Procurement Agent", "status": "active", "last_action": "Calculated Lead Stabilizer EOQ", "tasks_completed": 5},
        {"name": "Inventory Agent", "status": "active", "last_action": "Updated warehouse zone F usage", "tasks_completed": 9},
        {"name": "Machine Health Agent", "status": "processing", "last_action": "Analyzing EXT-06 vibration levels", "tasks_completed": 14},
        {"name": "Quality Agent", "status": "idle", "last_action": "Approved inspection INS-0122", "tasks_completed": 7},
        {"name": "Sales Agent", "status": "idle", "last_action": "Analyzed Godrej order feasibility", "tasks_completed": 4},
        {"name": "Cost Agent", "status": "active", "last_action": "Calculated production cost margins", "tasks_completed": 6},
        {"name": "Energy Agent", "status": "active", "last_action": "Monitored shift power load factor", "tasks_completed": 11},
        {"name": "Executive Support Agent", "status": "idle", "last_action": "Created weekly board digest", "tasks_completed": 3}
    ]

@router.post("/chat")
async def chat_with_agent(req: ChatRequest, current_user: User = Depends(get_current_user)):
    # SSE Generator for streaming response natively from Gemini stream
    async def sse_generator():
        try:
            async for chunk in coordinator.stream_response(
                req.message, current_user, req.conversation_id or "conv_default"
            ):
                data = {"text": chunk, "conversation_id": req.conversation_id or "conv_default"}
                yield f"data: {json.dumps(data)}\n\n"
        except Exception as e:
            data = {"text": f"\n\n⚠️ Error: {str(e)}", "conversation_id": req.conversation_id or "conv_default"}
            yield f"data: {json.dumps(data)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@router.get("/activity-feed")
async def get_activity_feed(current_user: User = Depends(get_current_user)):
    logs = await AgentLog.find_all().sort("-created_at").limit(10).to_list()
    return {
        "activities": [
            {
                "agent_name": log.agent_name,
                "action": log.action,
                "created_at": log.created_at
            } for log in logs
        ]
    }
