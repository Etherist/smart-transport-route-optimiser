#!/usr/bin/env python3
"""
Generate sample data for the Smart Route Optimizer demo.

This script pre-generates sample routes and mock data for testing.
"""

import json
import os

def generate_sample_road_network():
    """Generate NSW road network data."""
    data = {
        "nodes": [
            {"id": "sydney", "name": "Sydney, NSW", "lat": -33.8688, "lng": 151.2093},
            {"id": "newcastle", "name": "Newcastle, NSW", "lat": -32.9282, "lng": 151.7594},
            {"id": "wollongong", "name": "Wollongong, NSW", "lat": -34.4244, "lng": 150.8931},
            {"id": "central_coast", "name": "Central Coast, NSW", "lat": -33.425, "lng": 151.3417},
            {"id": "gosford", "name": "Gosford, NSW", "lat": -33.4256, "lng": 151.3412},
            {"id": "melson", "name": "Melson, NSW", "lat": -32.7323, "lng": 151.5612},
            {"id": "newcastle_west", "name": "Newcastle West, NSW", "lat": -32.92, "lng": 151.55},
            {"id": "cronulla", "name": "Cronulla, NSW", "lat": -34.0628, "lng": 151.1501},
            {"id": "campbelltown", "name": "Campbelltown, NSW", "lat": -34.0628, "lng": 150.8142}
        ],
        "edges": [
            {"from": "sydney", "to": "newcastle", "distance_km": 167.0, "speed_kmh": 100, "road_type": "motorway"},
            {"from": "sydney", "to": "wollongong", "distance_km": 80.0, "speed_kmh": 80, "road_type": "highway"},
            {"from": "sydney", "to": "central_coast", "distance_km": 80.0, "speed_kmh": 100, "road_type": "motorway"},
            {"from": "central_coast", "to": "newcastle", "distance_km": 80.5, "speed_kmh": 100, "road_type": "motorway"},
            {"from": "sydney", "to": "gosford", "distance_km": 75.0, "speed_kmh": 100, "road_type": "motorway"},
            {"from": "gosford", "to": "central_coast", "distance_km": 25.0, "speed_kmh": 90, "road_type": "highway"},
            {"from": "central_coast", "to": "melson", "distance_km": 45.0, "speed_kmh": 90, "road_type": "highway"},
            {"from": "melson", "to": "newcastle", "distance_km": 35.5, "speed_kmh": 100, "road_type": "motorway"},
            {"from": "sydney", "to": "cronulla", "distance_km": 26.0, "speed_kmh": 70, "road_type": "urban"},
            {"from": "sydney", "to": "campbelltown", "distance_km": 40.0, "speed_kmh": 90, "road_type": "highway"},
            {"from": "wollongong", "to": "campbelltown", "distance_km": 70.0, "speed_kmh": 80, "road_type": "highway"}
        ]
    }
    return data

def save_to_file(data, filename):
    """Save data to JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Created: {filename}")

def main():
    print("Generating sample data for Smart Route Optimizer...")

    os.makedirs("src/data", exist_ok=True)

    # Save road network
    road_network = generate_sample_road_network()
    save_to_file(road_network, "src/data/nsw_road_network.json")

    print("\n✅ Sample data generated successfully!")

if __name__ == "__main__":
    main()
