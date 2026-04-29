"""
Unit tests for Savings Reporter Agent
"""

import pytest
import os
from src.agents.savings_reporter import generate_report, generate_gpx_route
from src.agents.route_planner import plan_route
from src.agents.route_optimizer import optimize_route

class TestSavingsReporter:

    @pytest.fixture
    def sample_route(self):
        """Create a sample optimized route."""
        return {
            "route": [
                {"lat": -33.8688, "lng": 151.2093, "name": "Sydney"},
                {"lat": -33.425, "lng": 151.3417, "name": "Central Coast"},
                {"lat": -32.9282, "lng": 151.7594, "name": "Newcastle"}
            ],
            "distance_km": 167.0,
            "duration_hours": 2.5
        }

    @pytest.fixture
    def sample_baseline(self):
        """Create a sample baseline route."""
        return {
            "distance_km": 192.0,  # 15% longer
            "duration_hours": 2.9
        }

    def test_generate_report_structure(self, sample_route, sample_baseline, tmp_path):
        """Test report generation returns correct structure."""
        report_path = tmp_path / "test_report.pdf"
        result = generate_report(sample_route, sample_baseline, "Truck", str(report_path))

        assert "fuel_savings" in result
        assert "route_fuel_litres" in result
        assert "route_co2_kg" in result
        assert "baseline_fuel_litres" in result
        assert "baseline_co2_kg" in result
        assert "report_path" in result

    def test_fuel_savings_positive(self, sample_route, sample_baseline):
        """Test that optimized route uses less fuel."""
        result = generate_report(sample_route, sample_baseline, "Truck")

        assert result["fuel_savings"]["litres"] > 0
        assert result["fuel_savings"]["cost_AUD"] > 0

    def test_co2_savings_positive(self, sample_route, sample_baseline):
        """Test that optimized route produces less CO2."""
        result = generate_report(sample_route, sample_baseline, "Truck")

        assert result["fuel_savings"]["co2_kg"] > 0

    def test_baseline_uses_more_fuel(self, sample_route, sample_baseline):
        """Test baseline route uses more fuel than optimized."""
        result = generate_report(sample_route, sample_baseline, "Truck")

        assert result["baseline_fuel_litres"] > result["route_fuel_litres"]

    def test_report_pdf_created(self, sample_route, sample_baseline, tmp_path):
        """Test that PDF file is actually created."""
        report_path = tmp_path / "test_report.pdf"
        result = generate_report(sample_route, sample_baseline, "Truck", str(report_path))

        assert result["report_path"] is not None
        assert os.path.exists(result["report_path"])

    def test_no_pdf_when_no_path(self, sample_route, sample_baseline):
        """Test that None is returned when no output path given."""
        result = generate_report(sample_route, sample_baseline, "Truck", None)

        assert result["report_path"] is None

    def test_different_vehicle_fuel_rates(self):
        """Test that fuel calculations differ by vehicle type across fleet."""
        route = {"distance_km": 100.0, "duration_hours": 2.0}
        baseline = {"distance_km": 115.0, "duration_hours": 2.3}

        # Sample multiple vehicle types to ensure no errors
        vehicles = ["Truck", "B-Double", "Semi-Trailer", "B-Triple", "Rigid", "Tautliner", "Reefer", "Flatbed", "Dump Truck", "Tanker"]
        results = {}
        for v in vehicles:
            results[v] = generate_report(route, baseline, v)

        # All should have distinct fuel rates resulting in different savings
        # Except for vehicles with same consumption values (e.g., Truck vs Semi may differ)
        # Ensure no errors and results are numeric
        for v, res in results.items():
            assert "fuel_savings" in res
            assert res["fuel_savings"]["litres"] >= 0

        # B-Triple should have highest consumption among these (0.23)
        assert results["B-Triple"]["route_fuel_litres"] > results["Truck"]["route_fuel_litres"]
        # Rigid should have lowest consumption among trucks (0.12)
        assert results["Rigid"]["route_fuel_litres"] < results["Truck"]["route_fuel_litres"]

    def test_gpx_route_generation(self, sample_route, tmp_path):
        """Test GPX file generation."""
        gpx_path = tmp_path / "test_route.gpx"
        result_path = generate_gpx_route(sample_route, str(gpx_path))

        assert os.path.exists(result_path)
        assert result_path.endswith(".gpx")

        # Check GPX content structure
        with open(result_path, 'r') as f:
            content = f.read()
            assert "<?xml" in content
            assert "<gpx" in content
            assert "</gpx>" in content
            assert "<wpt" in content
            assert "<trk" in content

    def test_gpx_waypoints_count(self, sample_route, tmp_path):
        """Test that GPX contains correct number of waypoints."""
        gpx_path = tmp_path / "test.gpx"
        generate_gpx_route(sample_route, str(gpx_path))

        with open(gpx_path, 'r') as f:
            content = f.read()
            wpt_count = content.count("<wpt")
            assert wpt_count == len(sample_route["route"])

    def test_gpx_with_empty_route(self, tmp_path):
        """Test GPX generation with empty route raises error."""
        empty_route = {"route": []}
        gpx_path = tmp_path / "empty.gpx"

        with pytest.raises(ValueError):
            generate_gpx_route(empty_route, str(gpx_path))

    def test_fuel_consumption_values(self):
        """Test that fuel consumption values match vehicle constraints."""
        # Truck: 0.15 L/km
        # At 100 km, truck should consume 15 L
        route = {"distance_km": 100.0}
        baseline = {"distance_km": 115.0}

        result = generate_report(route, baseline, "Truck")

        # Truck fuel rate = 0.15 L/km
        # Optimized: 100 * 0.15 = 15 L
        # Baseline: 115 * 0.15 = 17.25 L
        # Savings: 2.25 L
        assert abs(result["route_fuel_litres"] - 15.0) < 0.01
        assert abs(result["baseline_fuel_litres"] - 17.25) < 0.01
        assert abs(result["fuel_savings"]["litres"] - 2.25) < 0.01

    def test_co2_conversion(self):
        """Test CO2 conversion uses correct factor (0.4 kg CO2/L)."""
        route = {"distance_km": 100.0}
        baseline = {"distance_km": 115.0}

        result = generate_report(route, baseline, "Truck")

        # Truck: 15 L * 0.4 = 6 kg CO2
        # Baseline: 17.25 L * 0.4 = 6.9 kg CO2
        # Savings: 0.9 kg CO2
        assert abs(result["route_co2_kg"] - 6.0) < 0.01
        assert abs(result["baseline_co2_kg"] - 6.9) < 0.01
        assert abs(result["fuel_savings"]["co2_kg"] - 0.9) < 0.01
