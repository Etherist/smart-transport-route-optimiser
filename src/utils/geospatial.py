import geopy.distance
from typing import Tuple, List, Dict

def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calculate geodesic distance between two coordinates in kilometers."""
    return geopy.distance.geodesic(coord1, coord2).km

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate latitude and longitude values."""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def find_nearest_node(lat: float, lng: float, nodes: List[Dict], threshold_km: float = 20.0) -> str:
    """Find the nearest node in the road network to given coordinates."""
    nearest_id = None
    min_distance = float('inf')

    for node in nodes:
        node_coords = (node["lat"], node["lng"])
        distance = calculate_distance((lat, lng), node_coords)
        if distance < min_distance:
            min_distance = distance
            nearest_id = node["id"]

    return nearest_id if min_distance <= threshold_km else ""

def build_adjacency_list(edges: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Build adjacency list from edge list."""
    adj = {}
    for edge in edges:
        from_id = edge["from"]
        to_id = edge["to"]
        distance = edge["distance_km"]

        if from_id not in adj:
            adj[from_id] = {}
        adj[from_id][to_id] = distance

        # Add reverse direction for undirected graph
        if to_id not in adj:
            adj[to_id] = {}
        adj[to_id][from_id] = distance

    return adj
