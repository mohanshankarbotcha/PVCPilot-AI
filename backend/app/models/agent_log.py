from datetime import datetime
from typing import Optional, Dict, List
from pydantic import Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class AgentLog(Document):
    agent_name: str
    action: str
    input_data: Dict = {}
    output_data: Dict = {}
    reasoning: Optional[str] = None
    tools_called: List[str] = []
    tokens_used: int = 0
    processing_time_ms: int = 0
    status: str = "success"  # 'success', 'partial', 'failed'
    error: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "agent_logs"
        indexes = [
            IndexModel([("agent_name", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
        ]
