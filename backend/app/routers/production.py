from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta
from typing import List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel

from app.models.user import User
from app.models.production import WorkOrder, MaterialAllocation
from app.models.inventory import RawMaterial
from app.schemas.production import WorkOrderCreate, WorkOrderUpdate, WorkOrderOut
from app.services.auth_service import get_current_user, require_role
from app.services.production_service import get_machine_chart_data

router = APIRouter(prefix="/production", tags=["Production Management"])

class StatusUpdate(BaseModel):
    status: Optional[str] = None

def get_mrp_requirements(diameter: int, quantity_meters: float) -> dict:
    # MRP formulas per 100m
    # 63mm: 28.5kg Resin, 1.2kg Stabilizer, 0.8kg CaCO3
    # 90mm: 42.8kg Resin, 1.8kg Stabilizer, 1.2kg CaCO3
    # 110mm: 58.4kg Resin, 2.4kg Stabilizer, 1.6kg CaCO3
    # 160mm: 112kg Resin, 4.6kg Stabilizer, 3.1kg CaCO3
    # Fallback to 110mm if not matched exactly
    mult = quantity_meters / 100.0
    if diameter <= 63:
        return {"resin": 28.5 * mult, "stabilizer": 1.2 * mult, "filler": 0.8 * mult}
    elif diameter <= 90:
        return {"resin": 42.8 * mult, "stabilizer": 1.8 * mult, "filler": 1.2 * mult}
    elif diameter <= 110:
        return {"resin": 58.4 * mult, "stabilizer": 2.4 * mult, "filler": 1.6 * mult}
    else:
        return {"resin": 112.0 * mult, "stabilizer": 4.6 * mult, "filler": 3.1 * mult}

