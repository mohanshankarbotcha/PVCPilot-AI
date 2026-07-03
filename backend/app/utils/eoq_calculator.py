import math

def calculate_eoq(
    annual_demand_kg: float,
    order_cost_inr: float,
    holding_cost_per_kg_per_year: float,
) -> float:
    """
    Calculates the Economic Order Quantity (EOQ).
    EOQ = sqrt((2 * D * S) / H)
    """
    if annual_demand_kg <= 0 or order_cost_inr <= 0 or holding_cost_per_kg_per_year <= 0:
        raise ValueError("All inputs to EOQ calculator must be positive values greater than zero.")
        
    numerator = 2 * annual_demand_kg * order_cost_inr
    eoq = math.sqrt(numerator / holding_cost_per_kg_per_year)
    return eoq
