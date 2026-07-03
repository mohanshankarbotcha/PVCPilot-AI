from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from beanie import PydanticObjectId

class RawMaterialOut(BaseModel):
    id: PydanticObjectId
    sku: str
    name: str
    category: str
    unit: str
    current_stock: float
    reorder_level: float
    reorder_quantity: float
    maximum_stock: float
    unit_cost: float
    total_value: float
    supplier_id: PydanticObjectId
    location: str
    last_received: Optional[datetime]
    expiry_date: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

class FinishedGoodOut(BaseModel):
    id: PydanticObjectId
    sku: str
    product_name: str
    pipe_diameter_mm: int
    pressure_class: str
    pipe_length_meters: float
    color: str
    standard: str
    available_quantity_meters: float
    reserved_quantity_meters: float
    warehouse_zone: str
    unit_price: float
    production_cost: float
    last_produced: Optional[datetime]

    class Config:
        from_attributes = True

class StockAdjustmentRequest(BaseModel):
    quantity: float
    operation: Optional[str] = None  # 'add' or 'subtract'
    type: Optional[str] = None       # 'receipt' or 'consumption'
    reference: Optional[str] = ""
    notes: Optional[str] = ""
