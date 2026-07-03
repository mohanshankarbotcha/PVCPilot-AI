from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.models.quality import DefectRecord

class QualityInspectionCreate(BaseModel):
    work_order_id: PydanticObjectId
    sample_size: int
    defects_found: int
    defect_types: List[DefectRecord] = []
    dimensions_ok: bool
    pressure_test_passed: bool
    visual_ok: bool
    weight_ok: bool
    result: str
    rejection_meters: float = 0.0
    corrective_actions: Optional[str] = None
    notes: Optional[str] = ""

class QualityInspectionOut(BaseModel):
    id: PydanticObjectId
    inspection_number: str
    work_order_id: PydanticObjectId
    batch_number: str
    product_sku: str
    inspector_id: PydanticObjectId
    inspection_date: datetime
    sample_size: int
    defects_found: int
    defect_types: List[DefectRecord]
    dimensions_ok: bool
    pressure_test_passed: bool
    visual_ok: bool
    weight_ok: bool
    result: str
    rejection_meters: float
    corrective_actions: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
