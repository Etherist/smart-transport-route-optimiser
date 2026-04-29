import os
import uuid
import logging
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from src.agents.route_planner import plan_route
from src.agents.traffic_monitor import fetch_traffic_incidents
from src.agents.weather_monitor import fetch_weather_alerts
from src.agents.route_optimizer import optimize_route
from src.agents.compliance_validator import validate_compliance
from src.agents.savings_reporter import generate_report, generate_gpx_route

from src.app.models import RouteRequest, RouteResponse
from src.utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Route Optimizer API",
    description="AI-powered route optimization for Australian transport",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/app/static"), name="static")

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

# Resolved reports directory for secure file serving
REPORTS_DIR = Path("reports").resolve()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML frontend."""
    return FileResponse("src/app/static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/optimize/", response_model=RouteResponse)
async def optimize_route_endpoint(request: RouteRequest):
    """
    Optimize a route between two addresses with comprehensive national coverage.

    - **start_address**: Starting location (e.g., "Sydney, NSW" or "Melbourne, VIC")
    - **end_address**: Destination location (e.g., "Brisbane, QLD")
    - **vehicle_type**: One of 13 vehicle types (Rigid, Truck, Semi-Trailer, B-Double, B-Triple, Tautliner, Reefer, Flatbed, Dump Truck, Tanker, Livestock Carrier, Car Carrier, Container Hauler)
    - **delivery_window**: Optional delivery deadline
    - **region**: Optional state override (auto-detected from address if omitted)
    """
    try:
        # Determine region/state from address or explicit parameter
        region = request.region if request.region else _detect_region_from_address(
            request.start_address, request.end_address
        )

        logger.info(
            f"Optimization request: {request.start_address} → {request.end_address} "
            f"({request.vehicle_type}) Region: {region}"
        )

        # Step 1: Plan the route (geocoding)
        route_request = plan_route(
            request.start_address,
            request.end_address,
            request.vehicle_type,
            request.delivery_window
        )

        # Step 2: Fetch real-time data (mock for demo)
        traffic_incidents = fetch_traffic_incidents(region)

        # Get midpoint for weather lookup
        mid_lat = (route_request["start"]["lat"] + route_request["end"]["lat"]) / 2
        mid_lng = (route_request["start"]["lng"] + route_request["end"]["lng"]) / 2
        weather_alerts = fetch_weather_alerts(mid_lat, mid_lng)

        # Step 3: Optimize route using national network
        optimized_route = optimize_route(route_request, traffic_incidents, weather_alerts)

        if "error" in optimized_route:
            raise HTTPException(status_code=400, detail=optimized_route["error"])

        # Step 4: Validate compliance with NHVR weight/height state rules if needed
        compliance = validate_compliance(optimized_route, request.vehicle_type, region=region)

        # Step 5: Calculate savings vs. baseline (simplified heuristic: 15% longer)
        baseline_distance = optimized_route["distance_km"] * 1.15
        baseline_route = {
            "distance_km": baseline_distance,
            "duration_hours": baseline_distance / 100  # Assume 100 km/h average
        }

        # Generate unique report filenames
        report_id = str(uuid.uuid4())[:8]
        report_filename = f"route_{report_id}.pdf"
        gpx_filename = f"route_{report_id}.gpx"
        report_path = os.path.join("reports", report_filename)
        gpx_path = os.path.join("reports", gpx_filename)

        # Generate PDF report with enhanced content
        savings = generate_report(
            optimized_route, baseline_route, request.vehicle_type, report_path,
            region=region, traffic_incidents=traffic_incidents, weather_alerts=weather_alerts
        )

        # Generate GPX file
        generate_gpx_route(optimized_route, gpx_path)

        # Prepare response
        response = RouteResponse(
            route=optimized_route["route"],
            distance_km=optimized_route["distance_km"],
            duration_hours=optimized_route["duration_hours"],
            fuel_savings=savings["fuel_savings"],
            compliance=compliance,
            report_url=f"/reports/{report_filename}",
            gpx_url=f"/reports/{gpx_filename}"
        )

        logger.info(f"Optimization complete: {optimized_route['distance_km']:.1f}km, Region: {region}")
        return response

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


def _detect_region_from_address(start_addr: str, end_addr: str) -> str:
    """
    Auto-detects Australian state/territory from address strings.
    Supports multi-state routes and falls back to NSW if ambiguous.

    Args:
        start_addr: Start address string
        end_addr: End address string

    Returns:
        State/territory identifier ("NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT")
    """
    # State identifiers and their variants
    state_patterns = {
        "NSW": ["nsw", "new south wales"],
        "VIC": ["vic", "victoria"],
        "QLD": ["qld", "queensland"],
        "SA": ["sa", "south australia"],
        "WA": ["wa", "western australia"],
        "TAS": ["tas", "tassie", "tasmania"],
        "NT": ["nt", "northern territory"],
        "ACT": ["act", "a.c.t.", "canberra"]
    }

    combined = (start_addr + " " + end_addr).lower()

    for state, patterns in state_patterns.items():
        for pattern in patterns:
            if pattern in combined:
                return state

    # Default to NSW for backward compatibility
    return "NSW"

@app.get("/traffic/")
async def get_traffic(region: str = "NSW"):
    """Fetch traffic incidents for a region."""
    try:
        incidents = fetch_traffic_incidents(region)
        return {"region": region, "incidents": incidents, "count": len(incidents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/")
async def get_weather(lat: float, lng: float, radius_km: int = 50):
    """Fetch weather alerts for coordinates."""
    try:
        alerts = fetch_weather_alerts(lat, lng, radius_km)
        return {"lat": lat, "lng": lng, "radius_km": radius_km, "alerts": alerts, "count": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/{filename}")
async def get_report(filename: str):
    """Download a generated report."""
    # Prevent path traversal attacks
    reports_dir = REPORTS_DIR
    # Resolve the full path and ensure it stays within reports directory
    file_path = (reports_dir / filename).resolve()
    if not str(file_path).startswith(str(reports_dir)):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    # Determine media type
    media_type = "application/pdf" if filename.endswith(".pdf") else "text/plain"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
