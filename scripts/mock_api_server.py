"""
Mock API Server for Traffic and Weather Data

This provides mock endpoints simulating:
- Live Traffic NSW API
- Bureau of Meteorology (BOM) API

Run this server alongside the main FastAPI application for demo purposes:
  python scripts/mock_api_server.py

Endpoints:
  GET /traffic/{region} - Get traffic incidents
  GET /weather/ - Get weather alerts
  GET /health - Server health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import random
from datetime import datetime

app = FastAPI(
    title="Mock Traffic & Weather API",
    description="Mock endpoints for Live Traffic NSW and BOM data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock traffic incidents database
TRAFFIC_INCIDENTS = {
    "NSW": [
        {
            "type": "accident",
            "location": {"lat": -33.8523, "lng": 151.2108},
            "road": "M1 Pacific Motorway",
            "direction": "Northbound",
            "severity": "high",
            "delay_minutes": 30,
            "description": "Multi-vehicle collision"
        },
        {
            "type": "roadworks",
            "location": {"lat": -33.7506, "lng": 151.0844},
            "road": "A1",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 15,
            "description": "Lane closures for resurfacing"
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
            "description": "Vehicle breakdown"
        },
        {
            "type": "roadworks",
            "location": {"lat": -34.4244, "lng": 150.8931},
            "road": "Princes Highway",
            "direction": "Southbound",
            "severity": "medium",
            "delay_minutes": 10,
            "description": "Pothole repairs"
        }
    ],
    "VIC": [
        {
            "type": "accident",
            "location": {"lat": -37.8136, "lng": 144.9631},
            "road": "Monash Freeway",
            "direction": "Northbound",
            "severity": "high",
            "delay_minutes": 25,
            "description": "Vehicle collision"
        }
    ],
    "QLD": [
        {
            "type": "congestion",
            "location": {"lat": -27.4698, "lng": 153.0251},
            "road": "Gateway Motorway",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 15,
            "description": "Peak hour congestion"
        }
    ]
}

# Mock weather alerts database
WEATHER_ALERTS_TEMPLATE = [
    {
        "type": "bushfire",
        "severity": "extreme",
        "message": "Bushfire warning: Avoid the area. Extremely dangerous conditions."
    },
    {
        "type": "storm",
        "severity": "high",
        "message": "Severe storm warning: Heavy rain and strong winds expected."
    },
    {
        "type": "flood",
        "severity": "high",
        "message": "Flood warning: Road closures possible in low-lying areas."
    },
    {
        "type": "heatwave",
        "severity": "medium",
        "message": "High temperatures forecast. Ensure vehicle cooling systems are operational."
    },
    {
        "type": "wind",
        "severity": "medium",
        "message": "Strong winds warning: Gale force winds expected."
    }
]

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "service": "Mock Traffic & Weather API",
        "version": "1.0.0",
        "endpoints": {
            "traffic": "/traffic/{region}",
            "weather": "/weather/",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "mock-api"
    }

@app.get("/traffic/{region}")
async def get_traffic_incidents(region: str):
    """
    Get mock traffic incidents for a region.

    Args:
        region: Region code (e.g., NSW, VIC, QLD)

    Returns:
        List of traffic incidents
    """
    try:
        region = region.upper()
        incidents = TRAFFIC_INCIDENTS.get(region, [])

        # Simulate random dynamic data
        if random.random() < 0.3 and incidents:
            # Randomly add a temporary incident
            temp_incident = {
                "type": "incident",
                "location": {
                    "lat": random.uniform(-34.0, -33.0),
                    "lng": random.uniform(150.5, 152.0)
                },
                "road": "Pacific Motorway",
                "direction": "Both",
                "severity": "low",
                "delay_minutes": random.randint(5, 15),
                "description": "Temporary incident - may be cleared shortly"
            }
            incidents = incidents + [temp_incident]

        return {
            "region": region,
            "incidents": incidents,
            "count": len(incidents),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/")
async def get_weather_alerts(lat: float, lng: float, radius_km: int = 50):
    """
    Get mock weather alerts for a location.

    Args:
        lat: Latitude
        lng: Longitude
        radius_km: Search radius

    Returns:
        List of weather alerts
    """
    try:
        # Determine region based on latitude (simplified)
        if lat < -33.0:
            # Southern NSW/VIC - more heatwaves
            relevant = [WEATHER_ALERTS_TEMPLATE[3]]  # heatwave
        elif -33.0 <= lat <= -32.0:
            # Central NSW - storms and floods
            relevant = [WEATHER_ALERTS_TEMPLATE[1], WEATHER_ALERTS_TEMPLATE[2]]
        else:
            # Northern NSW/QLD - bushfires and storms
            relevant = [WEATHER_ALERTS_TEMPLATE[0], WEATHER_ALERTS_TEMPLATE[1]]

        # Random chance of additional alert
        if random.random() < 0.2:
            relevant.append(random.choice(WEATHER_ALERTS_TEMPLATE))

        alerts = []
        for alert in relevant:
            alerts.append({
                "type": alert["type"],
                "severity": alert["severity"],
                "message": alert["message"],
                "location": {"lat": lat, "lng": lng},
                "radius_km": radius_km,
                "generated_at": datetime.now().isoformat()
            })

        return {
            "lat": lat,
            "lng": lng,
            "radius_km": radius_km,
            "alerts": alerts,
            "count": len(alerts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def status():
    """Extended status endpoint with mock server stats."""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "uptime": "N/A",
        "requests_served": random.randint(100, 1000)
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Mock API Server...")
    print("Endpoints:")
    print("  GET /traffic/{region}  - Traffic incidents")
    print("  GET /weather/         - Weather alerts")
    print("  GET /health           - Health check")
    uvicorn.run(app, host="0.0.0.0", port=8001)
