from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class DefectRecord(BaseModel):
    defect_type: str  # 'dimensional_variance', 'surface_defect', 'pipe_warping', 'color_streaks', 'wall_thickness', 'other'
    quantity: float  # in meters or count
    description: Optional[str] = ""

class QualityInspection(Document):
    inspection_number: str
    work_order_id: PydanticObjectId
    batch_number: str
    product_sku: str
    inspector_id: PydanticObjectId
    inspection_date: datetime = Field(default_factory=datetime.utcnow)
    sample_size: int
    defects_found: int
    defect_types: List[DefectRecord] = []
    dimensions_ok: bool
    pressure_test_passed: bool
    visual_ok: bool
    weight_ok: bool
    result: str = "pending"  # 'pass', 'fail', 'conditional_pass', 'pending'
    rejection_meters: float = 0.0
    corrective_actions: Optional[str] = None  # CAPA description
    notes: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "quality_inspections"
        indexes = [
            IndexModel([("inspection_number", ASCENDING)], unique=True),
            IndexModel([("work_order_id", ASCENDING)]),
            IndexModel([("result", ASCENDING)]),
            IndexModel([("inspection_date", DESCENDING)]),
        ]
