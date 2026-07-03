from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from beanie import PydanticObjectId

class MaterialAllocationSchema(BaseModel):
    material_id: PydanticObjectId
    material_sku: str
    material_name: str
    allocated_qty: float
    unit: str

class WorkOrderCreate(BaseModel):
    customer_order_id: Optional[PydanticObjectId] = None
    product_type: str = "uPVC Pipe"
    pipe_diameter_mm: int
    pressure_class: str
    quantity_meters: float
    machine_id: PydanticObjectId
    shift: str
    planned_start: datetime
    planned_end: datetime
    priority: str = "medium"
    notes: Optional[str] = ""

class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    produced_meters: Optional[float] = None
    rejection_meters: Optional[float] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    notes: Optional[str] = None
    machine_id: Optional[PydanticObjectId] = None
    priority: Optional[str] = None

class WorkOrderOut(BaseModel):
    id: PydanticObjectId
    order_number: str
    customer_order_id: Optional[PydanticObjectId]
    product_type: str
    pipe_diameter_mm: int
    pressure_class: str
    quantity_meters: float
    produced_meters: float
    machine_id: PydanticObjectId
    shift: str
    planned_start: datetime
    planned_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    status: str
    priority: str
    raw_materials_allocated: List[MaterialAllocationSchema]
    quality_result: Optional[str]
    rejection_meters: float
    notes: Optional[str]
    created_by: PydanticObjectId
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
