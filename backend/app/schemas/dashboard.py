from pydantic import BaseModel
from typing import List, Dict, Any
from app.schemas.alert import AlertOut
from app.schemas.machine import MachineOut

class KPISummary(BaseModel):
    todays_production_tons: float
    active_work_orders: int
    machine_uptime_pct: float
    raw_material_stock_days: int
    revenue_mtd_lakhs: float
    quality_pass_rate_pct: float
    open_alerts: int
    energy_today_kwh: float

class DashboardOverviewResponse(BaseModel):
    kpis: KPISummary
    production_chart: List[Dict[str, Any]]
    machine_statuses: List[MachineOut]
    top_alerts: List[AlertOut]
    ai_recommendations: List[Dict[str, Any]]
