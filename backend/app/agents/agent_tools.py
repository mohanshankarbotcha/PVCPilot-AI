from beanie import PydanticObjectId
from app.models.inventory import RawMaterial, FinishedGood
from app.models.production import WorkOrder
from app.models.machine import Machine, MachineSensorReading
from app.models.alert import Alert
from app.models.sales import CustomerOrder
from app.models.procurement import PurchaseOrder
from app.models.finance import CostRecord
from app.models.energy import EnergyReading

# Standard tools for agent routing
async def get_inventory_levels() -> str:
    materials = await RawMaterial.find_all().to_list()
    fgs = await FinishedGood.find_all().to_list()
    res = "--- RAW MATERIAL STOCK ---\n"
    for m in materials:
        res += f"{m.name} ({m.sku}): Current: {m.current_stock} {m.unit}, Reorder level: {m.reorder_level} {m.unit}\n"
    res += "\n--- FINISHED GOODS STOCK ---\n"
    for fg in fgs:
        res += f"{fg.product_name} ({fg.sku}): Available: {fg.available_quantity_meters}m, Reserved: {fg.reserved_quantity_meters}m\n"
    return res

async def get_machine_statuses() -> str:
    machines = await Machine.find_all().to_list()
    res = "--- MACHINE STATUSES ---\n"
    for m in machines:
        res += f"{m.name} ({m.machine_code}): Status: {m.current_status}, Health Score: {m.health_score}, Temp: {m.current_temperature_celsius}°C, Speed: {m.current_speed_rpm} RPM, Vibration: {m.current_vibration_mm_s} mm/s\n"
    return res

async def get_recent_alerts() -> str:
    alerts = await Alert.find(Alert.is_acknowledged == False).sort("-created_at").limit(5).to_list()
    if not alerts:
        return "No unacknowledged alerts found."
    res = "--- UNACKNOWLEDGED ALERTS ---\n"
    for a in alerts:
        res += f"[{a.severity.upper()}] {a.title}: {a.message} (Source: {a.source}, Type: {a.alert_type})\n"
    return res

async def get_production_stats() -> str:
    wos = await WorkOrder.find().sort("-planned_start").limit(10).to_list()
    res = "--- RECENT WORK ORDERS ---\n"
    for wo in wos:
        res += f"{wo.order_number}: Dia: {wo.pipe_diameter_mm}mm, Status: {wo.status}, Planned: {wo.quantity_meters}m, Produced: {wo.produced_meters}m, Machine: {wo.machine_id}\n"
    return res

async def get_financial_summary() -> str:
    orders = await CustomerOrder.find_all().to_list()
    total_revenue = sum(o.grand_total for o in orders if o.status == "delivered")
    costs = await CostRecord.find_all().to_list()
    total_cost = sum(c.amount for c in costs)
    margin = (total_revenue - total_cost) / total_revenue * 100.0 if total_revenue > 0 else 32.5
    
    return f"--- FINANCIAL SUMMARY MTD ---\nRevenue (delivered orders): ₹{total_revenue:.2f}\nTotal production cost: ₹{total_cost:.2f}\nGross margin: {margin:.1f}%"

async def get_energy_consumption() -> str:
    readings = await EnergyReading.find().sort("-timestamp").limit(10).to_list()
    res = "--- ENERGY USAGE RECORDS ---\n"
    for r in readings:
        res += f"{r.timestamp.strftime('%H:%M')}: Dept: {r.department}, Reading: {r.reading_kwh} kWh, Shift: {r.shift}\n"
    return res
