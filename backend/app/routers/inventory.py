from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from app.models.user import User
from app.models.inventory import RawMaterial, FinishedGood, InventoryTransaction
from app.schemas.inventory import RawMaterialOut, FinishedGoodOut, StockAdjustmentRequest
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

@router.get("/raw-materials", response_model=List[RawMaterialOut])
async def get_raw_materials(category: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {}
    if category:
        query["category"] = category
    return await RawMaterial.find(query).to_list()

@router.get("/raw-materials/low-stock", response_model=List[RawMaterialOut])
async def get_low_stock(current_user: User = Depends(get_current_user)):
    return await RawMaterial.find({"$expr": {"$lt": ["$current_stock", "$reorder_level"]}}).to_list()

@router.post("/raw-materials/{id}/adjust", response_model=RawMaterialOut)
async def adjust_stock(
    id: PydanticObjectId, 
    req: StockAdjustmentRequest, 
    current_user: User = Depends(get_current_user)
):
    material = await RawMaterial.get(id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
        
    old_stock = material.current_stock
    op = req.operation
    if not op and req.type:
        if req.type == "receipt":
            op = "add"
        elif req.type == "consumption":
            op = "subtract"
            
    qty = req.quantity
    if qty < 0:
        op = "subtract"
        qty = abs(qty)
    elif qty > 0 and not op:
        op = "add"

    if op == "add":
        material.current_stock += qty
    elif op == "subtract":
        if material.current_stock < qty:
            raise HTTPException(status_code=400, detail="Insufficient stock for subtraction")
        material.current_stock -= qty
    else:
        raise HTTPException(status_code=400, detail="Invalid operation type. Use 'add' or 'subtract'.")
        
    material.updated_at = datetime.utcnow()
    await material.save()

    # Log inventory transaction
    tx = InventoryTransaction(
        material_id=material.id,
        material_sku=material.sku,
        material_type="raw_material",
        type="adjustment",
        quantity=qty if op == "add" else -qty,
        unit=material.unit,
        reference=req.reference,
        user_id=current_user.id
    )
    await tx.insert()
    
    return material

@router.get("/finished-goods", response_model=List[FinishedGoodOut])
async def get_finished_goods(current_user: User = Depends(get_current_user)):
    return await FinishedGood.find_all().to_list()

@router.get("/transactions")
async def get_transactions(limit: int = 50, current_user: User = Depends(get_current_user)):
    return await InventoryTransaction.find_all().sort("-timestamp").limit(limit).to_list()

@router.get("/valuation")
async def get_valuation(current_user: User = Depends(get_current_user)):
    materials = await RawMaterial.find_all().to_list()
    total_val = sum(m.current_stock * m.unit_cost for m in materials)
    return {
        "raw_materials_value": total_val,
        "finished_goods_value": 450000.0,  # mock FG value
        "currency": "INR",
        "total_valuation": total_val + 450000.0
    }

@router.get("/warehouse-map")
async def get_warehouse_map(current_user: User = Depends(get_current_user)):
    # Simulates zone usage stats
    return [
        {"zone": "A", "label": "Zone A: Resins", "capacity_pct": 74.0, "status": "warning"},
        {"zone": "B", "label": "Zone B: Stabilizers", "capacity_pct": 38.0, "status": "ok"},
        {"zone": "C", "label": "Zone C: Lubricants", "capacity_pct": 42.0, "status": "ok"},
        {"zone": "D", "label": "Zone D: Fillers", "capacity_pct": 88.0, "status": "warning"},
        {"zone": "E", "label": "Zone E: Pigments", "capacity_pct": 15.0, "status": "ok"},
        {"zone": "F", "label": "Zone F: Finished Goods", "capacity_pct": 92.0, "status": "critical"}
    ]
