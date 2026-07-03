from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class MaterialAllocation(BaseModel):
    material_id: PydanticObjectId
    material_sku: str
    material_name: str
    allocated_qty: float
    unit: str

class WorkOrder(Document):
    order_number: str
    customer_order_id: Optional[PydanticObjectId] = None
    product_type: str = "uPVC Pipe"
    pipe_diameter_mm: int  # 63, 90, 110, 160, 200, 250
    pressure_class: str  # PN6, PN10, PN16
    quantity_meters: float
    produced_meters: float = 0.0
    machine_id: PydanticObjectId
    shift: str  # 'morning', 'afternoon', 'night'
    planned_start: datetime
    planned_end: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    status: str = "draft"  # 'draft', 'scheduled', 'in_progress', 'quality_check', 'completed', 'cancelled', 'delayed'
    priority: str = "medium"  # 'low', 'medium', 'high', 'critical'
    raw_materials_allocated: List[MaterialAllocation] = []
    quality_result: Optional[str] = None
    rejection_meters: float = 0.0
    notes: Optional[str] = ""
    created_by: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "work_orders"
        indexes = [
            IndexModel([("order_number", ASCENDING)], unique=True),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("planned_start", DESCENDING)]),
            IndexModel([("machine_id", ASCENDING)]),
        ]
