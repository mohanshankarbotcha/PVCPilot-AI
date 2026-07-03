from datetime import datetime
from typing import Optional
from pydantic import Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class Alert(Document):
    alert_type: str  # 'machine_fault', 'low_stock', 'quality_failure', 'maintenance_due', 'production_delay', 'financial', 'safety', 'energy_spike', 'supplier_issue'
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    title: str
    message: str
    source: str  # agent or system name
    related_entity_id: Optional[str] = None  # machine_id, order_id, etc.
    related_entity_type: Optional[str] = None
    is_acknowledged: bool = False
    acknowledged_by: Optional[PydanticObjectId] = None
    acknowledged_at: Optional[datetime] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    notification_sent: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "alerts"
        indexes = [
            IndexModel([("alert_type", ASCENDING)]),
            IndexModel([("severity", ASCENDING)]),
            IndexModel([("is_acknowledged", ASCENDING)]),
            IndexModel([("is_resolved", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
        ]
