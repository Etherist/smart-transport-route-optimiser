# Troubleshooting Guide

Common issues and solutions when running, deploying, or using the Smart Route Optimizer.

## Quick Diagnostics

Run these commands to get an overview of your system state:

```bash
# Local
docker-compose ps  # services status
docker-compose logs -f  # combined logs
uvicorn logs (if running directly)

# Kubernetes
kubectl get pods -n route-optimizer
kubectl get svc -n route-optimizer
kubectl logs -f deployment/route-optimizer-api -n route-optimizer
```

## Common Issues

### 1. Application fails to start – file not found errors

**Symptom**: `FileNotFoundError: src/data/australia_road_network.json not found`

**Cause**: Working directory is not project root or paths are incorrect.

**Fix**:

- Run from project root directory.
- Ensure `src/data/` contains `australia_road_network.json`.
- For Docker builds, ensure files are copied correctly (they are in the context).

Check:
```bash
ls -la src/data/*.json
```

### 2. Reports not downloading – 404

**Symptom**: `/reports/abc123.pdf` returns 404 after optimization.

**Cause**: Reports directory not mounted, or PDF generation failed.

**Fix**:

- Check logs for PDF generation errors
- Ensure `reports/` directory exists and is writable:

```bash
mkdir -p reports
chmod 755 reports
```

- In Kubernetes, verify PVC is bound and mounted

### 3. Tests failing – Import errors

**Symptom**: `ModuleNotFoundError: No module named 'src.agents'`

**Cause**: Python path misconfiguration.

**Fix**:

Install package in editable mode:

```bash
pip install -e .
```

Or run tests via `pytest` from project root (should use PYTHONPATH automatically). We also have a `pytest.ini` or `setup.py`? If missing, create `setup.py` but not required for this project. We can set `PYTHONPATH=.`:

```bash
PYTHONPATH=. pytest
```

### 4. Docker build fails – pip install errors

**Symptom**: `ERROR: Could not find a version that satisfies the requirement reportlab`

**Cause**: Outdated pip or missing wheel.

**Fix**:

Update pip and install build dependencies:

```bash
docker build --build-arg PIP_EXTRA_INDEX_URL=https://pypi.org/simple .
```

Or ensure Dockerfile builder stage installs `build-essential` which is already present.

### 5. Kubernetes pods stuck in `Pending`

**Symptom**: `kubectl get pods` shows `Pending` state.

**Cause**: No default storage class; PVC can't be satisfied.

**Fix**:

- Create a storage class or change PVC to use an existing one:

```bash
kubectl get storageclass
```

Then edit `k8s/pvc.yaml` to match.

Alternatively, disable PVC by patching deployment to remove volume mounts (not recommended for production).

### 6. Slow route optimization

**Symptom**: Request takes >2 seconds.

**Cause**: Cold start, or Dijkstra on large graph not optimized.

**Fix**:

- First request loads graph into memory; subsequent requests are fast
- Consider precomputing routes between major cities (caching)
- Deploy more replicas behind load balancer
- Use A* algorithm instead of Dijkstra for heuristic speed-up

### 7. ImportError: cannot import name 'loguru' or missing module

**Symptom**: `ImportError` for library in `agents` modules.

**Cause**: Missing dependency in `requirements.txt`.

**Fix**:

Add the dependency and reinstall:

```bash
pip install loguru
# or add to requirements.txt
```

We currently use standard `logging`. If we use other libs, ensure they're in requirements.

### 8. Geocoding fails for valid address

**Symptom**: `Address not found in geocoding database.`

**Cause**: Location not present in `GEOCODE_MOCK` in `route_planner.py`.

**Fix**:

Add the location to `GEOCODE_MOCK`. For production, switch to real geocoding API.

### 9. `isort` / `black` / `ruff` lint errors

**Symptom**: Pre-commit hook fails.

**Fix**:

Format code:

```bash
make format  # if Makefile exists
# or manually:
isort .
black .
```

Then re-run: `pre-commit run --all-files`

### 10. ReportLab PDF generation throws `RMLParseError`

**Symptom**: `Reportlab PDF error: RMLParseError: ...`

**Cause**: Invalid XML/HTML in story Paragraph.

**Fix**:

Ensure all HTML tags are correctly closed. Check that `styles['Normal']` exists.

### 11. Mock API server not responding

**Symptom**: Connection refused to `localhost:8001` when using frontend.

**Fix**:

Start mock server:

```bash
uvicorn scripts.mock_api_server:app --port 8001
```

Or include in Docker Compose: `docker-compose up mock-api`

### 12. CORS errors in browser

**Symptom**: `Access to fetch at ... from origin ... has been blocked by CORS policy`.

**Cause**: CORS not configured or too restrictive.

**Fix**:

`main.py` already sets `allow_origins=["*"]`. For production, restrict to your domain.

### 13. 500 errors after deployment

**Symptom**: Generic `Internal server error`.

**Fix**:

- Check server logs
- Look for stack traces
- Common reasons:
  - Missing environment variables
  - Reports dir not writable
  - Data file missing
  - Network errors if calling external APIs

### 14. Permission denied mounting volume

**Symptom**: Docker volume mount fails: `permission denied`.

**Fix**:

Adjust host directory permissions:

```bash
sudo chmod -R 755 /path/to/project/reports
```

Or run container with `:delegated` flag on macOS.

### 15. Graph edge cases: No route found

**Symptom**: `ValueError: No valid route found between the locations.`

**Cause**: Network disconnected; nodes too far apart; nearest node threshold too low.

**Fix**:

- Increase threshold in `find_nearest_node` (currently 20km)
- Add more nodes to road network
- Verify both start/end are within network coverage

---

## Getting Help

1. Check this guide and existing GitHub Issues
2. Run `diagnostics.sh` script if available (runs checks)
3. Provide:
   - Docker/K8s version
   - Python version
   - Log output
   - Steps to reproduce

---

## Debug Mode

Enable debug logging:

```python
# In .env or Config
DEBUG=True
LOG_LEVEL=DEBUG
```

Or via environment variable:

```bash
export LOG_LEVEL=DEBUG
```

Then restart services.

---

## Performance Diagnosis

Use Python profiling:

```python
import cProfile
cProfile.run('optimize_route(...)')
```

Compare timings.

---

Most issues stem from missing files or incorrect environment variables. Verify all prerequisites are met.
