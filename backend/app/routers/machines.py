from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from pydantic import BaseModel

from app.models.user import User
from app.models.machine import Machine, MachineSensorReading, MaintenanceRecord, PartReplacement
from app.models.production import WorkOrder
from app.schemas.machine import MachineOut, MachineSensorReadingOut, MaintenanceRecordCreate, MaintenanceRecordOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/machines", tags=["Machine Health & OEE"])

class MachineStatusUpdate(BaseModel):
    status: Optional[str] = None
    reason: Optional[str] = None

@router.get("", response_model=List[MachineOut])
async def get_machines(current_user: User = Depends(get_current_user)):
    return await Machine.find_all().to_list()

@router.get("/{id}", response_model=MachineOut)
async def get_machine(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    m = await Machine.get(id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")
    return m

@router.get("/{id}/sensors", response_model=List[MachineSensorReadingOut])
async def get_sensor_readings(
    id: PydanticObjectId,
    hours: int = 24,
    current_user: User = Depends(get_current_user)
):
    start_time = datetime.utcnow() - timedelta(hours=hours)
    readings = await MachineSensorReading.find(
        MachineSensorReading.machine_id == id,
        MachineSensorReading.timestamp >= start_time
    ).sort("timestamp").to_list()
    return readings

@router.get("/{id}/maintenance-history", response_model=List[MaintenanceRecordOut])
async def get_maintenance_history(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    return await MaintenanceRecord.find(MaintenanceRecord.machine_id == id).sort("-scheduled_date").to_list()

@router.post("/{id}/maintenance", response_model=MaintenanceRecordOut, status_code=status.HTTP_201_CREATED)
async def log_maintenance(
    id: PydanticObjectId,
    rec_in: MaintenanceRecordCreate,
    current_user: User = Depends(get_current_user)
):
    m = await Machine.get(id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")

    new_rec = MaintenanceRecord(
        machine_id=id,
        maintenance_type=rec_in.maintenance_type,
        scheduled_date=rec_in.scheduled_date,
        completed_date=datetime.utcnow(),
        status="completed",
        technician_id=current_user.id,
        description=rec_in.description,
        parts_replaced=rec_in.parts_replaced,
        cost=rec_in.cost,
        downtime_hours=rec_in.downtime_hours
    )
    await new_rec.insert()

    # Update machine status and health score
    m.current_status = "idle"
    m.last_maintenance = datetime.utcnow()
    m.health_score = min(m.health_score + 15.0, 100.0)
    m.updated_at = datetime.utcnow()
    await m.save()

    return new_rec

@router.patch("/{id}/status", response_model=MachineOut)
async def update_machine_status(
    id: PydanticObjectId,
    status_str: Optional[str] = None,
    status_update: Optional[MachineStatusUpdate] = None,
    current_user: User = Depends(get_current_user),
):
    target_status = status_str
    if status_update and status_update.status:
        target_status = status_update.status
        
    if not target_status:
        raise HTTPException(status_code=400, detail="Missing status parameter")

    m = await Machine.get(id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")
        
    m.current_status = target_status
    m.updated_at = datetime.utcnow()
    await m.save()
    return m

@router.get("/{id}/oee")
async def get_machine_oee(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    m = await Machine.get(id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Dynamic OEE calculation based on last 30 days of Completed Work Orders
    start_date = datetime.utcnow() - timedelta(days=30)
    wos = await WorkOrder.find(
        WorkOrder.machine_id == id,
        WorkOrder.status == "completed",
        WorkOrder.actual_end >= start_date
    ).to_list()

    if not wos:
        # Default fallback OEE parameters
        return {
            "availability": 92.5 if m.current_status != "fault" else 0.0,
            "performance": 88.0 if m.current_status != "fault" else 0.0,
            "quality": 98.2 if m.current_status != "fault" else 0.0,
            "oee": 79.9 if m.current_status != "fault" else 0.0
        }

    total_planned_time = len(wos) * 8.0  # 8 hours planned per work order
    # Sum up actual downtime from maintenance records
    maint_recs = await MaintenanceRecord.find(
        MaintenanceRecord.machine_id == id,
        MaintenanceRecord.completed_date >= start_date
    ).to_list()
    total_downtime = sum(r.downtime_hours for r in maint_recs)

    availability = (total_planned_time - total_downtime) / total_planned_time if total_planned_time > 0 else 0.90
    availability = max(min(availability, 1.0), 0.0)

    # Performance: Actual Output / Planned Output
    total_planned_qty = sum(wo.quantity_meters for wo in wos)
    total_produced_qty = sum(wo.produced_meters for wo in wos)
    performance = total_produced_qty / total_planned_qty if total_planned_qty > 0 else 0.85
    performance = max(min(performance, 1.0), 0.0)

    # Quality: Good Output / Total Output
    total_rejected = sum(wo.rejection_meters for wo in wos)
    total_good = total_produced_qty - total_rejected
    quality = total_good / total_produced_qty if total_produced_qty > 0 else 0.98
    quality = max(min(quality, 1.0), 0.0)

    oee = availability * performance * quality * 100.0

    return {
        "availability": round(availability * 100.0, 1),
        "performance": round(performance * 100.0, 1),
        "quality": round(quality * 100.0, 1),
        "oee": round(oee, 1)
    }
