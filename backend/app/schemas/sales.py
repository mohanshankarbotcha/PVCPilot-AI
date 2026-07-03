from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from app.models.procurement import Address
from app.models.sales import OrderLineItem

class CustomerCreate(BaseModel):
    customer_code: str
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: Address
    segment: str
    credit_limit: float = 0.0
    gst_number: str

class CustomerOut(BaseModel):
    id: PydanticObjectId
    customer_code: str
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: Address
    segment: str
    credit_limit: float
    current_outstanding: float
    lifetime_value: float
    total_orders: int
    payment_behavior: str
    assigned_sales_rep: PydanticObjectId
    gst_number: str
    is_active: bool

    class Config:
        from_attributes = True

class CustomerOrderCreate(BaseModel):
    customer_id: PydanticObjectId
    required_delivery: datetime
    items: List[OrderLineItem]
    notes: Optional[str] = ""

class CustomerOrderOut(BaseModel):
    id: PydanticObjectId
    order_number: str
    customer_id: PydanticObjectId
    order_date: datetime
    required_delivery: datetime
    items: List[OrderLineItem]
    total_quantity_meters: float
    total_value: float
    tax_amount: float
    grand_total: float
    status: str
    payment_status: str
    delivery_address: Address
    dispatch_date: Optional[datetime]
    tracking_number: Optional[str]
    sales_rep_id: PydanticObjectId
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
