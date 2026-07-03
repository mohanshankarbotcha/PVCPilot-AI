from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from beanie import PydanticObjectId

class AlertOut(BaseModel):
    id: PydanticObjectId
    alert_type: str
    severity: str
    title: str
    message: str
    source: str
    related_entity_id: Optional[str]
    related_entity_type: Optional[str]
    is_acknowledged: bool
    acknowledged_by: Optional[PydanticObjectId]
    acknowledged_at: Optional[datetime]
    is_resolved: bool
    resolved_at: Optional[datetime]
    notification_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True
