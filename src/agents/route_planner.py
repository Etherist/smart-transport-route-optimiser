import logging
from typing import Dict, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Mock geocoding database (in production, use Google Maps API or similar)
# National coverage across all Australian states and territories
GEOCODE_MOCK = {
    # New South Wales (NSW)
    "Sydney, NSW": (-33.8688, 151.2093),
    "Newcastle, NSW": (-32.9282, 151.7594),
    "Wollongong, NSW": (-34.4244, 150.8931),
    "Central Coast, NSW": (-33.425, 151.3417),
    "Gosford, NSW": (-33.4256, 151.3412),
    "Melson, NSW": (-32.7323, 151.5612),
    "Newcastle, NSW": (-32.9282, 151.7594),
    "Wollongong, NSW": (-34.4244, 150.8931),
    "Albury, NSW": (-36.0732, 146.9135),
    "Wagga Wagga, NSW": (-35.1145, 147.3512),
    "Dubbo, NSW": (-32.2569, 148.6011),
    "Coffs Harbour, NSW": (-30.2963, 153.1094),
    "Port Macquarie, NSW": (-31.4308, 152.9083),
    "Broken Hill, NSW": (-31.9513, 141.4617),
    # Victoria (VIC)
    "Melbourne, VIC": (-37.8136, 144.9631),
    "Geelong, VIC": (-38.1499, 144.3617),
    "Ballarat, VIC": (-37.5622, 143.8503),
    "Bendigo, VIC": (-36.7570, 144.2794),
    "Mildura, VIC": (-34.1847, 142.1525),
    "Warrnambool, VIC": (-38.3890, 142.4860),
    # Queensland (QLD)
    "Brisbane, QLD": (-27.4698, 153.0251),
    "Gold Coast, QLD": (-28.0167, 153.4000),
    "Sunshine Coast, QLD": (-26.6500, 153.0667),
    "Toowoomba, QLD": (-27.5598, 151.9507),
    "Townsville, QLD": (-19.2590, 146.8169),
    "Cairns, QLD": (-16.9186, 145.7781),
    # South Australia (SA)
    "Adelaide, SA": (-34.9285, 138.6007),
    "Mount Gambier, SA": (-37.8328, 140.7657),
    "Port Augusta, SA": (-32.5030, 137.7755),
    "Whyalla, SA": (-33.0038, 137.5855),
    "Coober Pedy, SA": (-29.0136, 134.7544),
    # Western Australia (WA)
    "Perth, WA": (-31.9505, 115.8605),
    "Bunbury, WA": (-33.3271, 115.6414),
    "Geraldton, WA": (-28.7793, 114.6158),
    "Kalgoorlie, WA": (-30.7489, 121.4656),
    "Busselton, WA": (-33.6526, 115.3455),
    # Tasmania (TAS)
    "Hobart, TAS": (-42.8821, 147.3272),
    "Launceston, TAS": (-41.4333, 147.3447),
    "Devonport, TAS": (-41.1761, 146.3508),
    "Burnie, TAS": (-41.0572, 145.8872),
    # Northern Territory (NT)
    "Darwin, NT": (-12.4634, 130.8456),
    "Alice Springs, NT": (-23.6980, 133.8807),
    "Katherine, NT": (-14.4648, 132.2638),
    # Australian Capital Territory (ACT)
    "Canberra, ACT": (-35.2809, 149.1300)
}

# State/territory mapping from location name
STATE_FROM_LOCATION = {
    "NSW": ["Sydney", "Newcastle", "Wollongong", "Central Coast", "Gosford", "Melson",
            "Albury", "Wagga Wagga", "Dubbo", "Coffs Harbour", "Port Macquarie", "Broken Hill"],
    "VIC": ["Melbourne", "Geelong", "Ballarat", "Bendigo", "Mildura", "Warrnambool"],
    "QLD": ["Brisbane", "Gold Coast", "Sunshine Coast", "Toowoomba", "Townsville", "Cairns"],
    "SA": ["Adelaide", "Mount Gambier", "Port Augusta", "Whyalla", "Coober Pedy"],
    "WA": ["Perth", "Bunbury", "Geraldton", "Kalgoorlie", "Busselton"],
    "TAS": ["Hobart", "Launceston", "Devonport", "Burnie"],
    "NT": ["Darwin", "Alice Springs", "Katherine"],
    "ACT": ["Canberra"]
}

def plan_route(
    start_address: str,
    end_address: str,
    vehicle_type: str,
    delivery_window: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Validates and structures user input into a structured route request.

    Args:
        start_address: Starting location address
        end_address: Destination address
        vehicle_type: Type of vehicle (Truck, B-Double, Semi-Trailer)
        delivery_window: Optional delivery deadline

    Returns:
        Structured route request dictionary with coordinates and constraints

    Raises:
        ValueError: If addresses are invalid or vehicle type unsupported
    """
    try:
        # Validate vehicle type - comprehensive fleet coverage
        valid_vehicles = [
            "Rigid", "Truck", "Semi-Trailer", "B-Double", "B-Triple",
            "Tautliner", "Reefer", "Flatbed", "Dump Truck", "Tanker",
            "Livestock Carrier", "Car Carrier", "Container Hauler"
        ]
        if vehicle_type not in valid_vehicles:
            raise ValueError(f"Invalid vehicle type. Must be one of: {valid_vehicles}")

        # Geocode addresses (mock)
        start_coords = GEOCODE_MOCK.get(start_address)
        end_coords = GEOCODE_MOCK.get(end_address)

        if not start_coords or not end_coords:
            raise ValueError(
                f"Address not found in geocoding database. "
                f"Supported locations: {list(GEOCODE_MOCK.keys())}"
            )

        # Build structured request
        route_request = {
            "start": {
                "address": start_address,
                "lat": start_coords[0],
                "lng": start_coords[1]
            },
            "end": {
                "address": end_address,
                "lat": end_coords[0],
                "lng": end_coords[1]
            },
            "vehicle_type": vehicle_type,
            "delivery_window": delivery_window.isoformat() if delivery_window else None
        }

        logger.info(
            f"Route planned: {start_address} → {end_address} "
            f"({vehicle_type})"
        )
        return route_request

    except ValueError as e:
        logger.error(f"Route planning validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Route planning failed: {e}")
        raise
