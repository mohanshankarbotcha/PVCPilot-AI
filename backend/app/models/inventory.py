from datetime import datetime
from typing import Optional
from pydantic import Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING

class RawMaterial(Document):
    sku: str
    name: str
    category: str  # 'resin', 'stabilizer', 'lubricant', 'pigment', 'filler', 'impact_modifier', 'packaging'
    unit: str  # kg, ton, litre, bag
    current_stock: float
    reorder_level: float
    reorder_quantity: float
    maximum_stock: float
    unit_cost: float
    total_value: float = 0.0  # computed in a save/before_event if needed, or stored directly
    supplier_id: PydanticObjectId
    location: str  # Warehouse zone: A1, B3, etc.
    last_received: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "raw_materials"
        indexes = [
            IndexModel([("sku", ASCENDING)], unique=True),
            IndexModel([("category", ASCENDING)]),
        ]

    async def before_save(self):
        self.total_value = self.current_stock * self.unit_cost

class FinishedGood(Document):
    sku: str
    product_name: str
    pipe_diameter_mm: int
    pressure_class: str
    pipe_length_meters: float  # Standard: 3m, 6m
    color: str
    standard: str  # IS 4985, IS 1239
    available_quantity_meters: float
    reserved_quantity_meters: float
    warehouse_zone: str
    unit_price: float
    production_cost: float
    last_produced: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "finished_goods"
        indexes = [
            IndexModel([("sku", ASCENDING)], unique=True),
        ]

class InventoryTransaction(Document):
    material_id: PydanticObjectId
    material_sku: str
    material_type: str  # 'raw_material', 'finished_good'
    type: str  # 'consumption', 'replenishment', 'adjustment', 'allocation'
    quantity: float
    unit: str
    reference: str  # WO-XXX, PO-XXX, ADJ-XXX
    user_id: Optional[PydanticObjectId] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "inventory_transactions"
        indexes = [
            IndexModel([("material_id", ASCENDING)]),
            IndexModel([("timestamp", ASCENDING)]),
        ]
