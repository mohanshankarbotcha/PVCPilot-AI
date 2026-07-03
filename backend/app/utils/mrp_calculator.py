from pydantic import BaseModel

class MRPResult(BaseModel):
    pvc_resin_kg: float
    stabilizer_kg: float
    calcium_carbonate_kg: float
    lubricant_kg: float
    pigment_kg: float

SUPPORTED_DIAMETERS = {63, 90, 110, 160, 200, 250}
SUPPORTED_PRESSURE_CLASSES = {"PN6", "PN10", "PN16"}

# Resin kg per meter for PN10
BASE_RESIN_COEFFICIENTS = {
    63: 0.285,
    90: 0.58,
    110: 0.85,
    160: 1.80,
    200: 2.80,
    250: 4.40,
}

PRESSURE_MULTIPLIERS = {
    "PN6": 0.65,
    "PN10": 1.00,
    "PN16": 1.55,
}

def calculate_mrp(
    pipe_diameter_mm: int,
    pressure_class: str,
    quantity_meters: float,
) -> MRPResult:
    """
    Calculates raw materials required for manufacturing PVC pipes based on diameter,
    pressure class and quantity.
    """
    if quantity_meters <= 0:
        raise ValueError("Quantity must be positive")
        
    if pipe_diameter_mm not in SUPPORTED_DIAMETERS:
        raise ValueError(f"Unsupported pipe diameter: {pipe_diameter_mm}")
        
    if pressure_class not in SUPPORTED_PRESSURE_CLASSES:
        raise ValueError(f"Invalid pressure class: {pressure_class}")

    base_coeff = BASE_RESIN_COEFFICIENTS[pipe_diameter_mm]
    mult = PRESSURE_MULTIPLIERS[pressure_class]

    resin_needed = base_coeff * mult * quantity_meters
    
    # PVC compound formulation ratios
    stabilizer = resin_needed * 0.03
    filler = resin_needed * 0.15
    lubricant = resin_needed * 0.012
    pigment = resin_needed * 0.004

    return MRPResult(
        pvc_resin_kg=round(resin_needed, 2),
        stabilizer_kg=round(stabilizer, 2),
        calcium_carbonate_kg=round(filler, 2),
        lubricant_kg=round(lubricant, 2),
        pigment_kg=round(pigment, 2),
    )