@router.get("/work-orders", response_model=List[WorkOrderOut])
async def get_work_orders(
    status: Optional[str] = None,
    machine_id: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if status:
        query["status"] = status
    if machine_id:
        query["machine_id"] = PydanticObjectId(machine_id)
        
    orders = await WorkOrder.find(query).sort("-planned_start").limit(limit).to_list()
    return orders

@router.post("/work-orders", response_model=WorkOrderOut, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    wo_in: WorkOrderCreate,
    current_user: User = Depends(require_role(["factory_owner", "plant_manager", "admin"]))
):
    # Auto-generate order number
    today_str = datetime.utcnow().strftime("%Y%m%d")
    count = await WorkOrder.find({"order_number": {"$regex": f"^WO-{today_str}-"}}).count()
    order_number = f"WO-{today_str}-{(count + 1):04d}"

    # Calculate MRP Requirements
    reqs = get_mrp_requirements(wo_in.pipe_diameter_mm, wo_in.quantity_meters)

    # Fetch raw materials from DB to allocate
    resin = await RawMaterial.find_one(RawMaterial.sku == "RM-PVC-K67")
    stb = await RawMaterial.find_one(RawMaterial.sku == "RM-STB-LAD")
    caco3 = await RawMaterial.find_one(RawMaterial.sku == "RM-FLR-CACO3")

    allocations = []
    if resin:
        allocations.append(MaterialAllocation(material_id=resin.id, material_sku=resin.sku, material_name=resin.name, allocated_qty=reqs["resin"], unit="kg"))
    if stb:
        allocations.append(MaterialAllocation(material_id=stb.id, material_sku=stb.sku, material_name=stb.name, allocated_qty=reqs["stabilizer"], unit="kg"))
    if caco3:
        allocations.append(MaterialAllocation(material_id=caco3.id, material_sku=caco3.sku, material_name=caco3.name, allocated_qty=reqs["filler"], unit="kg"))

    import html
    escaped_notes = html.escape(wo_in.notes) if wo_in.notes else ""

    new_wo = WorkOrder(
        order_number=order_number,
        customer_order_id=wo_in.customer_order_id,
        product_type=wo_in.product_type,
        pipe_diameter_mm=wo_in.pipe_diameter_mm,
        pressure_class=wo_in.pressure_class,
        quantity_meters=wo_in.quantity_meters,
        produced_meters=0.0,
        machine_id=wo_in.machine_id,
        shift=wo_in.shift,
        planned_start=wo_in.planned_start,
        planned_end=wo_in.planned_end,
        status="draft",
        priority=wo_in.priority,
        raw_materials_allocated=allocations,
        notes=escaped_notes,
        created_by=current_user.id
    )

    await new_wo.insert()
    return new_wo

@router.get("/work-orders/{id}", response_model=WorkOrderOut)
async def get_work_order(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    wo = await WorkOrder.get(id)
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    return wo

@router.put("/work-orders/{id}", response_model=WorkOrderOut)
async def update_work_order(id: PydanticObjectId, wo_in: WorkOrderUpdate, current_user: User = Depends(get_current_user)):
    wo = await WorkOrder.get(id)
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    update_dict = wo_in.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(wo, k, v)
        
    wo.updated_at = datetime.utcnow()
    await wo.save()
    return wo

@router.patch("/work-orders/{id}/status", response_model=WorkOrderOut)
async def update_wo_status(
    id: PydanticObjectId,
    status_str: Optional[str] = None,
    status_update: Optional[StatusUpdate] = None,
    current_user: User = Depends(get_current_user)
):
    target_status = status_str
    if status_update and status_update.status:
        target_status = status_update.status

    if not target_status:
        raise HTTPException(status_code=400, detail="Missing status parameter")

    wo = await WorkOrder.get(id)
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Validate transitions
    VALID_TRANSITIONS = {
        "draft": {"scheduled", "cancelled"},
        "scheduled": {"in_progress", "cancelled"},
        "in_progress": {"completed", "delayed"},
        "delayed": {"in_progress", "completed", "cancelled"},
        "completed": set(),
        "cancelled": set()
    }
    
    current_status = wo.status or "draft"
    if target_status != current_status:
        allowed = VALID_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition from {current_status} to {target_status}"
            )

    wo.status = target_status
    if target_status == "in_progress" and not wo.actual_start:
        wo.actual_start = datetime.utcnow()
    elif target_status == "completed" and not wo.actual_end:
        wo.actual_end = datetime.utcnow()
        if wo.produced_meters == 0:
            wo.produced_meters = wo.quantity_meters
            
    wo.updated_at = datetime.utcnow()
    await wo.save()
    return wo

@router.get("/schedule")
async def get_production_schedule(current_user: User = Depends(get_current_user)):
    # Returns schedule in Gantt chart compatible structure
    work_orders = await WorkOrder.find(WorkOrder.status.in_(["scheduled", "in_progress"])).to_list()
    schedule_data = []
    for wo in work_orders:
        schedule_data.append({
            "id": str(wo.id),
            "order_number": wo.order_number,
            "machine_id": str(wo.machine_id),
            "diameter": wo.pipe_diameter_mm,
            "quantity": wo.quantity_meters,
            "start": wo.planned_start.isoformat(),
            "end": wo.planned_end.isoformat(),
            "status": wo.status,
            "priority": wo.priority
        })
    return schedule_data

@router.get("/planning/mrp")
async def get_mrp_report(
    diameter: Optional[int] = None,
    quantity_meters: Optional[float] = None,
    work_order_id: Optional[PydanticObjectId] = None,
    current_user: User = Depends(get_current_user)
):
    if work_order_id:
        wo = await WorkOrder.get(work_order_id)
        if not wo:
            raise HTTPException(status_code=404, detail="Work order not found")
        diameter = wo.pipe_diameter_mm
        quantity_meters = wo.quantity_meters

    if diameter is None or quantity_meters is None:
        raise HTTPException(status_code=400, detail="Missing parameters: diameter and quantity_meters, or work_order_id")

    reqs = get_mrp_requirements(diameter, quantity_meters)
    return {
        "diameter": diameter,
        "quantity_meters": quantity_meters,
        "requirements": [
            {"sku": "RM-PVC-K67", "name": "PVC Resin K67", "qty": reqs["resin"], "unit": "kg"},
            {"sku": "RM-STB-LAD", "name": "Lead Stabilizer (One Pack)", "qty": reqs["stabilizer"], "unit": "kg"},
            {"sku": "RM-FLR-CACO3", "name": "Calcium Carbonate (CaCO3)", "qty": reqs["filler"], "unit": "kg"}
        ]
    }

@router.get("/chart-data")
async def get_production_chart_data(
    machine: str = Query(...),
    period: str = Query("30D"),
    current_user: User = Depends(get_current_user),
):
    """
    Returns per-machine production chart data in both primary and secondary chart formats.
    The data structure adapts based on the machine type and chart needs.
    """
    days = {"1D": 1, "7D": 7, "30D": 30, "90D": 90}.get(period, 30)
    chart_data = await get_machine_chart_data(machine, days)
    return chart_data
