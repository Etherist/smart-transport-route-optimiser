"""
Unit tests for Route Planner Agent
"""

import pytest
from datetime import datetime
from src.agents.route_planner import plan_route, GEOCODE_MOCK

class TestRoutePlanner:

    def test_plan_route_valid_input(self):
        """Test successful route planning with valid input."""
        result = plan_route("Sydney, NSW", "Newcastle, NSW", "Truck")

        assert result["start"]["address"] == "Sydney, NSW"
        assert result["start"]["lat"] == -33.8688
        assert result["start"]["lng"] == 151.2093
        assert result["end"]["address"] == "Newcastle, NSW"
        assert result["end"]["lat"] == -32.9282
        assert result["end"]["lng"] == 151.7594
        assert result["vehicle_type"] == "Truck"
        assert result["delivery_window"] is None

    def test_plan_route_with_delivery_window(self):
        """Test route planning with optional delivery window."""
        delivery = datetime(2026, 4, 28, 9, 0, 0)
        result = plan_route("Sydney, NSW", "Newcastle, NSW", "Truck", delivery)

        assert result["delivery_window"] == delivery.isoformat()

    def test_plan_route_invalid_vehicle_type(self):
        """Test error handling for invalid vehicle type."""
        with pytest.raises(ValueError) as exc:
            plan_route("Sydney, NSW", "Newcastle, NSW", "InvalidVehicle")

        assert "Invalid vehicle type" in str(exc.value)

    def test_plan_route_invalid_start_address(self):
        """Test error handling for unknown start address."""
        with pytest.raises(ValueError) as exc:
            plan_route("Unknown City, NSW", "Newcastle, NSW", "Truck")

        assert "Address not found" in str(exc.value)

    def test_plan_route_invalid_end_address(self):
        """Test error handling for unknown end address."""
        with pytest.raises(ValueError) as exc:
            plan_route("Sydney, NSW", "Unknown City, NSW", "Truck")

        assert "Address not found" in str(exc.value)

    def test_supported_locations(self):
        """Test that all predefined locations are geocodable."""
        for location in GEOCODE_MOCK.keys():
            result = plan_route(location, "Newcastle, NSW", "Truck")
            assert result is not None
            assert result["start"]["address"] == location

    def test_result_structure(self):
        """Test that result has expected structure."""
        result = plan_route("Sydney, NSW", "Newcastle, NSW", "Truck")

        required_keys = ["start", "end", "vehicle_type", "delivery_window"]
        for key in required_keys:
            assert key in result

    def test_plan_route_new_vehicle_types(self):
        """Test valid new vehicle types from expanded fleet (13 types)."""
        new_vehicle_types = [
            "Rigid", "Truck", "Semi-Trailer", "B-Double", "B-Triple",
            "Tautliner", "Reefer", "Flatbed", "Dump Truck", "Tanker",
            "Livestock Carrier", "Car Carrier", "Container Hauler"
        ]
        for vtype in new_vehicle_types:
            result = plan_route("Sydney, NSW", "Melbourne, VIC", vtype)
            assert result["vehicle_type"] == vtype
            assert result["start"]["address"] == "Sydney, NSW"
            assert result["end"]["address"] == "Melbourne, VIC"

    def test_plan_route_auto_detect_region(self):
        """Test that region auto-detection works from address (ACT, WA, QLD etc)."""
        # Various state-representative addresses
        test_cases = [
            ("Canberra, ACT", "Wagga Wagga, NSW"),
            ("Perth, WA", "Darwin, NT"),
            ("Brisbane, QLD", "Cairns, QLD"),
            ("Adelaide, SA", "Port Augusta, SA"),
        ]
        for start, end in test_cases:
            result = plan_route(start, end, "Truck")
            assert result["start"]["address"] == start
            assert result["end"]["address"] == end
