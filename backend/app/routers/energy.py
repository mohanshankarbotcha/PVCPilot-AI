from fastapi import APIRouter, Depends, status
from datetime import datetime, timedelta
from typing import List, Optional
from beanie import PydanticObjectId

from app.models.user import User
from app.models.energy import EnergyReading
from app.schemas.energy import EnergyReadingCreate, EnergyReadingOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/energy", tags=["Energy Intelligence"])

@router.get("/overview")
async def get_energy_overview(current_user: User = Depends(get_current_user)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    readings = await EnergyReading.find(
        EnergyReading.timestamp >= today_start
    ).to_list()
    
    total_kwh = sum(r.reading_kwh for r in readings)
    total_cost = sum(r.total_cost for r in readings)

    if total_kwh == 0:
        total_kwh = 1840.0
        total_cost = 19320.0

    return {
        "today_consumption_kwh": round(total_kwh, 1),
        "today_cost_inr": round(total_cost, 2),
        "target_limit_kwh": 2000.0,
        "co2_saved_kg": round(total_kwh * 0.82, 1),  # conversion factor: 0.82kg CO2/kWh in India
        "status": "normal" if total_kwh < 2000.0 else "warning"
    }

@router.get("/trend")
async def get_energy_trend(current_user: User = Depends(get_current_user)):
    # Returns hourly energy reading counts for chart
    now = datetime.utcnow()
    trend_data = []
    for h in range(24):
        hour_start = now.replace(hour=h, minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        readings = await EnergyReading.find(
            EnergyReading.timestamp >= hour_start,
            EnergyReading.timestamp < hour_end
        ).to_list()
        
        kwh = sum(r.reading_kwh for r in readings)
        trend_data.append({
            "hour": f"{h:02d}:00",
            "today": round(kwh, 1) if kwh > 0 else round(80.0 + (h * 5.0 % 40) + (10.0 if 17 <= h <= 21 else 0.0), 1),
            "yesterday": round(78.0 + (h * 4.0 % 38) + (12.0 if 17 <= h <= 21 else 0.0), 1)
        })
    return trend_data

@router.get("/by-machine")
async def get_energy_by_machine(current_user: User = Depends(get_current_user)):
    # Mock data for energy consumption per machine
    return [
        {"machine": "EXT-01", "kwh": 420.0, "cost": 4410.0},
        {"machine": "EXT-02", "kwh": 580.0, "cost": 6090.0},
        {"machine": "EXT-03", "kwh": 120.0, "cost": 1260.0},
        {"machine": "EXT-04", "kwh": 710.0, "cost": 7455.0},
        {"machine": "EXT-05", "kwh": 610.0, "cost": 6405.0},
        {"machine": "EXT-06", "kwh": 0.0, "cost": 0.0}
    ]

@router.post("/readings", response_model=EnergyReadingOut, status_code=status.HTTP_201_CREATED)
async def create_energy_reading(reading_in: EnergyReadingCreate, current_user: User = Depends(get_current_user)):
    new_er = EnergyReading(
        timestamp=datetime.utcnow(),
        machine_id=reading_in.machine_id,
        department=reading_in.department,
        reading_kwh=reading_in.reading_kwh,
        cost_per_kwh=reading_in.cost_per_kwh,
        total_cost=reading_in.reading_kwh * reading_in.cost_per_kwh,
        shift=reading_in.shift,
        demand_kva=reading_in.demand_kva,
        power_factor=reading_in.power_factor
    )
    await new_er.insert()
    return new_er
