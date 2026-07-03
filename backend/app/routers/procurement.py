from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from app.models.user import User
from app.models.procurement import Supplier, PurchaseOrder, POLineItem
from app.models.inventory import RawMaterial, InventoryTransaction
from app.schemas.procurement import SupplierCreate, SupplierOut, POCreate, POOut, POLineItemSchema
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/procurement", tags=["Procurement Management"])

@router.get("/suppliers", response_model=List[SupplierOut])
async def get_suppliers(current_user: User = Depends(get_current_user)):
    return await Supplier.find_all().to_list()

@router.post("/suppliers", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
async def create_supplier(sup_in: SupplierCreate, current_user: User = Depends(get_current_user)):
    new_sup = Supplier(
        supplier_code=sup_in.supplier_code,
        company_name=sup_in.company_name,
        contact_person=sup_in.contact_person,
        email=sup_in.email,
        phone=sup_in.phone,
        address=sup_in.address,
        material_categories=sup_in.material_categories,
        payment_terms=sup_in.payment_terms,
        lead_time_days=sup_in.lead_time_days,
        bank_details=sup_in.bank_details,
        gst_number=sup_in.gst_number,
        pan_number=sup_in.pan_number,
        is_preferred=sup_in.is_preferred
    )
    await new_sup.insert()
    return new_sup

@router.get("/suppliers/{id}/scorecard")
async def get_supplier_scorecard(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    sup = await Supplier.get(id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {
        "supplier_name": sup.company_name,
        "rating": sup.rating,
        "on_time_delivery_rate": sup.on_time_delivery_rate,
        "quality_rejection_rate": sup.quality_rejection_rate,
        "total_orders": sup.total_orders,
        "total_value_inr": sup.total_value
    }

@router.get("/purchase-orders", response_model=List[POOut])
async def get_purchase_orders(status: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {}
    if status:
        query["status"] = status
    return await PurchaseOrder.find(query).sort("-created_at").to_list()

@router.post("/purchase-orders", response_model=POOut, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(po_in: POCreate, current_user: User = Depends(get_current_user)):
    # Generate PO Number
    today_str = datetime.utcnow().strftime("%Y%m%d")
    count = await PurchaseOrder.find(PurchaseOrder.po_number.regex(f"^PO-{today_str}-")).count()
    po_number = f"PO-{today_str}-{(count + 1):03d}"

    # Calculate item values
    total_val = sum(item.quantity * item.unit_price for item in po_in.items)
    tax = total_val * 0.18  # 18% GST standard
    grand_total = total_val + tax

    # Map items to model items
    db_items = [
        POLineItem(
            material_id=item.material_id,
            material_sku=item.material_sku,
            material_name=item.material_name,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        )
        for item in po_in.items
    ]

    new_po = PurchaseOrder(
        po_number=po_number,
        supplier_id=po_in.supplier_id,
        items=db_items,
        total_value=total_val,
        tax_amount=tax,
        grand_total=grand_total,
        status="draft",
        payment_terms=po_in.payment_terms,
        expected_delivery=po_in.expected_delivery,
        delivery_address="PVCPilot Factory Gate, Sector 4, GIDC Industrial Estate",
        created_by=current_user.id,
        notes=po_in.notes
    )
    await new_po.insert()
    return new_po

@router.patch("/purchase-orders/{id}/approve", response_model=POOut)
async def approve_purchase_order(
    id: PydanticObjectId,
    current_user: User = Depends(require_role(["factory_owner", "procurement_manager", "admin"]))
):
    po = await PurchaseOrder.get(id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
        
    po.status = "sent"
    po.approved_by = current_user.id
    po.approved_at = datetime.utcnow()
    po.updated_at = datetime.utcnow()
    await po.save()
    return po

@router.get("/purchase-orders/{id}/approve")
@router.post("/purchase-orders/{id}/approve")
async def approve_purchase_order_fallback(
    id: str,
    current_user: User = Depends(require_role(["factory_owner", "procurement_manager", "admin"]))
):
    raise HTTPException(status_code=404, detail="Method Not Allowed for this route")

@router.patch("/purchase-orders/{id}/receive", response_model=POOut)
async def receive_purchase_order(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    po = await PurchaseOrder.get(id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
        
    if po.status == "delivered":
        raise HTTPException(status_code=400, detail="Purchase order is already received")

    po.status = "delivered"
    po.actual_delivery = datetime.utcnow()
    po.updated_at = datetime.utcnow()
    await po.save()

    # Replenish inventory stock for each item in the PO
    for item in po.items:
        material = await RawMaterial.get(item.material_id)
        if material:
            material.current_stock += item.quantity
            material.last_received = datetime.utcnow()
            await material.save()

            # Log Transaction
            tx = InventoryTransaction(
                material_id=material.id,
                material_sku=material.sku,
                material_type="raw_material",
                type="replenishment",
                quantity=item.quantity,
                unit=item.unit,
                reference=po.po_number,
                user_id=current_user.id
            )
            await tx.insert()
            
    # Update supplier stats
    supplier = await Supplier.get(po.supplier_id)
    if supplier:
        supplier.total_orders += 1
        supplier.total_value += po.total_value
        await supplier.save()

    return po
