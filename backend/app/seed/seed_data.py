import asyncio
import random
from datetime import datetime, timedelta, date
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.utils.security import get_password_hash
from app.models.user import User
from app.models.production import WorkOrder, MaterialAllocation
from app.models.inventory import RawMaterial, FinishedGood, InventoryTransaction
from app.models.machine import Machine, MachineSensorReading, MaintenanceRecord, PartReplacement
from app.models.procurement import Supplier, PurchaseOrder, POLineItem, Address, BankDetails
from app.models.quality import QualityInspection, DefectRecord
from app.models.sales import Customer, CustomerOrder, OrderLineItem
from app.models.finance import CostRecord
from app.models.energy import EnergyReading
from app.models.alert import Alert
from app.models.agent_log import AgentLog

# Seeding configurations
PASSWORD = "PVCPilot@2025"

SEED_USERS = [
    {"email": "owner@pvcpilot.com", "role": "factory_owner", "full_name": "Rajesh Kumar", "department": "Management", "permissions": ["view:all", "edit:all", "approve:all", "admin"]},
    {"email": "manager@pvcpilot.com", "role": "plant_manager", "full_name": "Suresh Reddy", "department": "Production", "permissions": ["view:all", "edit:production", "edit:machines", "approve:production"]},
    {"email": "quality@pvcpilot.com", "role": "quality_engineer", "full_name": "Priya Sharma", "department": "Quality", "permissions": ["view:quality", "edit:quality", "approve:quality"]},
    {"email": "inventory@pvcpilot.com", "role": "inventory_manager", "full_name": "Amit Patel", "department": "Inventory", "permissions": ["view:inventory", "edit:inventory", "approve:inventory"]},
    {"email": "purchase@pvcpilot.com", "role": "procurement_manager", "full_name": "Venkat Rao", "department": "Procurement", "permissions": ["view:procurement", "edit:procurement", "approve:purchase_orders"]},
    {"email": "sales@pvcpilot.com", "role": "sales_manager", "full_name": "Kavitha Nair", "department": "Sales", "permissions": ["view:sales", "view:finance", "edit:sales", "approve:sales"]},
    {"email": "operator@pvcpilot.com", "role": "operator", "full_name": "Ramu Yadav", "department": "Production", "permissions": ["view:production_own"]},
    {"email": "admin@pvcpilot.com", "role": "admin", "full_name": "Admin User", "department": "IT", "permissions": ["view:all", "edit:all", "approve:all", "admin"]},
]

SEED_SUPPLIERS = [
    {"supplier_code": "SUP-001", "company_name": "Finolex Industries", "contact_person": "M. Shah", "email": "contact@finolex.com", "phone": "022-24332211", "material_categories": ["resin"]},
    {"supplier_code": "SUP-002", "company_name": "Bodal Chemicals Ltd", "contact_person": "P. Patel", "email": "info@bodal.com", "phone": "079-25831684", "material_categories": ["stabilizer", "lubricant"]},
    {"supplier_code": "SUP-003", "company_name": "Gujarat Alkalies & Chemicals", "contact_person": "A. Mehta", "email": "sales@gacl.co.in", "phone": "0265-2232681", "material_categories": ["resin", "filler"]},
    {"supplier_code": "SUP-004", "company_name": "Pidilite Industries", "contact_person": "S. Joshi", "email": "procure@pidilite.com", "phone": "022-28357000", "material_categories": ["pigment", "impact_modifier"]},
    {"supplier_code": "SUP-005", "company_name": "Supreme Petrochem Ltd", "contact_person": "R. Sharma", "email": "supreme@spl.co.in", "phone": "022-67091900", "material_categories": ["lubricant", "packaging"]},
    {"supplier_code": "SUP-006", "company_name": "Tata Chemicals Ltd", "contact_person": "K. Sen", "email": "tata@tatachemicals.com", "phone": "022-66658282", "material_categories": ["filler"]},
    {"supplier_code": "SUP-007", "company_name": "Reliance Industries Ltd", "contact_person": "V. Ambani", "email": "poly@ril.com", "phone": "022-44770000", "material_categories": ["resin"]},
    {"supplier_code": "SUP-008", "company_name": "Balaji Amines Ltd", "contact_person": "D. Reddy", "email": "balaji@balajiamines.com", "phone": "040-27898206", "material_categories": ["stabilizer", "pigment"]}
]

