from datetime import datetime
from typing import Optional
from pydantic import Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class EnergyReading(Document):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    machine_id: Optional[PydanticObjectId] = None
    department: str  # 'extrusion', 'mixing', 'quality', 'packaging', 'office'
    reading_kwh: float
    cost_per_kwh: float = 10.0  # ₹10/kWh standard
    total_cost: float = 0.0  # calculated: reading_kwh * cost_per_kwh
    shift: str  # 'morning', 'afternoon', 'night'
    demand_kva: float = 0.0
    power_factor: float = 0.95
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "energy_readings"
        indexes = [
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("machine_id", ASCENDING)]),
            IndexModel([("department", ASCENDING)]),
        ]

    async def before_save(self):
        self.total_cost = self.reading_kwh * self.cost_per_kwh
