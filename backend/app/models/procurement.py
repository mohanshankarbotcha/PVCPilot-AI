from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel, ASCENDING

class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "India"

class BankDetails(BaseModel):
    bank_name: str
    account_number: str
    ifsc_code: str
    branch: str

class POLineItem(BaseModel):
    material_id: PydanticObjectId
    material_sku: str
    material_name: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float

class Supplier(Document):
    supplier_code: str
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: Address
    material_categories: List[str] = []
    payment_terms: str = "NET30"  # NET30, NET60, COD
    lead_time_days: int = 7
    rating: float = 5.0
    on_time_delivery_rate: float = 100.0
    quality_rejection_rate: float = 0.0
    total_orders: int = 0
    total_value: float = 0.0
    is_active: bool = True
    is_preferred: bool = False
    bank_details: BankDetails
    gst_number: str
    pan_number: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "suppliers"
        indexes = [
            IndexModel([("supplier_code", ASCENDING)], unique=True),
            IndexModel([("company_name", ASCENDING)]),
        ]

class PurchaseOrder(Document):
    po_number: str
    supplier_id: PydanticObjectId
    items: List[POLineItem]
    total_value: float
    tax_amount: float
    grand_total: float
    status: str = "draft"  # 'draft', 'sent', 'acknowledged', 'partial', 'delivered', 'cancelled', 'closed'
    payment_terms: str
    expected_delivery: datetime
    actual_delivery: Optional[datetime] = None
    delivery_address: str
    approved_by: Optional[PydanticObjectId] = None
    approved_at: Optional[datetime] = None
    created_by: PydanticObjectId
    notes: Optional[str] = ""
    attachments: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "purchase_orders"
        indexes = [
            IndexModel([("po_number", ASCENDING)], unique=True),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("supplier_id", ASCENDING)]),
        ]