SEED_RAW_MATERIALS = [
    # Category: resin
    {"sku": "RM-PVC-K67", "name": "PVC Resin K67", "category": "resin", "unit": "kg", "current_stock": 18500.0, "reorder_level": 10000.0, "reorder_quantity": 20000.0, "maximum_stock": 50000.0, "unit_cost": 85.0, "location": "Zone-A1"},
    {"sku": "RM-PVC-K57", "name": "PVC Resin K57", "category": "resin", "unit": "kg", "current_stock": 24000.0, "reorder_level": 8000.0, "reorder_quantity": 15000.0, "maximum_stock": 40000.0, "unit_cost": 90.0, "location": "Zone-A2"},
    # Category: stabilizer
    {"sku": "RM-STB-LAD", "name": "Lead Stabilizer (One Pack)", "category": "stabilizer", "unit": "kg", "current_stock": 2300.0, "reorder_level": 3000.0, "reorder_quantity": 5000.0, "maximum_stock": 10000.0, "unit_cost": 150.0, "location": "Zone-B1"},
    {"sku": "RM-STB-CAZN", "name": "Calcium Zinc Stabilizer", "category": "stabilizer", "unit": "kg", "current_stock": 3800.0, "reorder_level": 2000.0, "reorder_quantity": 4000.0, "maximum_stock": 8000.0, "unit_cost": 185.0, "location": "Zone-B2"},
    # Category: lubricant
    {"sku": "RM-LUB-STAC", "name": "Stearic Acid", "category": "lubricant", "unit": "kg", "current_stock": 1450.0, "reorder_level": 500.0, "reorder_quantity": 1000.0, "maximum_stock": 3000.0, "unit_cost": 110.0, "location": "Zone-C1"},
    {"sku": "RM-LUB-CAST", "name": "Calcium Stearate", "category": "lubricant", "unit": "kg", "current_stock": 980.0, "reorder_level": 400.0, "reorder_quantity": 800.0, "maximum_stock": 2000.0, "unit_cost": 120.0, "location": "Zone-C2"},
    {"sku": "RM-LUB-HDPE", "name": "HDPE Wax", "category": "lubricant", "unit": "kg", "current_stock": 740.0, "reorder_level": 300.0, "reorder_quantity": 500.0, "maximum_stock": 1500.0, "unit_cost": 140.0, "location": "Zone-C3"},
    # Category: filler
    {"sku": "RM-FLR-CACO3", "name": "Calcium Carbonate (CaCO3)", "category": "filler", "unit": "kg", "current_stock": 15600.0, "reorder_level": 5000.0, "reorder_quantity": 10000.0, "maximum_stock": 30000.0, "unit_cost": 18.0, "location": "Zone-D1"},
    # Category: pigment
    {"sku": "RM-PGM-TIO2", "name": "Titanium Dioxide (TiO2)", "category": "pigment", "unit": "kg", "current_stock": 1890.0, "reorder_level": 800.0, "reorder_quantity": 1500.0, "maximum_stock": 4000.0, "unit_cost": 210.0, "location": "Zone-E1"},
    {"sku": "RM-PGM-CARBON", "name": "Carbon Black", "category": "pigment", "unit": "kg", "current_stock": 620.0, "reorder_level": 200.0, "reorder_quantity": 500.0, "maximum_stock": 1200.0, "unit_cost": 160.0, "location": "Zone-E2"},
    # Category: impact_modifier
    {"sku": "RM-IMP-CPE", "name": "Chlorinated Polyethylene (CPE)", "category": "impact_modifier", "unit": "kg", "current_stock": 4200.0, "reorder_level": 1500.0, "reorder_quantity": 3000.0, "maximum_stock": 8000.0, "unit_cost": 135.0, "location": "Zone-F1"},
    # Packaging
    {"sku": "RM-PKG-STRAP", "name": "PET Strap Band", "category": "packaging", "unit": "bag", "current_stock": 240.0, "reorder_level": 50.0, "reorder_quantity": 100.0, "maximum_stock": 500.0, "unit_cost": 320.0, "location": "Zone-G1"},
]

# We will dynamically create products matching finished goods
SEED_FINISHED_GOODS = [
    {"sku": "FG-PIPE-63-PN10", "product_name": "uPVC Pipe 63mm PN10", "pipe_diameter_mm": 63, "pressure_class": "PN10", "pipe_length_meters": 6.0, "color": "Grey", "standard": "IS 4985", "available_quantity_meters": 12400.0, "reserved_quantity_meters": 1500.0, "warehouse_zone": "FG-Zone-A", "unit_price": 95.0, "production_cost": 65.0},
    {"sku": "FG-PIPE-90-PN10", "product_name": "uPVC Pipe 90mm PN10", "pipe_diameter_mm": 90, "pressure_class": "PN10", "pipe_length_meters": 6.0, "color": "Grey", "standard": "IS 4985", "available_quantity_meters": 9600.0, "reserved_quantity_meters": 800.0, "warehouse_zone": "FG-Zone-B", "unit_price": 140.0, "production_cost": 98.0},
    {"sku": "FG-PIPE-110-PN10", "product_name": "uPVC Pipe 110mm PN10", "pipe_diameter_mm": 110, "pressure_class": "PN10", "pipe_length_meters": 6.0, "color": "Grey", "standard": "IS 4985", "available_quantity_meters": 7800.0, "reserved_quantity_meters": 2400.0, "warehouse_zone": "FG-Zone-C", "unit_price": 195.0, "production_cost": 138.0},
    {"sku": "FG-PIPE-160-PN10", "product_name": "uPVC Pipe 160mm PN10", "pipe_diameter_mm": 160, "pressure_class": "PN10", "pipe_length_meters": 6.0, "color": "Grey", "standard": "IS 4985", "available_quantity_meters": 4200.0, "reserved_quantity_meters": 1200.0, "warehouse_zone": "FG-Zone-D", "unit_price": 380.0, "production_cost": 270.0},
]

