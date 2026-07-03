"""
Unit tests for OEE (Overall Equipment Effectiveness) calculation.
OEE = Availability × Performance × Quality
These tests verify the core manufacturing metric used across the entire platform.
"""
import pytest
from datetime import datetime, timedelta
from app.utils.oee_calculator import calculate_oee, OEEResult


class TestOEECalculator:

    def test_perfect_oee_returns_100(self):
        """A machine running at 100% availability, performance, and quality must return OEE = 100%"""
        result = calculate_oee(
            planned_minutes=480,     # 8-hour shift
            downtime_minutes=0,
            theoretical_output=1000,
            actual_output=1000,
            good_output=1000,
        )
        assert result.availability == 100.0
        assert result.performance == 100.0
        assert result.quality == 100.0
        assert result.oee == 100.0

    def test_realistic_oee_typical_pvc_extruder(self):
        """
        Typical PVC extruder: 45 min downtime in 8hr shift,
        running at 85% of theoretical, 96% quality pass rate.
        Expected OEE ≈ 72.5%
        """
        result = calculate_oee(
            planned_minutes=480,
            downtime_minutes=45,
            theoretical_output=1000,
            actual_output=850,
            good_output=816,        # 96% of 850
        )
        assert result.availability == pytest.approx(90.625, rel=0.01)
        assert result.performance == pytest.approx(85.0, rel=0.01)
        assert result.quality == pytest.approx(96.0, rel=0.01)
        assert result.oee == pytest.approx(73.97, rel=0.01)

    def test_oee_with_full_downtime_returns_zero(self):
        """Machine that was fully down for the shift must return availability = 0, OEE = 0"""
        result = calculate_oee(
            planned_minutes=480,
            downtime_minutes=480,
            theoretical_output=1000,
            actual_output=0,
            good_output=0,
        )
        assert result.availability == 0.0
        assert result.oee == 0.0

    def test_oee_cannot_exceed_100(self):
        """OEE must never be above 100% even with rounding errors"""
        result = calculate_oee(
            planned_minutes=480,
            downtime_minutes=0,
            theoretical_output=1000,
            actual_output=1001,     # Slightly over theoretical
            good_output=1001,
        )
        assert result.oee <= 100.0

    def test_oee_quality_defects_impact(self):
        """30% quality rejection must significantly drop OEE even with perfect availability and performance"""
        result = calculate_oee(
            planned_minutes=480,
            downtime_minutes=0,
            theoretical_output=1000,
            actual_output=1000,
            good_output=700,        # 30% rejected
        )
        assert result.quality == pytest.approx(70.0, rel=0.01)
        assert result.oee == pytest.approx(70.0, rel=0.01)

    def test_oee_result_type(self):
        """OEE function must return a typed OEEResult object"""
        result = calculate_oee(480, 60, 1000, 900, 882)
        assert isinstance(result, OEEResult)
        assert hasattr(result, 'availability')
        assert hasattr(result, 'performance')
        assert hasattr(result, 'quality')
        assert hasattr(result, 'oee')

    @pytest.mark.parametrize("planned,downtime,theoretical,actual,good,expected_oee", [
        (480, 0,   1000, 1000, 1000, 100.0),   # Perfect
        (480, 48,  1000, 900,  882,  79.38),   # Typical extruder
        (480, 96,  1000, 750,  750,  60.0),    # Heavy downtime
        (480, 240, 1000, 400,  380,  19.0),    # Very poor shift
        (240, 0,   500,  500,  495,  99.0),    # Half shift, near perfect
    ])
    def test_oee_parametric_cases(self, planned, downtime, theoretical, actual, good, expected_oee):
        result = calculate_oee(planned, downtime, theoretical, actual, good)
        assert result.oee == pytest.approx(expected_oee, rel=0.02)
