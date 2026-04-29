"""
Unit tests for Compliance Validator Agent
"""

import pytest
from src.agents.compliance_validator import validate_compliance

class TestComplianceValidator:

    def test_compliant_route_short_duration(self):
        """Test compliance for a short, valid route."""
        route = {"duration_hours": 2.5}
        result = validate_compliance(route, "Truck")

        assert result["nhvr_compliant"] == True
        assert result["cor_compliant"] == True
        assert "OK" in result["fatigue_management"]["notes"][0]

    def test_non_compliant_route_exceeds_daily_limit(self):
        """Test non-compliance when exceeding daily limit."""
        route = {"duration_hours": 13.0}  # Exceeds 12h limit
        result = validate_compliance(route, "Truck")

        assert result["nhvr_compliant"] == False
        assert result["cor_compliant"] == False
        assert len(result["fatigue_management"]["violations"]) > 0
        assert "daily limit" in result["fatigue_management"]["violations"][0].lower()

    def test_compliance_at_daily_limit_boundary(self):
        """Test compliance exactly at limit."""
        route = {"duration_hours": 12.0}  # Exactly at limit
        result = validate_compliance(route, "Truck")

        assert result["nhvr_compliant"] == True

    def test_weekly_hours_accumulation(self):
        """Test weekly hour accumulation check."""
        route = {"duration_hours": 10.0}
        result = validate_compliance(route, "Truck", driver_hours_week=65.0)

        # 65 + 10 = 75 > 72 (weekly limit)
        assert result["nhvr_compliant"] == False
        assert any("weekly" in v.lower() for v in result["fatigue_management"]["violations"])

    def test_weekly_hours_within_limit(self):
        """Test weekly accumulation within limits."""
        route = {"duration_hours": 5.0}
        result = validate_compliance(route, "Truck", driver_hours_week=60.0)

        # 60 + 5 = 65 < 72 (weekly limit)
        assert result["nhvr_compliant"] == True

    def test_different_vehicle_types(self):
        """Test all 13 vehicle types with compliant route."""
        # All vehicle types share same NHVR limits but should be recognized without error.
        all_vehicles = [
            "Rigid", "Truck", "Semi-Trailer", "B-Double", "B-Triple",
            "Tautliner", "Reefer", "Flatbed", "Dump Truck", "Tanker",
            "Livestock Carrier", "Car Carrier", "Container Hauler"
        ]
        for vehicle in all_vehicles:
            route = {"duration_hours": 5.0}
            result = validate_compliance(route, vehicle)
            assert result["nhvr_compliant"] == True, f"Vehicle {vehicle} should be compliant for 5h route"
            assert result["vehicle_type"] == vehicle

    def test_invalid_vehicle_defaults_to_truck(self):
        """Test that invalid vehicle type falls back to Truck rules."""
        route = {"duration_hours": 5.0}
        result = validate_compliance(route, "UnknownVehicle")

        # Should still work with default Truck rules
        assert "nhvr_compliant" in result

    def test_rest_period_recommendation(self):
        """Test that rest period is recommended for long shifts."""
        route = {"duration_hours": 11.5}
        result = validate_compliance(route, "Truck")

        assert any("rest" in note.lower() for note in result["fatigue_management"]["notes"])

    def test_result_structure(self):
        """Test that result has all required fields."""
        route = {"duration_hours": 5.0}
        result = validate_compliance(route, "Truck")

        required_fields = [
            "nhvr_compliant", "cor_compliant",
            "fatigue_management", "vehicle_type"
        ]
        for field in required_fields:
            assert field in result

    def test_fatigue_management_details(self):
        """Test fatigue management dictionary structure."""
        route = {"duration_hours": 8.0}
        result = validate_compliance(route, "Truck")

        fm = result["fatigue_management"]
        assert "duration_hours" in fm
        assert "daily_limit" in fm
        assert "weekly_limit" in fm
        assert "min_rest_hours" in fm
        assert "violations" in fm
        assert "warnings" in fm
        assert "notes" in fm