SEED_CUSTOMERS = [
    {"customer_code": "CUST-001", "company_name": "Godrej Properties", "contact_person": "Anand G.", "email": "purchase@godrej.com", "phone": "022-61490000", "segment": "builder", "credit_limit": 5000000.0, "current_outstanding": 1200000.0, "lifetime_value": 45000000.0, "total_orders": 34, "payment_behavior": "excellent", "gst_number": "27AAACG1234F1ZA"},
    {"customer_code": "CUST-002", "company_name": "Larsen & Toubro Ltd", "contact_person": "Ramesh Kumar", "email": "r.kumar@lntecc.com", "phone": "044-22526000", "segment": "industrial", "credit_limit": 10000000.0, "current_outstanding": 4200000.0, "lifetime_value": 128000000.0, "total_orders": 89, "payment_behavior": "excellent", "gst_number": "33AAACL5678K2ZB"},
    {"customer_code": "CUST-003", "company_name": "Bangalore Water Supply (BWSSB)", "contact_person": "Executive Eng.", "email": "ee-procure@bwssb.gov.in", "phone": "080-22238888", "segment": "government", "credit_limit": 15000000.0, "current_outstanding": 8500000.0, "lifetime_value": 94000000.0, "total_orders": 41, "payment_behavior": "average", "gst_number": "29AAACB9012J1ZC"},
    {"customer_code": "CUST-004", "company_name": "Kisan Irrigation World", "contact_person": "Balaji Patil", "email": "kisan@balajiirrigation.com", "phone": "02562-224488", "segment": "agricultural", "credit_limit": 2000000.0, "current_outstanding": 450000.0, "lifetime_value": 15000000.0, "total_orders": 28, "payment_behavior": "good", "gst_number": "27AAABK9876Q2ZD"},
    {"customer_code": "CUST-005", "company_name": "City Hardwares Hub", "contact_person": "Hasmukh Bhai", "email": "cityhw@gmail.com", "phone": "0987654321", "segment": "retail", "credit_limit": 1000000.0, "current_outstanding": 180000.0, "lifetime_value": 8500000.0, "total_orders": 55, "payment_behavior": "good", "gst_number": "24AAACH7766M1ZE"}
]

SEED_MACHINES = [
    # 6 Twin Screw Extruders
    {"machine_code": "EXT-01", "name": "Twin Screw Extruder 63-90mm", "type": "extruder", "manufacturer": "Kolsite", "model": "KTE-63", "installation_date": datetime(2021, 5, 12), "capacity_kg_per_hour": 180.0, "current_status": "running", "location": "Line 1"},
    {"machine_code": "EXT-02", "name": "Twin Screw Extruder 90-110mm", "type": "extruder", "manufacturer": "Kolsite", "model": "KTE-90", "installation_date": datetime(2021, 8, 15), "capacity_kg_per_hour": 250.0, "current_status": "running", "location": "Line 2"},
    {"machine_code": "EXT-03", "name": "Twin Screw Extruder 110-160mm", "type": "extruder", "manufacturer": "Kabra Extrusiontechnik", "model": "KET-110", "installation_date": datetime(2022, 2, 20), "capacity_kg_per_hour": 320.0, "current_status": "idle", "location": "Line 3"},
    {"machine_code": "EXT-04", "name": "Twin Screw Extruder 160-250mm", "type": "extruder", "manufacturer": "Kabra Extrusiontechnik", "model": "KET-160", "installation_date": datetime(2022, 11, 5), "capacity_kg_per_hour": 450.0, "current_status": "running", "location": "Line 4"},
    {"machine_code": "EXT-05", "name": "Twin Screw Extruder High-Speed", "type": "extruder", "manufacturer": "Milacron", "model": "HT-110", "installation_date": datetime(2023, 6, 1), "capacity_kg_per_hour": 350.0, "current_status": "running", "location": "Line 5"},
    {"machine_code": "EXT-06", "name": "Twin Screw Extruder Heavy-Duty", "type": "extruder", "manufacturer": "Milacron", "model": "HT-250", "installation_date": datetime(2024, 1, 10), "capacity_kg_per_hour": 550.0, "current_status": "fault", "location": "Line 6"},
    # 3 Cooling Tanks
    {"machine_code": "COOL-01", "name": "Vacuum Spray Calibration Cooling Tank 1", "type": "cooling_tank", "manufacturer": "Kolsite", "model": "VCT-01", "installation_date": datetime(2021, 5, 12), "capacity_kg_per_hour": 300.0, "current_status": "running", "location": "Line 1-2"},
    {"machine_code": "COOL-02", "name": "Vacuum Spray Calibration Cooling Tank 2", "type": "cooling_tank", "manufacturer": "Kolsite", "model": "VCT-02", "installation_date": datetime(2022, 2, 20), "capacity_kg_per_hour": 400.0, "current_status": "running", "location": "Line 3-4"},
    {"machine_code": "COOL-03", "name": "Vacuum Spray Calibration Cooling Tank 3", "type": "cooling_tank", "manufacturer": "Milacron", "model": "VCT-03", "installation_date": datetime(2023, 6, 1), "capacity_kg_per_hour": 600.0, "current_status": "running", "location": "Line 5-6"},
    # 4 Pipe Cutters
    {"machine_code": "CUT-01", "name": "Automatic Planetary Saw Pipe Cutter 1", "type": "cutter", "manufacturer": "Kolsite", "model": "APC-01", "installation_date": datetime(2021, 5, 12), "capacity_kg_per_hour": 300.0, "current_status": "running", "location": "Line 1-2"},
    {"machine_code": "CUT-02", "name": "Automatic Planetary Saw Pipe Cutter 2", "type": "cutter", "manufacturer": "Kolsite", "model": "APC-02", "installation_date": datetime(2022, 2, 20), "capacity_kg_per_hour": 400.0, "current_status": "running", "location": "Line 3-4"},
    {"machine_code": "CUT-03", "name": "Automatic Planetary Saw Pipe Cutter 3", "type": "cutter", "manufacturer": "Milacron", "model": "APC-03", "installation_date": datetime(2023, 6, 1), "capacity_kg_per_hour": 600.0, "current_status": "running", "location": "Line 5-6"},
    {"machine_code": "CUT-04", "name": "High-Speed Bells Cutting Machine", "type": "cutter", "manufacturer": "Kabra", "model": "HSC-01", "installation_date": datetime(2024, 1, 15), "capacity_kg_per_hour": 500.0, "current_status": "idle", "location": "Line 4-Alt"},
]

