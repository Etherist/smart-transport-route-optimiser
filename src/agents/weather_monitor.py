import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Comprehensive weather alerts covering all Australian climate zones
WEATHER_ALERTS_BY_ZONE = {
    "northern": [
        {
            "type": "bushfire",
            "severity": "extreme",
            "message": "Bushfire warning: Extremely dangerous fire conditions. Avoid travel through affected areas.",
            "season": "dry"
        },
        {
            "type": "cyclone",
            "severity": "extreme",
            "message": "Tropical Cyclone warning: Category 3+ cyclone approaching. Seek shelter immediately.",
            "season": "wet"
        },
        {
            "type": "storm",
            "severity": "high",
            "message": "Severe thunderstorm warning: Damaging winds and large hail expected.",
            "season": "wet"
        },
        {
            "type": "flood",
            "severity": "high",
            "message": "Flash flood warning: Rapidly rising waters possible. Avoid low-lying roads.",
            "season": "wet"
        }
    ],
    "eastern": [
        {
            "type": "storm",
            "severity": "high",
            "message": "Severe storm warning: Heavy rain, strong winds, and hail. Road closures likely.",
            "season": "all"
        },
        {
            "type": "flood",
            "severity": "high",
            "message": "Flood warning: Riverine flooding expected. Major roads may be inundated.",
            "season": "wet"
        },
        {
            "type": "bushfire",
            "severity": "high",
            "message": "Bushfire danger: Extreme fire weather conditions reported.",
            "season": "dry"
        },
        {
            "type": "fog",
            "severity": "medium",
            "message": "Dense fog warning: Visibility under 200m on major highways.",
            "season": "autumn"
        }
    ],
    "southern": [
        {
            "type": "storm",
            "severity": "high",
            "message": "Severe weather: Cold front bringing heavy rain and strong gusts.",
            "season": "winter"
        },
        {
            "type": "snow",
            "severity": "high",
            "message": "Snow and ice warning: Dangerous alpine conditions. Chains may be required.",
            "season": "winter"
        },
        {
            "type": "wind",
            "severity": "medium",
            "message": "Strong wind warning: Gusts up to 90km/h expected on exposed routes.",
            "season": "spring"
        },
        {
            "type": "heatwave",
            "severity": "medium",
            "message": "Extreme heat warning: Temperatures above 40°C. Vehicle overheating risk.",
            "season": "summer"
        }
    ],
    "central": [
        {
            "type": "dust_storm",
            "severity": "high",
            "message": "Dust storm warning: Zero visibility possible on outback highways.",
            "season": "spring"
        },
        {
            "type": "heatwave",
            "severity": "high",
            "message": "Extreme heat warning: Temperatures exceeding 45°C. Engine risk.",
            "season": "summer"
        },
        {
            "type": "flood",
            "severity": "extreme",
            "message": "Inland flooding: Major road closures across outback regions.",
            "season": "wet"
        }
    ],
    "west_coastal": [
        {
            "type": "storm",
            "severity": "medium",
            "message": "Winter storm: Heavy rain and possible hail on Perth area.",
            "season": "winter"
        },
        {
            "type": "bushfire",
            "severity": "extreme",
            "message": "Bushfire emergency: Extreme conditions, seek immediate shelter.",
            "season": "dry"
        }
    ],
    "south_coastal": [
        {
            "type": "storm",
            "severity": "high",
            "message": "Coastal storm warnings: High surf and gale-force winds.",
            "season": "winter"
        },
        {
            "type": "flood",
            "severity": "medium",
            "message": "Coastal flooding: High tide plus storm surge may inundate roads.",
            "season": "autumn"
        }
    ]
}

def fetch_weather_alerts(
    lat: float,
    lng: float,
    radius_km: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetches weather alerts for the specified geographic area across Australia.
    (Mock implementation simulating BOM-style data with regional climate zones)

    Args:
        lat: Latitude of route midpoint
        lng: Longitude of route midpoint
        radius_km: Search radius in kilometers

    Returns:
        List of weather alert dictionaries relevant to the location and season

    Note:
        In production, this would call Bureau of Meteorology (BOM) API for all Australian states/territories
    """
    try:
        from ..utils.geospatial import calculate_distance

        active_alerts = []

        # Determine climate zone based on latitude/longitude
        # Northern: QLD north, NT north, WA north
        # Eastern: NSW, VIC east coast, SEQ
        # Southern: TAS, VIC south, SA south
        # Central: Outback regions
        # Thresholds: east/west roughly 135°E longitude (Indian Ocean vs Pacific)

        is_north = lat > -20
        is_south = lat < -35
        is_east = lng > 145
        is_west = lng < 120
        is_central = (-35 <= lat <= -20) and (120 <= lng <= 145)

        # Determine current season (southern hemisphere)
        month = datetime.now().month
        if month in [12, 1, 2]:
            season = "summer"
        elif month in [3, 4, 5]:
            season = "autumn"
        elif month in [6, 7, 8]:
            season = "winter"
        else:
            season = "spring"

        # Select appropriate zone
        if is_north and is_east:
            zone = "northern"
            zone_alerts = WEATHER_ALERTS_BY_ZONE["northern"]
        elif is_north and is_west:
            zone = "northern"
            zone_alerts = WEATHER_ALERTS_BY_ZONE["northern"]
        elif is_south and is_east:
            zone = "southern"
            zone_alerts = WEATHER_ALERTS_BY_ZONE["southern"]
        elif is_south and is_west:
            zone = "south_coastal"
            zone_alerts = WEATHER_ALERTS_BY_ZONE["south_coastal"]
        elif is_central:
            zone = "central"
            zone_alerts = WEATHER_ALERTS_BY_ZONE["central"]
        elif is_west and lat > -30:
            zone = "west_coastal"
            zone_alerts = WEATHER_ALERTS_BY_ZONE["west_coastal"]
        elif is_east and -35 < lat < -25:
            zone = "eastern"
            zone_alerts = WEATHER_ALERTS_BY_ZONE["eastern"]
        else:
            # Default to eastern for mixed cases
            zone = "eastern"
            zone_alerts = WEATHER_ALERTS_BY_ZONE["eastern"]

        # Filter alerts by season - only include season-appropriate weather
        for alert in zone_alerts:
            if alert["season"] == "all" or alert["season"] == season:
                # Simulate random chance of active alert (30-60% depending on season)
                # For demo, always include 1-2 alerts
                active_alerts.append({
                    "type": alert["type"],
                    "severity": alert["severity"],
                    "message": alert["message"],
                    "location": {"lat": lat, "lng": lng},
                    "radius_km": radius_km,
                    "zone": zone,
                    "season": season
                })

        logger.info(
            f"Fetched {len(active_alerts)} weather alerts "
            f"for coordinates ({lat:.2f}, {lng:.2f}), zone: {zone}, season: {season}"
        )
        return active_alerts[:2]  # Return at most 2 alerts for demo clarity

    except Exception as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return []

def get_weather_impact_multiplier(severity: str) -> float:
    """
    Returns a speed/duration multiplier based on weather severity.
    Used to adjust route time for adverse conditions.

    Args:
        severity: Weather severity level (low, medium, high, extreme)

    Returns:
        Multiplier for travel time (1.0 = no impact, higher = slower)
    """
    impact_map = {
        "low": 1.1,
        "medium": 1.25,
        "high": 1.5,
        "extreme": 2.0
    }
    return impact_map.get(severity, 1.0)
