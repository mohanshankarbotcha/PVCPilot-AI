from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import AlertOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts Management"])

@router.get("", response_model=List[AlertOut])
async def get_alerts(
    severity: Optional[str] = None,
    is_acknowledged: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if severity:
        query["severity"] = severity
    if is_acknowledged is not None:
        query["is_acknowledged"] = is_acknowledged
        
    return await Alert.find(query).sort("-created_at").to_list()

@router.patch("/{id}/acknowledge", response_model=AlertOut)
async def acknowledge_alert(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    alert = await Alert.get(id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_acknowledged = True
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    await alert.save()
    return alert

@router.patch("/{id}/resolve", response_model=AlertOut)
async def resolve_alert(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    alert = await Alert.get(id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.is_acknowledged = True  # Auto-acknowledge resolved alerts
    await alert.save()
    return alert

@router.post("/bulk-acknowledge")
async def bulk_acknowledge(ids: List[PydanticObjectId], current_user: User = Depends(get_current_user)):
    for uid in ids:
        alert = await Alert.get(uid)
        if alert:
            alert.is_acknowledged = True
            alert.acknowledged_by = current_user.id
            alert.acknowledged_at = datetime.utcnow()
            await alert.save()
            
    return {"message": f"Successfully acknowledged {len(ids)} alerts."}