async def generate_simulation_data():
    # 1. Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            User, WorkOrder, RawMaterial, FinishedGood, InventoryTransaction,
            Machine, MachineSensorReading, MaintenanceRecord, Supplier,
            PurchaseOrder, QualityInspection, Customer, CustomerOrder,
            CostRecord, EnergyReading, Alert, AgentLog
        ]
    )

    # 2. Clear collections
    collections_to_clear = [
        User, WorkOrder, RawMaterial, FinishedGood, InventoryTransaction,
        Machine, MachineSensorReading, MaintenanceRecord, Supplier,
        PurchaseOrder, QualityInspection, Customer, CustomerOrder,
        CostRecord, EnergyReading, Alert, AgentLog
    ]
    for col in collections_to_clear:
        await col.find_all().delete()

    print("Cleared existing DB.")

    # 3. Seed Users
    hashed_p = get_password_hash(PASSWORD)
    inserted_users = []
    for user_data in SEED_USERS:
        u = User(
            email=user_data["email"],
            password_hash=hashed_p,
            full_name=user_data["full_name"],
            role=user_data["role"],
            department=user_data["department"],
            permissions=user_data["permissions"]
        )
        await u.insert()
        inserted_users.append(u)
    print(f"Seeded {len(inserted_users)} Users.")

    # Find users for refs
    owner = next(u for u in inserted_users if u.role == "factory_owner")
    manager = next(u for u in inserted_users if u.role == "plant_manager")
    quality_eng = next(u for u in inserted_users if u.role == "quality_engineer")
    purchase_mgr = next(u for u in inserted_users if u.role == "procurement_manager")
    sales_mgr = next(u for u in inserted_users if u.role == "sales_manager")

    # 4. Seed Suppliers
    dummy_addr = Address(street="Industrial Area Phase 2", city="Mumbai", state="Maharashtra", postal_code="400001", country="India")
    dummy_bank = BankDetails(bank_name="State Bank of India", account_number="1234567890", ifsc_code="SBIN0001234", branch="Mumbai Main")
    inserted_suppliers = []
    for sup_data in SEED_SUPPLIERS:
        s = Supplier(
            supplier_code=sup_data["supplier_code"],
            company_name=sup_data["company_name"],
            contact_person=sup_data["contact_person"],
            email=sup_data["email"],
            phone=sup_data["phone"],
            address=dummy_addr,
            material_categories=sup_data["material_categories"],
            bank_details=dummy_bank,
            gst_number="27AAACS1234A1Z" + str(random.randint(0,9)),
            pan_number="ABCDE" + str(random.randint(1000,9999)) + "F"
        )
        await s.insert()
        inserted_suppliers.append(s)
    print(f"Seeded {len(inserted_suppliers)} Suppliers.")

    # 5. Seed Raw Materials
    inserted_materials = []
    for mat_data in SEED_RAW_MATERIALS:
        # Match supplier category
        possible_sups = [s for s in inserted_suppliers if mat_data["category"] in s.material_categories]
        sup = random.choice(possible_sups) if possible_sups else inserted_suppliers[0]

        rm = RawMaterial(
            sku=mat_data["sku"],
            name=mat_data["name"],
            category=mat_data["category"],
            unit=mat_data["unit"],
            current_stock=mat_data["current_stock"],
            reorder_level=mat_data["reorder_level"],
            reorder_quantity=mat_data["reorder_quantity"],
            maximum_stock=mat_data["maximum_stock"],
            unit_cost=mat_data["unit_cost"],
            total_value=mat_data["current_stock"] * mat_data["unit_cost"],
            supplier_id=sup.id,
            location=mat_data["location"]
        )
        await rm.insert()
        inserted_materials.append(rm)
    print(f"Seeded {len(inserted_materials)} Raw Materials.")

    # 6. Seed Finished Goods
    inserted_fg = []
    for fg_data in SEED_FINISHED_GOODS:
        fg = FinishedGood(
            sku=fg_data["sku"],
            product_name=fg_data["product_name"],
            pipe_diameter_mm=fg_data["pipe_diameter_mm"],
            pressure_class=fg_data["pressure_class"],
            pipe_length_meters=fg_data["pipe_length_meters"],
            color=fg_data["color"],
            standard=fg_data["standard"],
            available_quantity_meters=fg_data["available_quantity_meters"],
            reserved_quantity_meters=fg_data["reserved_quantity_meters"],
            warehouse_zone=fg_data["warehouse_zone"],
            unit_price=fg_data["unit_price"],
            production_cost=fg_data["production_cost"]
        )
        await fg.insert()
        inserted_fg.append(fg)
    print(f"Seeded {len(inserted_fg)} Finished Goods Products.")

    # 7. Seed Customers
    inserted_customers = []
    for cust_data in SEED_CUSTOMERS:
        c = Customer(
            customer_code=cust_data["customer_code"],
            company_name=cust_data["company_name"],
            contact_person=cust_data["contact_person"],
            email=cust_data["email"],
            phone=cust_data["phone"],
            address=dummy_addr,
            segment=cust_data["segment"],
            credit_limit=cust_data["credit_limit"],
            current_outstanding=cust_data["current_outstanding"],
            lifetime_value=cust_data["lifetime_value"],
            total_orders=cust_data["total_orders"],
            payment_behavior=cust_data["payment_behavior"],
            assigned_sales_rep=sales_mgr.id,
            gst_number=cust_data["gst_number"]
        )
        await c.insert()
        inserted_customers.append(c)
    print(f"Seeded {len(inserted_customers)} Customers.")

    # 8. Seed Machines
    inserted_machines = []
    for mach_data in SEED_MACHINES:
        m = Machine(
            machine_code=mach_data["machine_code"],
            name=mach_data["name"],
            type=mach_data["type"],
            manufacturer=mach_data["manufacturer"],
            model=mach_data["model"],
            installation_date=mach_data["installation_date"],
            capacity_kg_per_hour=mach_data["capacity_kg_per_hour"],
            current_status=mach_data["current_status"],
            health_score=85.0 if mach_data["current_status"] != "fault" else 42.0,
            oee=78.5 if mach_data["current_status"] != "fault" else 0.0,
            last_maintenance=datetime.utcnow() - timedelta(days=20),
            next_maintenance=datetime.utcnow() + timedelta(days=10),
            location=mach_data["location"],
            assigned_operator=manager.id
        )
        await m.insert()
        inserted_machines.append(m)
    print(f"Seeded {len(inserted_machines)} Machines.")

    # 9. 6-Month Manufacturing History Simulation
    print("Simulating 6 months of shift-based history...")
    start_time = datetime.utcnow() - timedelta(days=180)
    
    # Pre-fetch some resources for allocation
    resin_k67 = next(m for m in inserted_materials if m.sku == "RM-PVC-K67")
    resin_k57 = next(m for m in inserted_materials if m.sku == "RM-PVC-K57")
    lead_stb = next(m for m in inserted_materials if m.sku == "RM-STB-LAD")
    caco3 = next(m for m in inserted_materials if m.sku == "RM-FLR-CACO3")

    extruders = [m for m in inserted_machines if m.type == "extruder"]

    total_orders = 0
    total_inspections = 0
    total_wos = 0
    total_energy_readings = 0

    # Let's seed machine hourly sensor readings only for the last 30 days to keep the seeding script fast
    sensor_start_time = datetime.utcnow() - timedelta(days=30)

    # Daily simulation loop
    for day in range(180):
        current_date = start_time + timedelta(days=day)
        
        # Check weekdays (Sunday is off, Saturday is half day)
        is_sunday = current_date.weekday() == 6
        is_saturday = current_date.weekday() == 5
        
        if is_sunday:
            continue
            
        shifts = ["morning", "afternoon", "night"] if not is_saturday else ["morning"]
        
        for shift in shifts:
            # Shift timing details
            if shift == "morning":
                shift_hour_start = 6
            elif shift == "afternoon":
                shift_hour_start = 14
            else:
                shift_hour_start = 22
                
            shift_datetime = datetime(current_date.year, current_date.month, current_date.day, shift_hour_start, 0, 0)
            
            # Select machines to run this shift
            active_machines = extruders[:4] if is_saturday else extruders
            
            for ext in active_machines:
                if ext.machine_code == "EXT-06" and day > 165:
                    # Let EXT-06 be in fault for the last 15 days of simulation
                    continue
                    
                total_wos += 1
                # Pipe size choices
                pipe_dia = random.choice([63, 90, 110, 160])
                pressure = "PN10"
                quantity = random.randint(15, 30) * 100.0  # 1500 to 3000 meters
                
                # Material formulas per 100m of pipe
                # - 63mm: 28.5kg Resin, 1.2kg Stabilizer, 0.8kg CaCO3
                # - 90mm: 42.8kg Resin, 1.8kg Stabilizer, 1.2kg CaCO3
                # - 110mm: 58.4kg Resin, 2.4kg Stabilizer, 1.6kg CaCO3
                # - 160mm: 112kg Resin, 4.6kg Stabilizer, 3.1kg CaCO3
                if pipe_dia == 63:
                    resin_qty = (quantity / 100.0) * 28.5
                    stb_qty = (quantity / 100.0) * 1.2
                    cc_qty = (quantity / 100.0) * 0.8
                elif pipe_dia == 90:
                    resin_qty = (quantity / 100.0) * 42.8
                    stb_qty = (quantity / 100.0) * 1.8
                    cc_qty = (quantity / 100.0) * 1.2
                elif pipe_dia == 110:
                    resin_qty = (quantity / 100.0) * 58.4
                    stb_qty = (quantity / 100.0) * 2.4
                    cc_qty = (quantity / 100.0) * 1.6
                else:
                    resin_qty = (quantity / 100.0) * 112.0
                    stb_qty = (quantity / 100.0) * 4.6
                    cc_qty = (quantity / 100.0) * 3.1

                allocations = [
                    MaterialAllocation(material_id=resin_k67.id, material_sku=resin_k67.sku, material_name=resin_k67.name, allocated_qty=resin_qty, unit="kg"),
                    MaterialAllocation(material_id=lead_stb.id, material_sku=lead_stb.sku, material_name=lead_stb.name, allocated_qty=stb_qty, unit="kg"),
                    MaterialAllocation(material_id=caco3.id, material_sku=caco3.sku, material_name=caco3.name, allocated_qty=cc_qty, unit="kg")
                ]

                # Create Work Order
                wo_number = f"WO-{shift_datetime.strftime('%Y%m%d')}-{total_wos:04d}"
                produced = quantity if random.random() < 0.95 else (quantity * random.uniform(0.85, 0.99))
                rejection = (quantity - produced) if produced < quantity else 0.0

                wo = WorkOrder(
                    order_number=wo_number,
                    product_type="uPVC Pipe",
                    pipe_diameter_mm=pipe_dia,
                    pressure_class=pressure,
                    quantity_meters=quantity,
                    produced_meters=produced,
                    machine_id=ext.id,
                    shift=shift,
                    planned_start=shift_datetime,
                    planned_end=shift_datetime + timedelta(hours=8),
                    actual_start=shift_datetime + timedelta(minutes=random.randint(5, 15)),
                    actual_end=shift_datetime + timedelta(hours=7, minutes=random.randint(45, 59)),
                    status="completed" if day < 179 else "in_progress",
                    priority=random.choice(["low", "medium", "high"]),
                    raw_materials_allocated=allocations,
                    quality_result="pass" if rejection == 0.0 else "fail",
                    rejection_meters=rejection,
                    created_by=manager.id,
                    created_at=shift_datetime - timedelta(days=2),
                    updated_at=shift_datetime + timedelta(hours=8)
                )
                await wo.insert()

                # Deduct Raw Materials / Create Transaction
                for alloc in allocations:
                    tx = InventoryTransaction(
                        material_id=alloc.material_id,
                        material_sku=alloc.material_sku,
                        material_type="raw_material",
                        type="consumption",
                        quantity=alloc.allocated_qty,
                        unit="kg",
                        reference=wo_number,
                        user_id=manager.id,
                        timestamp=shift_datetime
                    )
                    await tx.insert()

                # Add Finished Pipe Transaction if passed
                if wo.status == "completed" and wo.quality_result == "pass":
                    # Match finished good product SKU
                    matching_fg = next((fg for fg in inserted_fg if fg.pipe_diameter_mm == pipe_dia), inserted_fg[0])
                    tx_fg = InventoryTransaction(
                        material_id=matching_fg.id,
                        material_sku=matching_fg.sku,
                        material_type="finished_good",
                        type="replenishment",
                        quantity=produced,
                        unit="meters",
                        reference=wo_number,
                        user_id=manager.id,
                        timestamp=shift_datetime + timedelta(hours=8)
                    )
                    await tx_fg.insert()

                # Create Quality Inspection record
                total_inspections += 1
                insp_number = f"INS-{shift_datetime.strftime('%Y%m%d')}-{total_inspections:04d}"
                
                # Check for defects if there is rejection
                defects = []
                if rejection > 0:
                    defects.append(DefectRecord(
                        defect_type=random.choice(['dimensional_variance', 'surface_defect', 'pipe_warping', 'color_streaks', 'wall_thickness']),
                        quantity=rejection,
                        description="Visual test failed during extrusion check."
                    ))

                insp = QualityInspection(
                    inspection_number=insp_number,
                    work_order_id=wo.id,
                    batch_number=f"BAT-{shift_datetime.strftime('%y%m%d')}-{pipe_dia}",
                    product_sku=f"FG-PIPE-{pipe_dia}-PN10",
                    inspector_id=quality_eng.id,
                    inspection_date=shift_datetime + timedelta(hours=7),
                    sample_size=10,
                    defects_found=len(defects),
                    defect_types=defects,
                    dimensions_ok=rejection == 0,
                    pressure_test_passed=rejection == 0,
                    visual_ok=rejection == 0,
                    weight_ok=rejection == 0,
                    result="pass" if rejection == 0 else "fail",
                    rejection_meters=rejection,
                    corrective_actions="Recalibrated die thickness zone" if rejection > 0 else None,
                    created_at=shift_datetime + timedelta(hours=8)
                )
                await insp.insert()

            # Record Energy Reading
            # Extruder averages 250 kWh/ton of pipe. Average output is ~200 kg/hour = 1600kg/shift = 1.6 tons/shift = 400 kWh/shift.
            total_energy_readings += 1
            dept_kwh = random.uniform(350, 480) * len(active_machines)
            er = EnergyReading(
                timestamp=shift_datetime + timedelta(hours=8),
                department="extrusion",
                reading_kwh=dept_kwh,
                cost_per_kwh=10.5,
                total_cost=dept_kwh * 10.5,
                shift=shift,
                demand_kva=dept_kwh * 0.15,
                power_factor=0.96,
                created_at=shift_datetime + timedelta(hours=8)
            )
            await er.insert()

            # Seeding hourly sensor data for the last 30 days
            if shift_datetime >= sensor_start_time:
                for ext in active_machines:
                    for h in range(8):
                        sensor_time = shift_datetime + timedelta(hours=h)
                        # Normal vs Anomaly simulation
                        is_anomaly = ext.machine_code == "EXT-06" and random.random() < 0.15
                        
                        temp = random.uniform(170, 195) if not is_anomaly else random.uniform(225, 255)
                        vib = random.uniform(1.2, 3.4) if not is_anomaly else random.uniform(5.5, 8.8)
                        press = random.uniform(120, 155) if not is_anomaly else random.uniform(160, 205)
                        speed = random.uniform(30, 42)
                        pwr = random.uniform(70, 95)
                        
                        reading = MachineSensorReading(
                            machine_id=ext.id,
                            timestamp=sensor_time,
                            temperature_celsius=round(temp, 1),
                            speed_rpm=round(speed, 1),
                            pressure_bar=round(press, 1),
                            vibration_mm_s=round(vib, 2),
                            power_kw=round(pwr, 1),
                            output_kg_per_hour=ext.capacity_kg_per_hour * random.uniform(0.85, 0.98),
                            anomaly_detected=is_anomaly,
                            anomaly_type="high_temperature_vibration" if is_anomaly else None
                        )
                        await reading.insert()

                        # If anomaly detected, log an Alert!
                        if is_anomaly:
                            alt = Alert(
                                alert_type="machine_fault",
                                severity="critical" if vib > 7.0 or temp > 250 else "high",
                                title=f"Vibration / Temperature Spike on {ext.machine_code}",
                                message=f"Machine sensor reported abnormal temperature ({temp:.1f}°C) and vibration ({vib:.2f}mm/s).",
                                source="Machine Sensor Monitor Service",
                                related_entity_id=str(ext.id),
                                related_entity_type="machine",
                                is_acknowledged=day < 179,
                                created_at=sensor_time
                            )
                            await alt.insert()

        # Seed some Customer Orders & Sales
        # Every few days, generate a customer order
        if day % 6 == 0:
            total_orders += 1
            cust = random.choice(inserted_customers)
            co_number = f"CO-{current_date.strftime('%Y%m%d')}-{total_orders:04d}"
            
            # Select 1 to 3 items
            items = []
            order_sum = 0
            order_meters = 0
            for fg_item in random.sample(inserted_fg, random.randint(1, 2)):
                qty_m = random.randint(10, 50) * 100.0  # 1000 to 5000m
                tot_item_price = qty_m * fg_item.unit_price
                items.append(OrderLineItem(
                    product_sku=fg_item.sku,
                    product_name=fg_item.product_name,
                    quantity=qty_m,
                    unit_price=fg_item.unit_price,
                    total_price=tot_item_price
                ))
                order_sum += tot_item_price
                order_meters += qty_m
                
            tax = order_sum * 0.18  # 18% GST
            
            co = CustomerOrder(
                order_number=co_number,
                customer_id=cust.id,
                order_date=current_date,
                required_delivery=current_date + timedelta(days=random.randint(10, 20)),
                items=items,
                total_quantity_meters=order_meters,
                total_value=order_sum,
                tax_amount=tax,
                grand_total=order_sum + tax,
                status="delivered" if day < 170 else "confirmed",
                payment_status="paid" if day < 170 else "pending",
                delivery_address=cust.address,
                dispatch_date=current_date + timedelta(days=6) if day < 170 else None,
                sales_rep_id=sales_mgr.id,
                created_at=current_date
            )
            await co.insert()

            # Record Revenue Cost entries
            if co.status == "delivered":
                # Create cost records for tracking margin
                cost_of_production = order_sum * random.uniform(0.65, 0.72)
                
                # Material cost
                await CostRecord(
                    category="raw_material",
                    description=f"Raw material cost for order {co_number}",
                    amount=cost_of_production * 0.60,
                    date=co.dispatch_date or current_date,
                    reference_id=co.id
                ).insert()
                # Labor cost
                await CostRecord(
                    category="labor",
                    description=f"Production labor for order {co_number}",
                    amount=cost_of_production * 0.15,
                    date=co.dispatch_date or current_date,
                    reference_id=co.id
                ).insert()
                # Overhead cost
                await CostRecord(
                    category="overhead",
                    description=f"Plant overheads for order {co_number}",
                    amount=cost_of_production * 0.25,
                    date=co.dispatch_date or current_date,
                    reference_id=co.id
                ).insert()

        # Seed some Procurement Purchase Orders
        # Every 12 days, order stabilizers/resins
        if day % 12 == 0:
            sup = random.choice(inserted_suppliers)
            po_number = f"PO-{current_date.strftime('%Y%m%d')}-{random.randint(100, 999)}"
            
            # Select 1 material
            rm_item = random.choice([m for m in inserted_materials if sup.id == m.supplier_id])
            po_qty = rm_item.reorder_quantity
            item_val = po_qty * rm_item.unit_cost
            po_item = POLineItem(
                material_id=rm_item.id,
                material_sku=rm_item.sku,
                material_name=rm_item.name,
                quantity=po_qty,
                unit=rm_item.unit,
                unit_price=rm_item.unit_cost,
                total_price=item_val
            )
            
            po = PurchaseOrder(
                po_number=po_number,
                supplier_id=sup.id,
                items=[po_item],
                total_value=item_val,
                tax_amount=item_val * 0.18,
                grand_total=item_val * 1.18,
                status="delivered" if day < 172 else "sent",
                payment_terms=sup.payment_terms,
                expected_delivery=current_date + timedelta(days=sup.lead_time_days),
                actual_delivery=current_date + timedelta(days=sup.lead_time_days) if day < 172 else None,
                delivery_address="PVCPilot Factory Gate, Sector 4, GIDC Industrial Estate",
                approved_by=purchase_mgr.id,
                approved_at=current_date + timedelta(hours=4),
                created_by=purchase_mgr.id,
                created_at=current_date
            )
            await po.insert()

            if po.status == "delivered":
                # Create transactions for stock replenishment
                tx_rep = InventoryTransaction(
                    material_id=rm_item.id,
                    material_sku=rm_item.sku,
                    material_type="raw_material",
                    type="replenishment",
                    quantity=po_qty,
                    unit=rm_item.unit,
                    reference=po_number,
                    user_id=purchase_mgr.id,
                    timestamp=po.actual_delivery or current_date
                )
                await tx_rep.insert()

        # Seed Maintenance Records
        # Random breakdowns or preventive checks
        if day % 25 == 0:
            mch = random.choice(inserted_machines)
            rec = MaintenanceRecord(
                machine_id=mch.id,
                maintenance_type=random.choice(["preventive", "corrective"]),
                scheduled_date=current_date,
                completed_date=current_date + timedelta(hours=random.randint(2, 6)),
                status="completed",
                technician_id=manager.id,
                description="General inspection and calibration of heating nozzles.",
                parts_replaced=[PartReplacement(part_name="Nozzle band heater", part_number="BH-220V-450W", quantity=2, cost=1800.0)],
                cost=5600.0,
                downtime_hours=4.5,
                root_cause="Wear and tear",
                created_at=current_date
            )
            await rec.insert()

    # 10. Seed final system level alerts
    await Alert(
        alert_type="low_stock",
        severity="high",
        title="Lead Stabilizer below safety levels",
        message="Current stock of Lead Stabilizer (One Pack) is 2,300 kg (safety threshold: 3,000 kg). Expected exhaustion in 4 days.",
        source="Inventory Agent",
        related_entity_id=str(lead_stb.id),
        related_entity_type="raw_material",
        created_at=datetime.utcnow() - timedelta(hours=2)
    ).insert()

    await Alert(
        alert_type="quality_failure",
        severity="medium",
        title="First Pass Quality drop on EXT-04",
        message="Batch B-2247 reported 320m of pipe failing wall thickness standards. Production rate adjusted.",
        source="Quality Agent",
        related_entity_id=str(extruders[3].id),
        related_entity_type="machine",
        created_at=datetime.utcnow() - timedelta(hours=6)
    ).insert()

    print("Database seeding and 6-month simulation data generation successfully completed.")

if __name__ == "__main__":
    asyncio.run(generate_simulation_data())
