"""
Unit tests for Route Optimizer Agent
"""

import pytest
from src.agents.route_optimizer import optimize_route, _dijkstra
from src.agents.route_planner import plan_route

class TestRouteOptimizer:

    def test_optimize_route_sydney_to_newcastle(self):
        """Test optimizing a simple Sydney -> Newcastle route."""
        route_request = plan_route("Sydney, NSW", "Newcastle, NSW", "Truck")
        traffic = []
        weather = []

        result = optimize_route(route_request, traffic, weather)

        assert "error" not in result
        assert "route" in result
        assert "distance_km" in result
        assert "duration_hours" in result
        assert len(result["route"]) >= 2  # At least start and end

    def test_optimize_route_with_traffic(self):
        """Test optimization with traffic incidents."""
        route_request = plan_route("Sydney, NSW", "Newcastle, NSW", "Truck")
        traffic = [
            {
                "location": {"lat": -33.8500, "lng": 151.2000},
                "delay_minutes": 20,
                "road": "M1"
            }
        ]
        weather = []

        result = optimize_route(route_request, traffic, weather)

        assert "error" not in result
        # With traffic, duration might increase
        assert result["distance_km"] > 0

    def test_optimize_route_with_weather(self):
        """Test optimization with weather alerts."""
        route_request = plan_route("Sydney, NSW", "Central Coast, NSW", "Truck")
        traffic = []
        weather = [
            {
                "severity": "high",
                "type": "storm"
            }
        ]

        result = optimize_route(route_request, traffic, weather)

        assert "error" not in result
        # With bad weather, effective distance should increase
        assert result["distance_km"] > 0

    def test_optimize_route_unknown_location(self):
        """Test error handling for unknown locations."""
        route_request = {
            "start": {"lat": -40.0, "lng": 150.0},  # Not in network
            "end": {"lat": -32.9, "lng": 151.7},
            "vehicle_type": "Truck",
            "delivery_window": None
        }

        result = optimize_route(route_request, [], [])

        # Should return error or empty route
        assert "error" in result or result.get("route") is None

    def test_dijkstra_algorithm(self):
        """Test Dijkstra's algorithm on simple path."""
        # Test using node IDs
        from src.agents.route_optimizer import ADJACENCY_LIST

        # Sydney to Newcastle should have path
        path, distance = _dijkstra("sydney", "newcastle")

        assert isinstance(path, list)
        assert len(path) >= 2
        assert path[0] == "sydney"
        assert path[-1] == "newcastle"
        assert distance > 0

    def test_dijkstra_no_path(self):
        """Test Dijkstra with unreachable nodes."""
        # If we had an isolated node, would return empty
        path, distance = _dijkstra("nonexistent", "newcastle")

        assert path == []
        assert distance == 0.0

    def test_vehicle_type_affects_speed(self):
        """Test that vehicle type impacts duration calculation."""
        route_request_truck = plan_route("Sydney, NSW", "Newcastle, NSW", "Truck")
        route_request_bdouble = plan_route("Sydney, NSW", "Newcastle, NSW", "B-Double")

        result_truck = optimize_route(route_request_truck, [], [])
        result_bdouble = optimize_route(route_request_bdouble, [], [])

        # Same route distance should differ in duration
        assert result_truck["distance_km"] == result_bdouble["distance_km"]
        # B-Double is slower (90 km/h vs 100), so duration should be longer
        assert result_bdouble["duration_hours"] > result_truck["duration_hours"]

    def test_route_structure(self):
        """Test that optimized route has proper structure."""
        route_request = plan_route("Sydney, NSW", "Newcastle, NSW", "Truck")
        result = optimize_route(route_request, [], [])

        assert "route" in result
        for point in result["route"]:
            assert "lat" in point
            assert "lng" in point
            assert -90 <= point["lat"] <= 90
            assert -180 <= point["lng"] <= 180

    def test_distance_positive(self):
        """Test that calculated distance is always positive."""
        route_request = plan_route("Sydney, NSW", "Newcastle, NSW", "Truck")
        result = optimize_route(route_request, [], [])

        assert result["distance_km"] > 0
        assert result["duration_hours"] > 0
