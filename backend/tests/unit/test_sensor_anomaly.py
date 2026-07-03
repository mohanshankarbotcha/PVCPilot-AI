"""
Sensor anomaly detection unit tests.
Critical for machine health monitoring — false negatives miss failures,
false positives cause unnecessary downtime.
"""
import pytest
from datetime import datetime, timedelta
from app.utils.sensor_anomaly import detect_anomaly, AnomalyResult


class TestSensorAnomalyDetection:

    def test_normal_temperature_no_anomaly(self):
        """Extruder temperature within range (175-215°C) should not trigger anomaly"""
        readings = [188.2, 190.5, 191.0, 189.8, 190.2, 188.6, 190.0] * 10
        result = detect_anomaly(readings, sensor_type='temperature', machine_type='extruder')
        assert result.is_anomaly is False

    def test_high_temperature_triggers_warning(self):
        """Temperature spike to 238°C should trigger WARNING anomaly (threshold: 235°C)"""
        # Normal readings then spike
        readings = [190.0] * 20 + [238.0, 240.0]
        result = detect_anomaly(readings, sensor_type='temperature', machine_type='extruder')
        assert result.is_anomaly is True
        assert result.severity == 'warning'

    def test_critical_temperature_triggers_critical(self):
        """Temperature above 260°C (critical threshold) must trigger CRITICAL alert"""
        readings = [190.0] * 20 + [265.0, 268.0, 270.0]
        result = detect_anomaly(readings, sensor_type='temperature', machine_type='extruder')
        assert result.is_anomaly is True
        assert result.severity == 'critical'

    def test_vibration_spike_detected(self):
        """Vibration spike from normal ~2 mm/s to 8 mm/s must be flagged"""
        readings = [2.1, 2.3, 2.0, 2.2, 2.1] * 10 + [8.2, 8.5, 8.1]
        result = detect_anomaly(readings, sensor_type='vibration', machine_type='extruder')
        assert result.is_anomaly is True
        assert result.anomaly_type in ('spike', 'threshold_exceeded')

    def test_gradual_drift_detected(self):
        """Gradual temperature drift (creeping upward over time) must be detected as trend anomaly"""
        # Rising from 190 to 228 over 30 readings
        readings = [190 + i for i in range(38)]
        result = detect_anomaly(readings, sensor_type='temperature', machine_type='extruder')
        assert result.is_anomaly is True
        assert result.anomaly_type in ('drift', 'trend')

    def test_single_outlier_not_flagged_as_anomaly(self):
        """A single blip reading should NOT be flagged — only sustained anomalies matter"""
        readings = [190.0] * 50
        readings[25] = 201.0   # Single outlier within warning range
        result = detect_anomaly(readings, sensor_type='temperature', machine_type='extruder')
        # Single blip within warning threshold should not be anomaly
        assert result.is_anomaly is False

    def test_cooling_tank_low_flow_anomaly(self):
        """Cooling tank flow rate dropping below minimum (30 L/min critical) must alert"""
        readings = [120.0] * 20 + [25.0, 22.0, 20.0]  # Flow drops critically low
        result = detect_anomaly(readings, sensor_type='flow_rate', machine_type='cooling')
        assert result.is_anomaly is True
        assert result.severity == 'critical'

    def test_anomaly_returns_timestamp(self):
        """Anomaly result must include detection timestamp"""
        readings = [190.0] * 20 + [270.0]
        result = detect_anomaly(readings, sensor_type='temperature', machine_type='extruder')
        assert result.detected_at is not None
