"""
Integration tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

class TestAPIEndpoints:

    def test_root_returns_html(self):
        """Test that root endpoint serves HTML frontend."""
        response = client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Smart Route Optimizer" in response.text

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_optimize_endpoint_valid_request(self):
        """Test route optimization with valid request."""
        payload = {
            "start_address": "Sydney, NSW",
            "end_address": "Newcastle, NSW",
            "vehicle_type": "Truck"
        }

        response = client.post("/optimize/", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "route" in data
        assert "distance_km" in data
        assert "duration_hours" in data
        assert "fuel_savings" in data
        assert "compliance" in data
        assert "report_url" in data

    def test_optimize_endpoint_invalid_vehicle(self):
        """Test optimization with unsupported vehicle type."""
        payload = {
            "start_address": "Sydney, NSW",
            "end_address": "Newcastle, NSW",
            "vehicle_type": "Spaceship"
        }

        response = client.post("/optimize/", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_optimize_endpoint_missing_fields(self):
        """Test optimization with missing required fields."""
        payload = {
            "start_address": "Sydney, NSW"
            # Missing end_address and vehicle_type
        }

        response = client.post("/optimize/", json=payload)

        assert response.status_code == 422  # Validation error

    def test_optimize_endpoint_unknown_address(self):
        """Test optimization with unknown address."""
        payload = {
            "start_address": "Unknown City",
            "end_address": "Newcastle, NSW",
            "vehicle_type": "Truck"
        }

        response = client.post("/optimize/", json=payload)

        assert response.status_code == 400

    def test_traffic_endpoint(self):
        """Test traffic incidents endpoint."""
        response = client.get("/traffic/?region=NSW")

        assert response.status_code == 200
        data = response.json()
        assert data["region"] == "NSW"
        assert "incidents" in data
        assert "count" in data

    def test_traffic_endpoint_default_region(self):
        """Test traffic endpoint with default region."""
        response = client.get("/traffic/")

        assert response.status_code == 200
        data = response.json()
        assert data["region"] == "NSW"

    def test_weather_endpoint(self):
        """Test weather alerts endpoint."""
        response = client.get("/weather/?lat=-33.8688&lng=151.2093")

        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "count" in data

    def test_weather_endpoint_with_radius(self):
        """Test weather endpoint with custom radius."""
        response = client.get("/weather/?lat=-33.8688&lng=151.2093&radius_km=100")

        assert response.status_code == 200
        data = response.json()
        assert data["radius_km"] == 100

    def test_reports_endpoint_not_found(self):
        """Test requesting non-existent report."""
        response = client.get("/reports/nonexistent.pdf")

        assert response.status_code == 404

    def test_response_time_optimize(self):
        """Test that optimization responds quickly (< 5 seconds)."""
        import time

        payload = {
            "start_address": "Sydney, NSW",
            "end_address": "Newcastle, NSW",
            "vehicle_type": "Truck"
        }

        start = time.time()
        response = client.post("/optimize/", json=payload)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 5.0, f"Response took {elapsed:.2f}s, should be < 5s"

    def test_compliance_in_response(self):
        """Test that compliance data is included in optimize response."""
        payload = {
            "start_address": "Sydney, NSW",
            "end_address": "Newcastle, NSW",
            "vehicle_type": "Truck"
        }

        response = client.post("/optimize/", json=payload)
        data = response.json()

        compliance = data["compliance"]
        assert "nhvr_compliant" in compliance
        assert "cor_compliant" in compliance
        assert "fatigue_management" in compliance

    def test_fuel_savings_in_response(self):
        """Test that fuel savings data is included."""
        payload = {
            "start_address": "Sydney, NSW",
            "end_address": "Newcastle, NSW",
            "vehicle_type": "Truck"
        }

        response = client.post("/optimize/", json=payload)
        data = response.json()

        savings = data["fuel_savings"]
        assert "litres" in savings
        assert "cost_AUD" in savings
        assert "co2_kg" in savings

    def test_json_response_validity(self):
        """Test that JSON response is valid."""
        payload = {
            "start_address": "Sydney, NSW",
            "end_address": "Newcastle, NSW",
            "vehicle_type": "Truck"
        }

        response = client.post("/optimize/", json=payload)

        # Should not raise JSON decode error
        data = response.json()
        assert isinstance(data, dict)
