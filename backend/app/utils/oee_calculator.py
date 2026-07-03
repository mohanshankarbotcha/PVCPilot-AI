from pydantic import BaseModel

class OEEResult(BaseModel):
    availability: float
    performance: float
    quality: float
    oee: float

def calculate_oee(
    planned_minutes: float,
    downtime_minutes: float,
    theoretical_output: float,
    actual_output: float,
    good_output: float,
) -> OEEResult:
    """
    Calculates OEE metrics. Clamps each metric and overall OEE to a max of 100%.
    """
    # 1. Availability
    if planned_minutes <= 0:
        availability = 0.0
    else:
        run_minutes = planned_minutes - downtime_minutes
        availability = max(0.0, min(100.0, (run_minutes / planned_minutes) * 100.0))

    # 2. Performance
    if theoretical_output <= 0:
        performance = 0.0
    else:
        performance = max(0.0, min(100.0, (actual_output / theoretical_output) * 100.0))

    # 3. Quality
    if actual_output <= 0:
        quality = 0.0
    else:
        quality = max(0.0, min(100.0, (good_output / actual_output) * 100.0))

    # 4. Overall OEE
    oee = (availability / 100.0) * (performance / 100.0) * (quality / 100.0) * 100.0
    oee = max(0.0, min(100.0, oee))

    return OEEResult(
        availability=round(availability, 3),
        performance=round(performance, 3),
        quality=round(quality, 3),
        oee=round(oee, 2),
    )
