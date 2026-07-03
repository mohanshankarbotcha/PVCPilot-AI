from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class PartReplacement(BaseModel):
    part_name: str
    part_number: str
    quantity: int
    cost: float

class Machine(Document):
    machine_code: str
    name: str
    type: str  # 'extruder', 'cooling_tank', 'cutter', 'haul_off', 'belling', 'printing'
    manufacturer: str
    model: str
    installation_date: datetime
    capacity_kg_per_hour: float
    current_status: str  # 'running', 'idle', 'maintenance', 'fault', 'shutdown'
    health_score: float = 100.0  # 0-100
    oee: float = 100.0  # 0-100
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    total_runtime_hours: float = 0.0
    current_temperature_celsius: float = 0.0
    current_speed_rpm: float = 0.0
    current_pressure_bar: float = 0.0
    current_vibration_mm_s: float = 0.0
    power_consumption_kw: float = 0.0
    fault_codes: List[str] = []
    location: str
    assigned_operator: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "machines"
        indexes = [
            IndexModel([("machine_code", ASCENDING)], unique=True),
            IndexModel([("current_status", ASCENDING)]),
        ]

class MachineSensorReading(Document):
    machine_id: PydanticObjectId
    timestamp: datetime
    temperature_celsius: float
    speed_rpm: float
    pressure_bar: float
    vibration_mm_s: float
    power_kw: float
    output_kg_per_hour: float
    anomaly_detected: bool = False
    anomaly_type: Optional[str] = None

    class Settings:
        name = "machine_sensor_readings"
        indexes = [
            IndexModel([("machine_id", ASCENDING), ("timestamp", DESCENDING)]),
            IndexModel([("timestamp", DESCENDING)]),
        ]
        # In Beanie/Pymongo, timeseries collections are supported
        # pass extra parameters to create_collection via settings
        extra_collection_parameters = {
            "timeseries": {
                "timeField": "timestamp",
                "metaField": "machine_id",
                "granularity": "minutes"
            }
        }

class MaintenanceRecord(Document):
    machine_id: PydanticObjectId
    maintenance_type: str  # 'preventive', 'corrective', 'predictive', 'emergency'
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    status: str = "scheduled"  # 'scheduled', 'in_progress', 'completed', 'overdue', 'cancelled'
    technician_id: Optional[PydanticObjectId] = None
    description: str
    parts_replaced: List[PartReplacement] = []
    cost: float = 0.0
    downtime_hours: float = 0.0
    root_cause: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "maintenance_records"
        indexes = [
            IndexModel([("machine_id", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
        ]
