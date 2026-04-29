import logging
from typing import List, Dict, Any
import random

logger = logging.getLogger(__name__)

# Comprehensive mock traffic incidents covering all Australian states/territories
# Based on known congestion hotspots, roadworks, and accident-prone areas

TRAFFIC_INCIDENTS = {
    "NSW": [
        {
            "type": "accident",
            "location": {"lat": -33.8523, "lng": 151.2108},
            "road": "M1 Pacific Motorway",
            "direction": "Northbound",
            "severity": "high",
            "delay_minutes": 30,
            "description": "Multi-vehicle collision near Sydney Harbour Bridge"
        },
        {
            "type": "roadworks",
            "location": {"lat": -33.7506, "lng": 151.0844},
            "road": "A1",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 15,
            "description": "Lane closures for resurfacing between Liverpool and Parramatta"
        },
        {
            "type": "congestion",
            "location": {"lat": -33.8700, "lng": 151.2000},
            "road": "M2 Hills Motorway",
            "direction": "Eastbound",
            "severity": "low",
            "delay_minutes": 5,
            "description": "Heavy traffic during peak hours"
        },
        {
            "type": "accident",
            "location": {"lat": -33.425, "lng": 151.3417},
            "road": "Pacific Highway",
            "direction": "Northbound",
            "severity": "medium",
            "delay_minutes": 20,
            "description": "Vehicle breakdown near Gosford"
        },
        {
            "type": "roadworks",
            "location": {"lat": -32.9282, "lng": 151.7594},
            "road": "M1",
            "direction": "Southbound",
            "severity": "medium",
            "delay_minutes": 10,
            "description": "Heavy vehicle checkpoint near Newcastle"
        },
        {
            "type": "congestion",
            "location": {"lat": -36.0732, "lng": 146.9135},
            "road": "Hume Highway",
            "direction": "Northbound",
            "severity": "medium",
            "delay_minutes": 12,
            "description": "Holiday traffic near Albury"
        }
    ],
    "VIC": [
        {
            "type": "accident",
            "location": {"lat": -37.8136, "lng": 144.9631},
            "road": "CityLink",
            "direction": "Northbound",
            "severity": "high",
            "delay_minutes": 25,
            "description": "Multi-vehicle pileup on Bolte Bridge"
        },
        {
            "type": "roadworks",
            "location": {"lat": -37.7500, "lng": 145.0500},
            "road": "EastLink",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 15,
            "description": "Lane closures for toll upgrades"
        },
        {
            "type": "congestion",
            "location": {"lat": -38.1499, "lng": 144.3617},
            "road": "Princes Highway",
            "direction": "Westbound",
            "severity": "low",
            "delay_minutes": 8,
            "description": "Heavy freight traffic near Geelong"
        },
        {
            "type": "accident",
            "location": {"lat": -37.5622, "lng": 143.8503},
            "road": "Western Highway",
            "direction": "Eastbound",
            "severity": "medium",
            "delay_minutes": 18,
            "description": "Truck rollover near Ballarat"
        },
        {
            "type": "flood",
            "location": {"lat": -34.1847, "lng": 142.1525},
            "road": "Sturt Highway",
            "direction": "Both",
            "severity": "high",
            "delay_minutes": 45,
            "description": "Road closed due to flooding near Mildura"
        }
    ],
    "QLD": [
        {
            "type": "accident",
            "location": {"lat": -27.4698, "lng": 153.0251},
            "road": "Pacific Motorway (M1)",
            "direction": "Northbound",
            "severity": "high",
            "delay_minutes": 35,
            "description": "Serious collision near Brisbane CBD"
        },
        {
            "type": "roadworks",
            "location": {"lat": -27.5598, "lng": 151.9507},
            "road": "Warrego Highway",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 20,
            "description": "Road widening project near Toowoomba"
        },
        {
            "type": "congestion",
            "location": {"lat": -28.0167, "lng": 153.4000},
            "road": "Pacific Motorway",
            "direction": "Southbound",
            "severity": "low",
            "delay_minutes": 10,
            "description": "Weekend holiday traffic on Gold Coast"
        },
        {
            "type": "accident",
            "location": {"lat": -16.9186, "lng": 145.7781},
            "road": "Captain Cook Highway",
            "direction": "Northbound",
            "severity": "medium",
            "delay_minutes": 25,
            "description": "Tourist vehicle incident near Cairns"
        },
        {
            "type": "cyclone_impact",
            "location": {"lat": -19.2590, "lng": 146.8169},
            "road": "Flinders Highway",
            "direction": "Both",
            "severity": "extreme",
            "delay_minutes": 180,
            "description": "Flooding and debris from Tropical Cyclone – road closed"
        }
    ],
    "SA": [
        {
            "type": "accident",
            "location": {"lat": -34.9285, "lng": 138.6007},
            "road": "South Eastern Freeway",
            "direction": "Eastbound",
            "severity": "high",
            "delay_minutes": 40,
            "description": "Truck brake failure incident near Adelaide Hills"
        },
        {
            "type": "roadworks",
            "location": {"lat": -35.2000, "lng": 138.9000},
            "road": "South Road",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 15,
            "description": "Grade separation construction"
        },
        {
            "type": "congestion",
            "location": {"lat": -32.5030, "lng": 137.7755},
            "road": "Stuart Highway",
            "direction": "Northbound",
            "severity": "low",
            "delay_minutes": 5,
            "description": "Heavy freight convoy causing delays"
        },
        {
            "type": "flood",
            "location": {"lat": -37.8328, "lng": 140.7657},
            "road": "Princes Highway",
            "direction": "Both",
            "severity": "high",
            "delay_minutes": 60,
            "description": "Bridge flooding near Mount Gambier"
        }
    ],
    "WA": [
        {
            "type": "accident",
            "location": {"lat": -31.9505, "lng": 115.8605},
            "road": "Mitchell Freeway",
            "direction": "Southbound",
            "severity": "medium",
            "delay_minutes": 20,
            "description": "Multi-vehicle collision in Perth CBD"
        },
        {
            "type": "roadworks",
            "location": {"lat": -32.0000, "lng": 115.8000},
            "road": "Kwinana Freeway",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 15,
            "description": "Lane resurfacing near Fremantle"
        },
        {
            "type": "congestion",
            "location": {"lat": -33.3271, "lng": 115.6414},
            "road": "South Western Highway",
            "direction": "Northbound",
            "severity": "low",
            "delay_minutes": 8,
            "description": "Peak hour congestion near Bunbury"
        },
        {
            "type": "bushfire",
            "location": {"lat": -31.5000, "lng": 116.0000},
            "road": "Great Eastern Highway",
            "direction": "Eastbound",
            "severity": "extreme",
            "delay_minutes": 240,
            "description": "Bushfire closures – road blocked"
        }
    ],
    "TAS": [
        {
            "type": "accident",
            "location": {"lat": -42.8821, "lng": 147.3272},
            "road": "Brooker Highway",
            "direction": "Northbound",
            "severity": "medium",
            "delay_minutes": 15,
            "description": "Vehicle breakdown near Hobart"
        },
        {
            "type": "roadworks",
            "location": {"lat": -41.4333, "lng": 147.3447},
            "road": "Midland Highway",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 12,
            "description": "Intersection upgrades near Launceston"
        },
        {
            "type": "flood",
            "location": {"lat": -41.1761, "lng": 146.3508},
            "road": "Bass Highway",
            "direction": "Both",
            "severity": "high",
            "delay_minutes": 90,
            "description": "Bridge flooding near Devonport"
        }
    ],
    "NT": [
        {
            "type": "accident",
            "location": {"lat": -12.4634, "lng": 130.8456},
            "road": "Stuart Highway",
            "direction": "Southbound",
            "severity": "medium",
            "delay_minutes": 30,
            "description": "Truck incident near Darwin"
        },
        {
            "type": "roadworks",
            "location": {"lat": -23.6980, "lng": 133.8807},
            "road": "Stuart Highway",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 20,
            "description": "Road resealing near Alice Springs"
        },
        {
            "type": "flood",
            "location": {"lat": -14.4648, "lng": 132.2638},
            "road": "Victoria Highway",
            "direction": "Both",
            "severity": "extreme",
            "delay_minutes": 300,
            "description": "Monsoon flooding – road closed"
        }
    ]
}

