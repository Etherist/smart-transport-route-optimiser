# Demo Guide

## Quick Start (3-Step Setup)

### 1. Install Dependencies

Using UV (recommended) or pip:

```bash
# With UV (fast)
uv sync

# Or with pip
pip install -r requirements.txt
```

**Requirements:**
- Python 3.10+
- Core packages: FastAPI, Uvicorn, Pandas, Geopy, ReportLab, Pytest

---

### 2. Start the Mock API Server

The demo uses mock traffic and weather data. Start the mock server in one terminal:

```bash
python scripts/mock_api_server.py
```

This runs on `http://localhost:8001` and provides:
- `GET /traffic/{region}` – Traffic incidents
- `GET /weather/` – Weather alerts
- `GET /health` – Health check

---

### 3. Launch the Application

In a second terminal, start the FastAPI backend:

```bash
uvicorn src.app.main:app --reload
```

The `--reload` flag enables auto-restart on code changes (development only).

**Access points:**
- **Frontend UI:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Using the Web Interface

### Step 1: Enter Route Details

![Form](https://via.placeholder.com/600x200?text=Route+Input+Form)

Fields:
- **Start Address:** e.g., "Sydney, NSW"
- **End Address:** e.g., "Newcastle, NSW"
- **Vehicle Type:** Truck / B-Double / Semi-Trailer
- **Delivery Window:** (Optional) Click to set deadline

**Supported Locations** (mock database):
- NSW: Sydney, Newcastle, Wollongong, Central Coast, Gosford, Melson
- VIC: Melbourne, Geelong
- QLD: Brisbane, Gold Coast

---

### Step 2: Optimize

Click **"Optimize Route"**.

The system will:
1. Geocode the addresses
2. Fetch mock traffic incidents
3. Check weather alerts
4. Compute the optimal path
5. Validate NHVR/CoR compliance
6. Calculate fuel & CO₂ savings
7. Generate PDF + GPX reports

---

### Step 3: Review Results

The results page displays:

#### Interactive Map (Leaflet.js)
- Blue polyline showing optimized route
- Green marker: start
- Red marker: destination
- Auto-zoom to route bounds

#### Route Summary Card
- Distance (km)
- Duration (hours)
- Waypoint count

#### Savings Card
- Fuel saved (litres)
- Cost saved (AUD)
- CO₂ reduction (kg)

#### Compliance Card
- NHVR status (✅/❌)
- CoR status (✅/❌)
- Detailed fatigue management notes

#### Download
- **PDF Report** – Printable summary with route details, compliance attestation, and savings calculations
- **GPX File** – For importing into GPS navigation systems (Garmin, etc.)

---

## Command-Line Interface (CLI)

For quick tests or automation, use the built-in CLI:

```bash
python src/app/cli.py \
  --start "Sydney, NSW" \
  --end "Newcastle, NSW" \
  --vehicle-type "Truck" \
  --output-dir "reports"
```

**Options:**
- `--start`, `--end`: Addresses (required)
- `--vehicle-type`: One of Truck, B-Double, Semi-Trailer (default: Truck)
- `--delivery-window`: ISO datetime string (optional)
- `--output-dir`: Where to save reports (default: `reports/`)
- `--no-pdf`: Skip PDF generation
- `--no-gpx`: Skip GPX generation
- `--verbose, -v`: Show detailed logs

**Sample Output:**
```
==================================================
🚛 Smart Route Optimizer for Australian Transport
==================================================

📋 Optimizing route...
   From: Sydney, NSW
   To:   Newcastle, NSW
   Vehicle: Truck

📍 Planning route...
   ✓ Geocoded locations
📡 Fetching real-time data...
   ✓ 4 traffic incidents
   ✓ 2 weather alerts
🧠 Optimizing route...
   ✓ Calculated optimal path
⚖️  Checking compliance...
   ✓ NHVR Compliant: ✅ Yes
   ✓ CoR Compliant: ✅ Yes
📊 Generating reports...

✅ OPTIMIZATION COMPLETE
==================================================
📏 Distance:   167.0 km
⏱  Duration:   2.30 hours
📍 Waypoints:  3

💰 Fuel Savings: 12.50 L ($20.00)
🌍 CO₂ Reduced:  31.20 kg

✅ NHVR Compliant: Yes
✅ CoR Compliant:  Yes

📄 PDF Report:   reports/route_a1b2c3d4.pdf
🗺  GPX File:     reports/route_a1b2c3d4.gpx
==================================================
```

---

## API Usage (Direct Calls)

You can also call the API directly with `curl` or any HTTP client.

### Optimize Route

```bash
curl -X POST "http://localhost:8000/optimize/" \
  -H "Content-Type: application/json" \
  -d '{
    "start_address": "Sydney, NSW",
    "end_address": "Newcastle, NSW",
    "vehicle_type": "Truck"
  }' | python -m json.tool
```

### Get Traffic Data

```bash
curl "http://localhost:8000/traffic/?region=NSW" | python -m json.tool
```

### Get Weather Alerts

```bash
curl "http://localhost:8000/weather/?lat=-33.8688&lng=151.2093&radius_km=50" \
  | python -m json.tool
```

---

## Jupyter Notebook Demo

Open `notebooks/demo.ipynb` for an interactive walkthrough:

```bash
# If Jupyter is installed:
jupyter notebook notebooks/demo.ipynb

# Or use JupyterLab:
jupyter lab notebooks/demo.ipynb
```

The notebook demonstrates:
- Step-by-step agent execution
- Route visualization (if matplotlib/folium installed)
- Savings calculations
- Compliance checking logic

---

## Sample Routes to Try

| Start | End | Vehicle | Expected Distance |
|-------|-----|---------|------------------|
| Sydney, NSW | Newcastle, NSW | Truck | ~167 km |
| Sydney, NSW | Wollongong, NSW | B-Double | ~80 km |
| Melbourne, VIC | Geelong, VIC | Semi-Trailer | ~75 km |
| Brisbane, QLD | Gold Coast, QLD | Truck | ~80 km |

---

## Understanding the Output

### Distance & Duration

- **Distance:** Total km of optimized route (may be slightly longer than straight-line due to road network)
- **Duration:** Estimated driving time at vehicle's maximum speed, **plus** traffic/weather penalties

### Fuel Savings

Compared to a hypothetical manual route (assumed 15% longer):
- **Litres saved:** Baseline fuel − Optimized fuel
- **Cost saved:** Litres × $1.60/L (current Australian diesel price)
- **CO₂ saved:** Litres × 0.4 kg CO₂/L

### Compliance

- **NHVR Compliant:** True if route duration ≤ 12h (or vehicle-specific daily limit)
- **CoR Compliant:** True if NHVR compliant (simplified for demo)
- **Fatigue Management:** Detailed breakdown including violations, warnings, and rest recommendations

---

## Troubleshooting

### Port Already in Use

If `8000` or `8001` is occupied, kill the process:

```bash
# Find process
lsof -ti:8000

# Kill
kill -9 <PID>
```

Or change ports:
- Backend: `uvicorn src.app.main:app --reload --port 8080`
- Mock API: edit `scripts/mock_api_server.py` to use different port

### Module Import Errors

Ensure you're running commands from the project root:

```bash
cd /path/to/smart-transport-route-optimiser
python -m pytest tests/
```

If imports fail, check that `src/` is in Python path. Pytest adds it automatically via `conftest.py`.

### Missing Reports Directory

The app auto-creates `reports/` on startup. If you see file not found errors, manually create:

```bash
mkdir reports
```

### PDF Generation Fails

ReportLab requires the `reportlab` package. Reinstall:

```bash
pip install reportlab
```

Also ensure `reports/` is writable.

---

## Performance Benchmarks

On a typical laptop (Intel i5, 8GB RAM):

| Metric | Target | Actual (Demo) |
|--------|--------|---------------|
| Route optimization | < 5s | ~0.5s |
| API response time | < 1s | ~0.2s |
| Test suite execution | < 30s | ~1s |
| PDF generation | < 2s | ~0.3s |

---

## Next Steps

- **Try different vehicles:** Compare fuel rates (B-Double consumes more per km)
- **Add traffic incidents:** See how delays affect compliance
- **Test edge cases:** Try routes >12h to trigger violations
- **Inspect PDFs:** Open generated reports in `reports/` folder
- **Run test suite:** `pytest -v` to verify all 79 tests pass

---

## Real-World Deployment

For production use:
1. Replace mock APIs with Live Traffic NSW and BOM integrations
2. Use Google Maps or OpenStreetMap Nominatim for geocoding
3. Store road network in PostGIS with real NSW road data
4. Implement OR-Tools for multi-stop VRP
5. Add user authentication and audit logging
6. Deploy with Docker + HTTPS (see `Dockerfile` template in deployment docs)
