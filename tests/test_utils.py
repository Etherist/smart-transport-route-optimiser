"""
Unit tests for utility functions
"""

import pytest
from src.utils.geospatial import (
    calculate_distance,
    validate_coordinates,
    find_nearest_node,
    build_adjacency_list
)

class TestGeospatialUtils:

    def test_calculate_distance_same_point(self):
        """Distance between same point should be zero."""
        coord = (-33.8688, 151.2093)
        dist = calculate_distance(coord, coord)
        assert dist == 0.0

    def test_calculate_distance_known_values(self):
        """Test distance calculation with known Sydney-Melbourne distance."""
        sydney = (-33.8688, 151.2093)
        melbourne = (-37.8136, 144.9631)
        dist = calculate_distance(sydney, melbourne)

        # Approx distance: ~714 km
        assert 700 < dist < 720

    def test_validate_coordinates_valid(self):
        """Test valid coordinates."""
        assert validate_coordinates(0, 0) == True
        assert validate_coordinates(90, 180) == True
        assert validate_coordinates(-90, -180) == True
        assert validate_coordinates(45.5, 120.3) == True

    def test_validate_coordinates_invalid_latitude(self):
        """Test invalid latitude."""
        assert validate_coordinates(91, 0) == False
        assert validate_coordinates(-91, 0) == False

    def test_validate_coordinates_invalid_longitude(self):
        """Test invalid longitude."""
        assert validate_coordinates(0, 181) == False
        assert validate_coordinates(0, -181) == False

    def test_build_adjacency_list(self):
        """Test adjacency list construction."""
        edges = [
            {"from": "A", "to": "B", "distance_km": 10.0},
            {"from": "A", "to": "C", "distance_km": 20.0},
            {"from": "B", "to": "C", "distance_km": 15.0}
        ]

        adj = build_adjacency_list(edges)

        assert "A" in adj
        assert "B" in adj["A"]
        assert adj["A"]["B"] == 10.0
        assert adj["A"]["C"] == 20.0
        # Should be undirected - reverse edges included
        assert "A" in adj["B"]
        assert adj["B"]["A"] == 10.0

    def test_find_nearest_node_basic(self):
        """Test finding nearest node."""
        nodes = [
            {"id": "n1", "lat": -33.8688, "lng": 151.2093},
            {"id": "n2", "lat": -33.8700, "lng": 151.2100},
            {"id": "n3", "lat": -34.0, "lng": 150.0}
        ]

        nearest = find_nearest_node(-33.8688, 151.2093, nodes, threshold_km=100)

        assert nearest == "n1"

    def test_find_nearest_node_threshold(self):
        """Test threshold exclusion."""
        nodes = [
            {"id": "n1", "lat": -33.8688, "lng": 151.2093},
            {"id": "n2", "lat": -40.0, "lng": 150.0}  # Far away
        ]

        nearest = find_nearest_node(-33.8688, 151.2093, nodes, threshold_km=10)

        assert nearest == "n1"

    def test_find_nearest_node_beyond_threshold(self):
        """Test that returns empty when all nodes beyond threshold."""
        nodes = [
            {"id": "n1", "lat": -40.0, "lng": 150.0},
            {"id": "n2", "lat": -41.0, "lng": 151.0}
        ]

        nearest = find_nearest_node(-33.8688, 151.2093, nodes, threshold_km=10)

        assert nearest == ""

    def test_distance_commutative(self):
        """Test that distance A->B equals B->A."""
        a = (-33.8688, 151.2093)
        b = (-32.9282, 151.7594)

        assert calculate_distance(a, b) == calculate_distance(b, a)
