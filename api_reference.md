# API Reference

## Base URL

When running locally: `http://localhost:8000`

## Authentication

None required for demo. Production would implement API keys or OAuth2.

## Endpoints

### GET `/`

Serve the interactive HTML frontend.

**Response:** `text/html`

---

### GET `/health`

Health check endpoint for monitoring and load balancers.

**Response (200 OK):**
```json
{
    "status": "healthy",
    "timestamp": "2026-04-29T10:30:00"
}
```

---

### POST `/optimize/`

Optimize a route between two addresses.

**Request Body (application/json):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start_address` | string | Yes | Starting location (e.g., "Sydney, NSW") |
| `end_address` | string | Yes | Destination location |
| `vehicle_type` | string | Yes | One of: "Truck", "B-Double", "Semi-Trailer" |
| `delivery_window` | string (ISO datetime) | No | Optional delivery deadline |

**Example Request:**
```json
{
    "start_address": "Sydney, NSW",
    "end_address": "Newcastle, NSW",
    "vehicle_type": "Truck",
    "delivery_window": "2026-04-28T09:00:00"
}
```

**Response (200 OK):**
```json
{
    "route": [
        {"address": "Sydney, NSW", "lat": -33.8688, "lng": 151.2093},
        {"address": "Central Coast, NSW", "lat": -33.425, "lng": 151.3417},
        {"address": "Newcastle, NSW", "lat": -32.9282, "lng": 151.7594}
    ],
    "distance_km": 167.0,
    "duration_hours": 2.3,
    "fuel_savings": {
        "litres": 12.5,
        "cost_AUD": 20.00,
        "co2_kg": 31.2
    },
    "compliance": {
        "nhvr_compliant": true,
        "cor_compliant": true,
        "fatigue_management": {
            "duration_hours": 2.3,
            "daily_limit": 12,
            "weekly_limit": 72,
            "min_rest_hours": 7,
            "violations": [],
            "warnings": [],
            "notes": ["Compliance: OK", "Daily hours: 2.3/12h (9.7h remaining)"]
        },
        "vehicle_type": "Truck"
    },
    "report_url": "/reports/route_abc123.pdf",
    "gpx_url": "/reports/route_abc123.gpx"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid addresses, vehicle type, or route not found
- `500 Internal Server Error`: Unexpected server failure

---

### GET `/traffic/?region=NSW`

Fetch current traffic incidents for a region.

**Query Parameters:**
- `region` (optional, default: "NSW"): State/territory code

**Response (200 OK):**
```json
{
    "region": "NSW",
    "incidents": [
        {
            "type": "accident",
            "location": {"lat": -33.8523, "lng": 151.2108},
            "road": "M1 Pacific Motorway",
            "direction": "Northbound",
            "severity": "high",
            "delay_minutes": 30,
            "description": "Multi-vehicle collision"
        }
    ],
    "count": 1,
    "timestamp": "2026-04-29T10:35:00"
}
```

---

### GET `/weather/?lat=-33.8688&lng=151.2093&radius_km=50`

Fetch weather alerts for a geographic area.

**Query Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude
- `radius_km` (optional, default: 50): Search radius in kilometers

**Response (200 OK):**
```json
{
    "lat": -33.8688,
    "lng": 151.2093,
    "radius_km": 50,
    "alerts": [
        {
            "type": "storm",
            "severity": "high",
            "message": "Severe storm warning: Heavy rain and strong winds expected.",
            "location": {"lat": -33.8688, "lng": 151.2093}
        }
    ],
    "count": 1
}
```

---

### GET `/reports/{filename}`

Download a generated PDF or GPX report.

**Path Parameters:**
- `filename`: Report filename (e.g., `route_abc123.pdf`)

**Response:**
- `200 OK`: File content with appropriate `Content-Type`
- `404 Not Found`: Report does not exist
- `400 Bad Request`: Invalid filename (path traversal attempt)

**Security Note:** Filenames are sanitized to prevent directory traversal attacks. Only files within the `reports/` directory are accessible.

---

### Exception Handlers

**HTTPException:** Returns JSON with `error` and `status_code`.  
**Generic Exception:** Returns `500` with generic message; full traceback logged server-side.

---

## Data Models

### RouteRequest

```json
{
    "start_address": "string",
    "end_address": "string",
    "vehicle_type": "string",
    "delivery_window": "2026-04-28T09:00:00"  // optional ISO 8601
}
```

### RouteResponse

```json
{
    "route": [{"address": "string", "lat": float, "lng": float}],
    "distance_km": float,
    "duration_hours": float,
    "fuel_savings": {"litres": float, "cost_AUD": float, "co2_kg": float},
    "compliance": {...},
    "report_url": "/reports/...",
    "gpx_url": "/reports/..."
}
```

---

## Rate Limiting & Throttling

None enforced in demo. Production should implement:
- Per-IP rate limits (e.g., 60 requests/minute)
- API key quotas
- Request size limits

---

## OpenAPI Documentation

When the server is running, interactive API docs are available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These are auto-generated by FastAPI from the Pydantic models and type hints.

---

## Example cURL Requests

**Optimize a route:**
```bash
curl -X POST "http://localhost:8000/optimize/" \
  -H "Content-Type: application/json" \
  -d '{"start_address":"Sydney, NSW","end_address":"Newcastle, NSW","vehicle_type":"Truck"}'
```

**Get traffic incidents:**
```bash
curl "http://localhost:8000/traffic/?region=NSW"
```

**Get weather alerts:**
```bash
curl "http://localhost:8000/weather/?lat=-33.8688&lng=151.2093&radius_km=100"
```

**Download report:**
```bash
curl "http://localhost:8000/reports/route_abc123.pdf" -o report.pdf
```

---

## Error Codes

| Code | Meaning | Typical Cause |
|------|---------|---------------|
| 400 | Bad Request | Invalid vehicle type, unknown address, path traversal |
| 404 | Not Found | Report file missing |
| 500 | Internal Server Error | Unexpected exception, missing data files |

All error responses include a JSON body:
```json
{
    "error": "Human-readable message",
    "status_code": 400
}
```
