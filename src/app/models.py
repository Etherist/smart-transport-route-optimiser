from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class Location(BaseModel):
    """Geographic location with coordinates."""
    address: str
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")

class RouteRequest(BaseModel):
    """User-submitted route optimization request."""
    start_address: str = Field(..., min_length=3, description="Starting address")
    end_address: str = Field(..., min_length=3, description="Destination address")
    vehicle_type: str = Field(..., description="Type of vehicle")
    delivery_window: Optional[datetime] = Field(None, description="Required delivery time")
    region: Optional[str] = Field(None, description="State/territory (NSW, VIC, QLD, SA, WA, TAS, NT, ACT) – auto-detected if omitted")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_address": "Sydney, NSW",
                "end_address": "Newcastle, NSW",
                "vehicle_type": "Truck",
                "delivery_window": "2026-04-28T09:00:00",
                "region": "NSW"
            }
        }
    )

class RouteResponse(BaseModel):
    """Response containing optimized route and metrics."""
    route: List[Dict[str, Any]]
    distance_km: float
    duration_hours: float
    fuel_savings: Dict[str, Any]
    compliance: Dict[str, Any]
    report_url: str
    gpx_url: Optional[str] = None

class TrafficIncident(BaseModel):
    """Traffic incident data."""
    type: str
    location: Dict[str, float]
    road: str
    direction: str
    severity: str
    delay_minutes: int
    description: Optional[str] = None

class WeatherAlert(BaseModel):
    """Weather alert data."""
    type: str
    location: Dict[str, float]
    severity: str
    message: str
    radius_km: Optional[int] = 50

class ComplianceReport(BaseModel):
    """Compliance validation result."""
    nhvr_compliant: bool
    cor_compliant: bool
    fatigue_management: Dict[str, Any]
    vehicle_type: str

class SavingsReport(BaseModel):
    """Fuel and emissions savings report."""
    fuel_savings: Dict[str, float]
    route_fuel_litres: float
    route_co2_kg: float
    baseline_fuel_litres: float
    baseline_co2_kg: float
    report_path: Optional[str] = None
