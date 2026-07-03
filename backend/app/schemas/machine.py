from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.models.machine import PartReplacement

class MachineOut(BaseModel):
    id: PydanticObjectId
    machine_code: str
    name: str
    type: str
    manufacturer: str
    model: str
    installation_date: datetime
    capacity_kg_per_hour: float
    current_status: str
    health_score: float
    oee: float
    last_maintenance: Optional[datetime]
    next_maintenance: Optional[datetime]
    total_runtime_hours: float
    current_temperature_celsius: float
    current_speed_rpm: float
    current_pressure_bar: float
    current_vibration_mm_s: float
    power_consumption_kw: float
    fault_codes: List[str]
    location: str
    assigned_operator: Optional[PydanticObjectId]

    class Config:
        from_attributes = True

class MachineSensorReadingOut(BaseModel):
    id: PydanticObjectId
    machine_id: PydanticObjectId
    timestamp: datetime
    temperature_celsius: float
    speed_rpm: float
    pressure_bar: float
    vibration_mm_s: float
    power_kw: float
    output_kg_per_hour: float
    anomaly_detected: bool
    anomaly_type: Optional[str]

    class Config:
        from_attributes = True

class MaintenanceRecordCreate(BaseModel):
    machine_id: PydanticObjectId
    maintenance_type: str
    scheduled_date: datetime
    description: str
    parts_replaced: List[PartReplacement] = []
    cost: float = 0.0
    downtime_hours: float = 0.0

class MaintenanceRecordOut(BaseModel):
    id: PydanticObjectId
    machine_id: PydanticObjectId
    maintenance_type: str
    scheduled_date: datetime
    completed_date: Optional[datetime]
    status: str
    technician_id: Optional[PydanticObjectId]
    description: str
    parts_replaced: List[PartReplacement]
    cost: float
    downtime_hours: float
    root_cause: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
