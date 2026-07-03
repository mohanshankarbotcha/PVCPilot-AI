"""
Material Requirements Planning (MRP) unit tests.
Verifies that raw material calculations for different pipe diameters are correct.
This is critical: wrong MRP = production stoppage or waste.
"""
import pytest
from app.utils.mrp_calculator import calculate_mrp, MRPResult


class TestMRPCalculator:

    def test_mrp_63mm_pn10_basic(self):
        """
        63mm PN10 pipe: 1000m order should require ~285 kg PVC resin.
        Formula: 28.5 kg resin per 100m
        """
        result = calculate_mrp(
            pipe_diameter_mm=63,
            pressure_class='PN10',
            quantity_meters=1000,
        )
        assert result.pvc_resin_kg == pytest.approx(285.0, rel=0.05)

    def test_mrp_110mm_pn16_higher_resin(self):
        """
        110mm PN16 requires significantly more resin than 63mm PN10.
        Larger diameter + higher pressure = thicker wall = more material.
        """
        result_63 = calculate_mrp(63, 'PN10', 1000)
        result_110 = calculate_mrp(110, 'PN16', 1000)
        assert result_110.pvc_resin_kg > result_63.pvc_resin_kg * 2

    def test_mrp_includes_all_additives(self):
        """MRP must include all additives: stabilizer, CaCO3, lubricants, pigment"""
        result = calculate_mrp(90, 'PN10', 5000)
        assert result.stabilizer_kg > 0
        assert result.calcium_carbonate_kg > 0
        assert result.lubricant_kg > 0

    def test_mrp_scales_linearly(self):
        """Doubling quantity must double all material requirements"""
        result_1000 = calculate_mrp(90, 'PN10', 1000)
        result_2000 = calculate_mrp(90, 'PN10', 2000)
        assert result_2000.pvc_resin_kg == pytest.approx(result_1000.pvc_resin_kg * 2, rel=0.01)
        assert result_2000.stabilizer_kg == pytest.approx(result_1000.stabilizer_kg * 2, rel=0.01)

    def test_mrp_pressure_class_impacts_wall_thickness(self):
        """Higher pressure class = thicker wall = more material for same diameter"""
        result_pn6  = calculate_mrp(110, 'PN6',  1000)
        result_pn10 = calculate_mrp(110, 'PN10', 1000)
        result_pn16 = calculate_mrp(110, 'PN16', 1000)
        assert result_pn6.pvc_resin_kg < result_pn10.pvc_resin_kg < result_pn16.pvc_resin_kg

    def test_mrp_invalid_diameter_raises(self):
        """Non-standard diameter must raise ValueError"""
        with pytest.raises(ValueError, match="Unsupported pipe diameter"):
            calculate_mrp(75, 'PN10', 1000)

    def test_mrp_invalid_pressure_class_raises(self):
        """Invalid pressure class must raise ValueError"""
        with pytest.raises(ValueError, match="Invalid pressure class"):
            calculate_mrp(90, 'PN20', 1000)

    def test_mrp_zero_quantity_raises(self):
        """Zero quantity order should raise ValueError"""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            calculate_mrp(63, 'PN10', 0)
