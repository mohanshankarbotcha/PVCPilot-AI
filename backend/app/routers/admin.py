from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import User
from app.schemas.auth import UserOut
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

@router.get("/users", response_model=List[UserOut])
async def list_users(current_user: User = Depends(require_role(["factory_owner", "admin"]))):
    """
    Returns all registered users on the platform. Restricted to factory_owner or admin roles.
    """
    users = await User.find_all().to_list()
    # Beanie documents contain the MongoDB object id, so we map them to string for schema serialization
    res = []
    for u in users:
        u_dict = u.model_dump()
        u_dict["id"] = str(u.id)
        res.append(u_dict)
    return res
