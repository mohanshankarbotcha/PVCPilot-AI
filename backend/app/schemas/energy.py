from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from beanie import PydanticObjectId

class EnergyReadingCreate(BaseModel):
    machine_id: Optional[PydanticObjectId] = None
    department: str
    reading_kwh: float
    cost_per_kwh: float = 10.0
    shift: str
    demand_kva: float = 0.0
    power_factor: float = 0.95

class EnergyReadingOut(BaseModel):
    id: PydanticObjectId
    timestamp: datetime
    machine_id: Optional[PydanticObjectId]
    department: str
    reading_kwh: float
    cost_per_kwh: float
    total_cost: float
    shift: str
    demand_kva: float
    power_factor: float
    created_at: datetime

    class Config:
        from_attributes = True
