import asyncio
from datetime import datetime, timedelta
from app.utils.security import get_password_hash
from app.models.user import User
from app.models.machine import Machine, MachineSensorReading
from app.models.inventory import RawMaterial
from app.models.production import WorkOrder
from app.models.alert import Alert
from app.models.procurement import Supplier, Address, BankDetails

PASSWORD = "PVCPilot@2025"

async def seed_test_data():
    # 1. Clear tables
    await User.find_all().delete()
    await Machine.find_all().delete()
    await MachineSensorReading.find_all().delete()
    await RawMaterial.find_all().delete()
    await WorkOrder.find_all().delete()
    await Alert.find_all().delete()
    await Supplier.find_all().delete()

    # 2. Seed Users
    hashed_p = get_password_hash(PASSWORD)
    
    users = [
        User(email="owner@pvcpilot.com", password_hash=hashed_p, full_name="Owner User", role="factory_owner", department="Management", permissions=["view:all", "edit:all", "approve:all", "admin"]),
        User(email="operator@pvcpilot.com", password_hash=hashed_p, full_name="Operator User", role="operator", department="Production", permissions=["view:production_own"]),
        User(email="quality@pvcpilot.com", password_hash=hashed_p, full_name="Quality User", role="quality_engineer", department="Quality", permissions=["view:quality", "edit:quality", "approve:quality"]),
        User(email="purchase@pvcpilot.com", password_hash=hashed_p, full_name="Procurement User", role="procurement_manager", department="Procurement", permissions=["view:procurement", "edit:procurement", "approve:purchase_orders"]),
        User(email="sales@pvcpilot.com", password_hash=hashed_p, full_name="Sales User", role="sales_manager", department="Sales", permissions=["view:sales", "view:finance", "edit:sales", "approve:sales"]),
    ]
    for u in users:
        await u.insert()

    # 3. Seed 13 Machines
    machines_data = [
        ("EXT-01", "Twin Screw Extruder 01", "extruder", "Line 1", "running", 85.0, 78.5),
        ("EXT-02", "Twin Screw Extruder 02", "extruder", "Line 2", "running", 85.0, 78.5),
        ("EXT-03", "Twin Screw Extruder 03", "extruder", "Line 3", "running", 85.0, 78.5),
        ("EXT-04", "Twin Screw Extruder 04", "extruder", "Line 4", "running", 85.0, 78.5),
        ("EXT-05", "Twin Screw Extruder 05", "extruder", "Line 5", "running", 85.0, 78.5),
        ("EXT-06", "Twin Screw Extruder 06", "extruder", "Line 6", "fault", 42.0, 0.0),
        ("COOL-01", "Cooling Tank 01", "cooling", "Line 1-Cooling", "running", 85.0, 78.5),
        ("COOL-02", "Cooling Tank 02", "cooling", "Line 2-Cooling", "running", 85.0, 78.5),
        ("COOL-03", "Cooling Tank 03", "cooling", "Line 3-Cooling", "running", 85.0, 78.5),
        ("CUT-01", "Pipe Cutter 01", "cutter", "Line 1-Cutter", "running", 85.0, 78.5),
        ("CUT-02", "Pipe Cutter 02", "cutter", "Line 2-Cutter", "running", 85.0, 78.5),
        ("CUT-03", "Pipe Cutter 03", "cutter", "Line 3-Cutter", "running", 85.0, 78.5),
        ("CUT-04", "Pipe Cutter 04", "cutter", "Line 4-Cutter", "running", 85.0, 78.5),
    ]
    
    machines = []
    for code, name, m_type, loc, status, health, oee in machines_data:
        m = Machine(
            machine_code=code,
            name=name,
            type=m_type,
            manufacturer="Kabra",
            model="CT-01",
            installation_date=datetime(2023, 5, 10),
            capacity_kg_per_hour=350.0,
            current_status=status,
            health_score=health,
            oee=oee,
            last_maintenance=datetime.utcnow() - timedelta(days=20),
            next_maintenance=datetime.utcnow() + timedelta(days=10),
            location=loc,
            assigned_operator=None
        )
        await m.insert()
        machines.append(m)

    # 4. Seed Supplier
    sup = Supplier(
        supplier_code="SUP-TEST",
        company_name="Test Supplier",
        contact_person="John Doe",
        email="john@test.com",
        phone="9876543210",
        address=Address(street="Test St", city="Test City", state="Test State", postal_code="123456"),
        material_categories=["resin", "stabilizer"],
        bank_details=BankDetails(bank_name="Test Bank", account_number="1234567890", ifsc_code="IFSC123", branch="Test Branch"),
        gst_number="27AAAAA1111A1Z1",
        pan_number="ABCDE1234F"
    )
    await sup.insert()

    # 5. Seed Raw Materials
    materials = [
        RawMaterial(sku="RM-PVC-K67", name="PVC Resin K67", category="resin", unit="kg", current_stock=18500.0, reorder_level=10000.0, reorder_quantity=20000.0, maximum_stock=50000.0, unit_cost=85.0, supplier_id=sup.id, location="Zone-A1"),
        RawMaterial(sku="RM-STB-LAD", name="Lead Stabilizer (One Pack)", category="stabilizer", unit="kg", current_stock=2300.0, reorder_level=3000.0, reorder_quantity=5000.0, maximum_stock=10000.0, unit_cost=140.0, supplier_id=sup.id, location="Zone-B1"),
    ]
    for rm in materials:
        await rm.insert()

    # 6. Seed Work Orders
    # We create a template work order in draft status
    wo = WorkOrder(
        order_number="WO-2026-0001",
        product_type="uPVC Pipe",
        pipe_diameter_mm=90,
        pressure_class="PN10",
        quantity_meters=5000.0,
        produced_meters=0.0,
        machine_id=machines[0].id,
        shift="morning",
        status="draft",
        priority="high",
        planned_start=datetime.utcnow() + timedelta(hours=2),
        planned_end=datetime.utcnow() + timedelta(hours=10),
        created_at=datetime.utcnow(),
        created_by=users[0].id
    )
    await wo.insert()

    # Seed hourly sensor data for last 24h
    now = datetime.utcnow()
    for h in range(24):
        time = now - timedelta(hours=h)
        await MachineSensorReading(
            machine_id=machines[0].id,
            timestamp=time,
            temperature_celsius=190.0,
            speed_rpm=35.0,
            pressure_bar=130.0,
            vibration_mm_s=2.2,
            power_kw=80.0,
            output_kg_per_hour=250.0,
            anomaly_detected=False
        ).insert()

    print("Seeded integration test minimal database.")
