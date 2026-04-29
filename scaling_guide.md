# Scaling & Performance Guide

Optimizing performance and scaling the Smart Route Optimizer for high workloads.

## Performance Characteristics

### Baseline Performance

| Operation | Typical Latency | Resource Usage |
|-----------|----------------|----------------|
| Geocoding lookup (cached) | <2ms | Negligible |
| Dijkstra route calculation (9 nodes) | ~20ms | Low CPU |
| Dijkstra route calculation (35 nodes) | ~45ms | Low-Moderate CPU |
| Traffic incident check | <5ms | Negligible |
| Weather alert fetch | <5ms | Negligible |
| PDF report generation | 50–150ms | Moderate CPU/memory |
| GPX file generation | <10ms | Negligible |

### Throughput Capacity (single instance)

- Approx. **200–300 requests/minute** (burst up to 500)
- Memory: ~150–250 MB resident
- CPU: ~100–200m per request

## Horizontal Scaling

### Kubernetes HPA (Horizontal Pod Autoscaler)

Already configured in `k8s/hpa.yaml`:

- **Target CPU:** 70%
- **Target Memory:** 75%
- **Min Replicas:** 2
- **Max Replicas:** 10

To modify:

```bash
kubectl edit hpa route-optimizer-hpa -n route-optimizer
```

### Custom Metrics Autoscaling

Consider scaling based on request rate or queue length:

```yaml
metrics:
  - type: External
    external:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

Requires Prometheus Adapter or Keda.

## Caching Strategies

### In-Memory LRU Cache

Add for repeated geocode lookups and route results:

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def get_cached_route(start_addr, end_addr, vehicle_type, region):
    # Calculate route
    return optimized_route
```

### Redis Cache (distributed)

For multi-pod deployments, use Redis to share cache:

```python
import redis
import pickle
import hashlib

redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_cached_route(...):
    key = hashlib.sha256(f"{start}:{end}:{vehicle}:{region}".encode()).hexdigest()
    cached = redis_client.get(key)
    if cached:
        return pickle.loads(cached)
    # compute route...
    redis_client.setex(key, 300, pickle.dumps(result))  # 5 min TTL
    return result
```

## Database Considerations

Currently using JSON files which are fast enough for demo. For production with large national network:

- Keep road network in memory (already loaded as module-level dict)
- Consider **SQLite** or **PostgreSQL + PostGIS** for large network with dynamic updates
- Load graph once per process, not per request

## Asynchronous Processing

Long-running PDF/GPX generation could be offloaded to background workers using **Celery** + **Redis/RabbitMQ**:

- FastAPI endpoint returns job ID
- Worker generates report asynchronously
- Client polls for completion or uses websockets

## Load Balancer Configuration

For K8s ingress, configure keepalive and timeouts:

```yaml
nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
nginx.ingress.kubernetes.io/proxy-connect-timeout: "10"
nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
```

## Database (Graph) Optimization

If scaling to continent-wide graph (thousands of nodes):

- Use **Contraction Hierarchies** or **Hub Labels** for faster shortest-path queries (~microseconds)
- Precompute distance matrix for major cities
- Consider **OSRM** or **Valhalla** as backend instead of Dijkstra
- Use **A* algorithm** with heuristic for large networks

## Monitoring Metrics

Key metrics to watch:

| Metric | Target | Alert if |
|--------|--------|----------|
| Request latency 95th percentile | <200ms | >500ms |
| Request rate | — | <10 req/s (potential issue) |
| Pod CPU usage | <70% | >85% average |
| Pod memory usage | <80% | >90% |
| HPA replica count | — | at max limit |

Set up Grafana alerts.

## Stress Testing

Use `locust` or `hey`:

```bash
hey -n 1000 -c 50 http://localhost:8000/optimize/
```

Observe:
- Response time distribution
- Error rate
- Pod autoscaling triggers
- PVC storage consumption

## Optimization Tips

### Graph Preprocessing

- Compute all-pairs shortest path for top 35 cities (only 1,225 pairs) at startup
- Store in adjacency structure for O(1) lookups between major nodes
- Fall back to Dijkstra for less common routes

### Route Caching

Many popular routes (Sydney→Melbourne, etc.) repeat. Cache results for 5 minutes.

### PDF Report Pre-generation

Common route templates could be pre-generated statically; but not needed.

## Cost Estimation (Cloud)

### Minimum Viable (Small Traffic)

- 2 x t3.medium (2 vCPU, 4 GB) – $70/mo
- LoadBalancer – $20/mo
- EBS 1 GiB – $1/mo
- **Total ~$100/mo**

### Medium Scale (hundreds of daily users)

- 5 x m5.large (2 vCPU, 8 GB) – ~$180/mo
- ALB + WAF – $50/mo
- EBS 5 GiB – $5/mo
- CloudWatch logs – $10/mo
- **Total ~$250/mo**

### Enterprise (thousands daily)

- 10+ x m5.xlarge (4 vCPU, 16 GB)
- Multi-AZ
- Redis cache
- RDS PostgreSQL + PostGIS
- **Total $800–1500/mo**

---

## Multi-Region Deployment (Future)

If expanding to serve global users or separate continents:

- Deploy separate clusters in each region ( Sydney AWS AP-Southeast-2, etc.)
- Use Cloudflare or global load balancer for routing
- GeoIP-based routing to nearest cluster
- Replicate data via CRDT or vendor-managed DB

---

## Security Scaling

- Add **rate limiting** (e.g., 60 requests/minute per IP) via API gateway or nginx
- Add **WAF** to block injection attacks
- Deploy **API keys** or **OAuth2** for access control
- VPN or private endpoints for enterprise clients

---

## Best Practices Checklist

- [x] HPA enabled with CPU/memory targets
- [x] Resource limits set on all pods
- [x] Liveness/readiness probes configured
- [x] Health endpoint available at `/health`
- [x] Metrics exposed at `/metrics`
- [ ] Redis cache layer (optional)
- [ ] Celery async worker for reports (optional)
- [ ] API gateway with rate limiting (optional)
- [ ] External PostgreSQL for route storage if needed

---

For issues or questions, open an issue on GitHub.
