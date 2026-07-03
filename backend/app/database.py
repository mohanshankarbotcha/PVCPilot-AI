from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings

# Import all Beanie Documents to initialize them
from app.models.user import User
from app.models.production import WorkOrder
from app.models.inventory import RawMaterial, FinishedGood, InventoryTransaction
from app.models.machine import Machine, MachineSensorReading, MaintenanceRecord
from app.models.procurement import Supplier, PurchaseOrder
from app.models.quality import QualityInspection
from app.models.sales import Customer, CustomerOrder
from app.models.finance import CostRecord
from app.models.energy import EnergyReading
from app.models.alert import Alert
from app.models.agent_log import AgentLog

async def init_db():
    # Initialize the AsyncIOMotorClient
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize beanie with the Documents
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            User,
            WorkOrder,
            RawMaterial,
            FinishedGood,
            InventoryTransaction,
            Machine,
            MachineSensorReading,
            MaintenanceRecord,
            Supplier,
            PurchaseOrder,
            QualityInspection,
            Customer,
            CustomerOrder,
            CostRecord,
            EnergyReading,
            Alert,
            AgentLog
        ]
    )