def fetch_traffic_incidents(region: str = "NSW") -> List[Dict[str, Any]]:
    """
    Fetches real-time traffic data for the specified region.
    (Mock implementation for demo)

    Args:
        region: Geographic region (e.g., "NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT")

    Returns:
        List of traffic incident dictionaries

    Note:
        In production, this would call Live Traffic APIs (e.g., Live Traffic NSW, VicRoads, QLD Traffic)
    """
    try:
        region = region.upper()
        if region in TRAFFIC_INCIDENTS:
            # Simulate random selection with optional variability
            # Return all incidents for demo consistency, but could be filtered
            logger.info(f"Fetched {len(TRAFFIC_INCIDENTS[region])} traffic incidents for {region}")
            return TRAFFIC_INCIDENTS[region].copy()

        logger.warning(f"No traffic data available for region: {region}")
        return []

    except Exception as e:
        logger.error(f"Failed to fetch traffic data: {e}")
        return []

def is_route_affected_by_incident(
    route_coords: List[Dict[str, float]],
    incident: Dict[str, Any],
    buffer_km: float = 5.0
) -> bool:
    """
    Checks if a traffic incident affects a given route.

    Args:
        route_coords: List of {lat, lng} waypoints
        incident: Traffic incident dictionary
        buffer_km: Maximum distance (km) from route to consider affected

    Returns:
        True if incident affects route, False otherwise
    """
    from ..utils.geospatial import calculate_distance

    incident_lat = incident["location"]["lat"]
    incident_lng = incident["location"]["lng"]

    for point in route_coords:
        distance = calculate_distance(
            (point["lat"], point["lng"]),
            (incident_lat, incident_lng)
        )
        if distance <= buffer_km:
            return True

    return False
