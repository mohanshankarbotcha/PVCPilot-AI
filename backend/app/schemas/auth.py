from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role: str  # 'factory_owner', 'plant_manager', etc.
    department: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    full_name: str
    role: str
    department: str
    phone: Optional[str] = None
    permissions: List[str] = []
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    email: str
    full_name: str
    user: Optional[UserOut] = None
