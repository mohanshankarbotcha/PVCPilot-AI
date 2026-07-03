from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING
from app.models.procurement import Address

class OrderLineItem(BaseModel):
    product_sku: str
    product_name: str
    quantity: float  # quantity in meters
    unit_price: float
    total_price: float

class Customer(Document):
    customer_code: str
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: Address
    segment: str  # 'builder', 'government', 'retail', 'industrial', 'agricultural', 'infrastructure'
    credit_limit: float = 0.0
    current_outstanding: float = 0.0
    lifetime_value: float = 0.0
    total_orders: int = 0
    payment_behavior: str = "good"  # 'excellent', 'good', 'average', 'poor'
    assigned_sales_rep: PydanticObjectId
    gst_number: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "customers"
        indexes = [
            IndexModel([("customer_code", ASCENDING)], unique=True),
            IndexModel([("company_name", ASCENDING)]),
            IndexModel([("segment", ASCENDING)]),
        ]

class CustomerOrder(Document):
    order_number: str
    customer_id: PydanticObjectId
    order_date: datetime = Field(default_factory=datetime.utcnow)
    required_delivery: datetime
    items: List[OrderLineItem] = []
    total_quantity_meters: float = 0.0
    total_value: float = 0.0
    tax_amount: float = 0.0
    grand_total: float = 0.0
    status: str = "pending"  # 'pending', 'confirmed', 'in_production', 'quality_check', 'ready', 'dispatched', 'delivered', 'cancelled'
    payment_status: str = "pending"  # 'pending', 'partial', 'paid', 'overdue'
    delivery_address: Address
    dispatch_date: Optional[datetime] = None
    tracking_number: Optional[str] = None
    sales_rep_id: PydanticObjectId
    notes: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "customer_orders"
        indexes = [
            IndexModel([("order_number", ASCENDING)], unique=True),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("customer_id", ASCENDING)]),
            IndexModel([("order_date", DESCENDING)]),
        ]
