"""
Economic Order Quantity (EOQ) unit tests.
EOQ = sqrt(2 × Annual Demand × Order Cost / Holding Cost per unit)
Wrong EOQ = excess inventory or stock-outs in procurement.
"""
import pytest
from app.utils.eoq_calculator import calculate_eoq


class TestEOQCalculator:

    def test_eoq_pvc_resin_basic(self):
        """
        PVC Resin K67:
        Annual demand: 120,000 kg
        Order cost: ₹5,000 per order (logistics, admin)
        Holding cost: ₹2 per kg per year
        Expected EOQ: sqrt(2 × 120000 × 5000 / 2) = 24,495 kg ≈ 24,500 kg
        """
        eoq = calculate_eoq(
            annual_demand_kg=120_000,
            order_cost_inr=5_000,
            holding_cost_per_kg_per_year=2.0,
        )
        assert eoq == pytest.approx(24_495, rel=0.02)

    def test_eoq_increases_with_higher_demand(self):
        """Higher annual demand must result in larger EOQ"""
        eoq_low  = calculate_eoq(60_000,  5_000, 2.0)
        eoq_high = calculate_eoq(120_000, 5_000, 2.0)
        assert eoq_high > eoq_low

    def test_eoq_decreases_with_higher_holding_cost(self):
        """Higher holding cost makes it better to order smaller, more frequent batches"""
        eoq_cheap_storage = calculate_eoq(120_000, 5_000, 1.0)
        eoq_expensive_storage = calculate_eoq(120_000, 5_000, 5.0)
        assert eoq_expensive_storage < eoq_cheap_storage

    def test_eoq_zero_demand_raises(self):
        """Zero annual demand should raise ValueError"""
        with pytest.raises(ValueError):
            calculate_eoq(0, 5_000, 2.0)

    def test_eoq_negative_values_raise(self):
        """Negative inputs must raise ValueError"""
        with pytest.raises(ValueError):
            calculate_eoq(-1000, 5_000, 2.0)
