from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr, Field
from beanie import Document
from pymongo import IndexModel, ASCENDING

class User(Document):
    email: EmailStr
    password_hash: str
    full_name: str
    role: str  # 'factory_owner', 'plant_manager', 'quality_engineer', 'inventory_manager', 'procurement_manager', 'sales_manager', 'operator', 'admin'
    department: str
    phone: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    permissions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("role", ASCENDING)]),
        ]
