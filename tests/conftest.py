"""
Pytest configuration and fixtures
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def sample_route_request():
    """Sample route request data."""
    return {
        "start": {
            "address": "Sydney, NSW",
            "lat": -33.8688,
            "lng": 151.2093
        },
        "end": {
            "address": "Newcastle, NSW",
            "lat": -32.9282,
            "lng": 151.7594
        },
        "vehicle_type": "Truck",
        "delivery_window": None
    }

@pytest.fixture
def sample_traffic_incidents():
    """Sample traffic incidents."""
    return [
        {
            "type": "accident",
            "location": {"lat": -33.8523, "lng": 151.2108},
            "road": "M1 Pacific Motorway",
            "direction": "Northbound",
            "severity": "high",
            "delay_minutes": 30
        },
        {
            "type": "roadworks",
            "location": {"lat": -33.7506, "lng": 151.0844},
            "road": "A1",
            "direction": "Both",
            "severity": "medium",
            "delay_minutes": 15
        }
    ]

@pytest.fixture
def sample_weather_alerts():
    """Sample weather alerts."""
    return [
        {
            "type": "storm",
            "severity": "high",
            "message": "Severe storm warning",
            "location": {"lat": -33.4, "lng": 151.3}
        }
    ]

@pytest.fixture
def sample_vehicle_constraints():
    """Sample vehicle constraints."""
    return {
        "Truck": {
            "max_speed_kmh": 100,
            "fuel_consumption_L_per_km": 0.15,
            "max_weight_kg": 40000,
            "nhvr_rules": {
                "max_hours_per_day": 12,
                "max_hours_per_week": 72,
                "min_rest_after_shift_hours": 7
            }
        }
    }
