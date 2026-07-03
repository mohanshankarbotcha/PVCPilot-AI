from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from app.models.procurement import Address, BankDetails, POLineItem

class SupplierCreate(BaseModel):
    supplier_code: str
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: Address
    material_categories: List[str] = []
    payment_terms: str = "NET30"
    lead_time_days: int = 7
    bank_details: BankDetails
    gst_number: str
    pan_number: str
    is_preferred: bool = False

class SupplierOut(BaseModel):
    id: PydanticObjectId
    supplier_code: str
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: Address
    material_categories: List[str]
    payment_terms: str
    lead_time_days: int
    rating: float
    on_time_delivery_rate: float
    quality_rejection_rate: float
    total_orders: int
    total_value: float
    is_active: bool
    is_preferred: bool
    gst_number: str
    pan_number: str

    class Config:
        from_attributes = True

class POLineItemSchema(BaseModel):
    material_id: PydanticObjectId
    material_sku: str
    material_name: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float

class POCreate(BaseModel):
    supplier_id: PydanticObjectId
    items: List[POLineItemSchema]
    notes: Optional[str] = ""
    expected_delivery: datetime
    payment_terms: str

class POOut(BaseModel):
    id: PydanticObjectId
    po_number: str
    supplier_id: PydanticObjectId
    items: List[POLineItemSchema]
    total_value: float
    tax_amount: float
    grand_total: float
    status: str
    payment_terms: str
    expected_delivery: datetime
    actual_delivery: Optional[datetime]
    delivery_address: str
    approved_by: Optional[PydanticObjectId]
    approved_at: Optional[datetime]
    created_by: PydanticObjectId
    notes: Optional[str]
    attachments: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
