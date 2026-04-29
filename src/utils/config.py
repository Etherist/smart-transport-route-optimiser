import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration manager for environment variables."""
    LIVE_TRAFFIC_API_KEY = os.getenv("LIVE_TRAFFIC_NSW_API_KEY", "mock_key")
    BOM_API_KEY = os.getenv("BOM_API_KEY", "mock_key")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    # File paths
    ROAD_NETWORK_PATH = "src/data/australia_road_network.json"
    VEHICLE_CONSTRAINTS_PATH = "src/data/vehicle_constraints.json"
    NHVR_RULES_PATH = "src/data/nhvr_rules.json"

    # Fuel and emissions constants
    FUEL_PRICE_AUD_PER_LITRE = 1.60
    CO2_PER_LITRE = 0.4  # kg CO2 per litre of diesel
