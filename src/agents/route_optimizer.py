import logging
import json
from typing import Dict, List, Tuple, Any, Optional
import geopy.distance
from src.utils.config import Config
from src.utils.geospatial import calculate_distance, find_nearest_node, build_adjacency_list

logger = logging.getLogger(__name__)

# Load road network data (national coverage)
def load_road_network() -> Tuple[Dict[str, Dict], List[Dict]]:
    """Load Australian national road network from JSON file."""
    try:
        with open(Config.ROAD_NETWORK_PATH, "r") as f:
            data = json.load(f)
        nodes = data["nodes"]
        edges = data["edges"]
        adj = build_adjacency_list(edges)

        # Create node lookup dict
        node_dict = {node["id"]: node for node in nodes}

        logger.info(f"Loaded road network: {len(nodes)} nodes, {len(edges)} edges across {len(data.get('metadata', {}).get('states', []))} states/territories")
        return node_dict, adj
    except Exception as e:
        logger.error(f"Failed to load road network: {e}")
        raise

NODE_DICT, ADJACENCY_LIST = load_road_network()

# Comprehensive vehicle speed profiles (km/h) - based on vehicle type + regulatory limits
VEHICLE_SPEEDS = {
    "Rigid": 100,
    "Truck": 100,
    "Semi-Trailer": 100,
    "B-Double": 90,
    "B-Triple": 90,
    "Tautliner": 100,
    "Reefer": 95,
    "Flatbed": 100,
    "Dump Truck": 80,
    "Tanker": 90,
    "Livestock Carrier": 90,
    "Car Carrier": 100,
    "Container Hauler": 100
}

def optimize_route(
    route_request: Dict[str, Any],
    traffic_incidents: List[Dict[str, Any]],
    weather_alerts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Optimizes a route using a simplified Dijkstra's algorithm.
    Considers traffic incidents and weather impacts.

    Args:
        route_request: Structured route request with start/end coordinates
        traffic_incidents: List of traffic incidents affecting travel
        weather_alerts: List of weather alerts affecting the route

    Returns:
        Optimized route dictionary with waypoints, distance, and duration

    Raises:
        ValueError: If no valid route can be found
    """
    try:
        start_lat = route_request["start"]["lat"]
        start_lng = route_request["start"]["lng"]
        end_lat = route_request["end"]["lat"]
        end_lng = route_request["end"]["lng"]
        vehicle_type = route_request["vehicle_type"]

        # Find nearest nodes in road network
        start_node_id = find_nearest_node(start_lat, start_lng, list(NODE_DICT.values()))
        end_node_id = find_nearest_node(end_lat, end_lng, list(NODE_DICT.values()))

        if not start_node_id or not end_node_id:
            raise ValueError("Start or end point not found in road network.")

        # Calculate base route using Dijkstra's
        path, base_distance = _dijkstra(start_node_id, end_node_id)
        if not path:
            raise ValueError("No valid route found between the locations.")

        # Apply traffic and weather adjustments
        adjusted_distance = _apply_traffic_adjustments(
            path, base_distance, traffic_incidents
        )
        adjusted_distance = _apply_weather_adjustments(
            adjusted_distance, weather_alerts
        )

        # Calculate travel duration
        base_speed = VEHICLE_SPEEDS.get(vehicle_type, 100)
        duration_hours = adjusted_distance / base_speed

        # Convert path to coordinate waypoints
        route_coords = [
            {
                "lat": NODE_DICT[node_id]["lat"],
                "lng": NODE_DICT[node_id]["lng"],
                "name": NODE_DICT[node_id]["name"]
            }
            for node_id in path
        ]

        logger.info(
            f"Route optimized: {len(path)} waypoints, "
            f"{adjusted_distance:.1f} km, {duration_hours:.1f} hours"
        )

        return {
            "route": route_coords,
            "node_ids": path,
            "distance_km": round(adjusted_distance, 1),
            "duration_hours": round(duration_hours, 2),
            "vehicle_type": vehicle_type,
            "base_distance_km": round(base_distance, 1)
        }

    except Exception as e:
        logger.error(f"Route optimization failed: {e}")
        return {"error": str(e)}

def _dijkstra(
    start: str,
    end: str
) -> Tuple[List[str], float]:
    """
    Finds the shortest path between two nodes using Dijkstra's algorithm.

    Args:
        start: Starting node ID
        end: Destination node ID

    Returns:
        Tuple of (path node IDs, total distance in km)
    """
    import heapq

    # Priority queue: (distance, node_id)
    pq = [(0.0, start)]
    distances = {start: 0.0}
    previous = {start: None}
    visited = set()

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_node == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = previous[node]
            path.reverse()
            return path, current_dist

        if current_node in visited:
            continue

        visited.add(current_node)

        # Explore neighbors
        for neighbor, edge_dist in ADJACENCY_LIST.get(current_node, {}).items():
            if neighbor in visited:
                continue

            new_dist = current_dist + edge_dist

            if neighbor not in distances or new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))

    return [], 0.0  # No path found

def _apply_traffic_adjustments(
    path: List[str],
    base_distance: float,
    traffic_incidents: List[Dict[str, Any]]
) -> float:
    """
    Adjusts route distance based on traffic incidents.
    Increases distance if detours required, or adds time penalty.

    Args:
        path: List of node IDs in route
        base_distance: Base route distance in km
        traffic_incidents: List of traffic incidents

    Returns:
        Adjusted distance accounting for traffic delays
    """
    from ..utils.geospatial import calculate_distance

    total_delay_km = 0.0

    # For each node in path, check if affected by incidents
    for node_id in path:
        node = NODE_DICT.get(node_id)
        if not node:
            continue

        node_coords = (node["lat"], node["lng"])

        for incident in traffic_incidents:
            inc_coords = (
                incident["location"]["lat"],
                incident["location"]["lng"]
            )
            distance_to_incident = calculate_distance(node_coords, inc_coords)

            # If incident is within 5km of this node
            if distance_to_incident <= 5.0:
                delay_minutes = incident.get("delay_minutes", 0)
                # Convert delay to distance equivalent at base speed
                base_speed = 100  # km/h (average)
                delay_hours = delay_minutes / 60.0
                delay_km = delay_hours * base_speed
                total_delay_km += delay_km
                logger.debug(
                    f"Traffic incident on {incident['road']} "
                    f"adds {delay_km:.1f} km equivalent"
                )
                break  # Only count one incident per node

    return base_distance + total_delay_km

def _apply_weather_adjustments(
    base_distance: float,
    weather_alerts: List[Dict[str, Any]]
) -> float:
    """
    Adjusts route distance/time based on weather conditions.

    Args:
        base_distance: Base route distance in km
        weather_alerts: List of weather alerts

    Returns:
        Adjusted distance accounting for weather speed reductions
    """
    if not weather_alerts:
        return base_distance

    # Find most severe weather alert
    max_severity = "low"
    for alert in weather_alerts:
        severity = alert.get("severity", "low")
        severity_order = ["low", "medium", "high", "extreme"]
        if severity_order.index(severity) > severity_order.index(max_severity):
            max_severity = severity

    # Apply multiplier to convert to distance equivalent
    from .weather_monitor import get_weather_impact_multiplier

    multiplier = get_weather_impact_multiplier(max_severity)

    # Effective distance = base * (multiplier - 1)
    weather_penalty_km = base_distance * (multiplier - 1)

    logger.info(
        f"Weather adjustment: {max_severity} severity "
        f"adds {weather_penalty_km:.1f} km equivalent"
    )

    return base_distance + weather_penalty_km
