from datetime import datetime
from typing import Optional
from pydantic import Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class CostRecord(Document):
    category: str  # 'raw_material', 'energy', 'labor', 'overhead', 'maintenance', 'logistics'
    description: str
    amount: float
    date: datetime = Field(default_factory=datetime.utcnow)
    reference_id: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "cost_records"
        indexes = [
            IndexModel([("category", ASCENDING)]),
            IndexModel([("date", DESCENDING)]),
        ]
