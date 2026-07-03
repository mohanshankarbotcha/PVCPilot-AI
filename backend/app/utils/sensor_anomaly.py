from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class AnomalyResult(BaseModel):
    is_anomaly: bool
    severity: Optional[str] = None
    anomaly_type: Optional[str] = None
    detected_at: datetime

def detect_anomaly(readings: List[float], sensor_type: str, machine_type: str) -> AnomalyResult:
    """
    Analyzes a time series of sensor readings to detect warning or critical anomalies.
    Supports temperature, vibration, and flow rate checks, and looks for threshold
    violations and gradual trends (drift).
    """
    now = datetime.utcnow()
    
    if not readings:
        return AnomalyResult(is_anomaly=False, detected_at=now)

    # 1. Check for gradual drift/trend
    if len(readings) >= 15:
        # Check if the last 15 elements are strictly increasing or drifting up
        last_15 = readings[-15:]
        is_drifting = True
        for i in range(1, len(last_15)):
            if last_15[i] <= last_15[i-1]:
                is_drifting = False
                break
        if is_drifting:
            return AnomalyResult(
                is_anomaly=True,
                severity="warning",
                anomaly_type="drift",
                detected_at=now
            )

    latest_val = readings[-1]

    # Helper: Check if a value is above thresholds
    if sensor_type == 'temperature' and machine_type == 'extruder':
        # Thresholds: Warning > 235, Critical > 260
        # Sustained check: at least last 2 elements must exceed threshold to avoid single blips
        warning_limit = 235.0
        critical_limit = 260.0
        
        if len(readings) >= 2 and all(v > critical_limit for v in readings[-2:]):
            return AnomalyResult(is_anomaly=True, severity="critical", anomaly_type="threshold_exceeded", detected_at=now)
        elif len(readings) >= 2 and all(v > warning_limit for v in readings[-2:]):
            return AnomalyResult(is_anomaly=True, severity="warning", anomaly_type="threshold_exceeded", detected_at=now)

    elif sensor_type == 'vibration' and machine_type == 'extruder':
        # Thresholds: Warning > 5.5, Critical > 8.0
        warning_limit = 5.5
        critical_limit = 8.0
        
        if len(readings) >= 2 and all(v > critical_limit for v in readings[-2:]):
            return AnomalyResult(is_anomaly=True, severity="critical", anomaly_type="spike", detected_at=now)
        elif len(readings) >= 2 and all(v > warning_limit for v in readings[-2:]):
            return AnomalyResult(is_anomaly=True, severity="warning", anomaly_type="spike", detected_at=now)

    elif sensor_type == 'flow_rate' and machine_type == 'cooling':
        # Lower limits: Critical < 30, Warning < 45
        warning_limit = 45.0
        critical_limit = 30.0
        
        if len(readings) >= 2 and all(v < critical_limit for v in readings[-2:]):
            return AnomalyResult(is_anomaly=True, severity="critical", anomaly_type="threshold_exceeded", detected_at=now)
        elif len(readings) >= 2 and all(v < warning_limit for v in readings[-2:]):
            return AnomalyResult(is_anomaly=True, severity="warning", anomaly_type="threshold_exceeded", detected_at=now)

    return AnomalyResult(is_anomaly=False, detected_at=now)
