# Deployment Guide

This guide covers all deployment options for the Smart Route Optimizer, from local development to production Kubernetes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Production Hardening](#production-hardening)
- [Monitoring & Observability](#monitoring--observability)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Common Requirements

- **Python 3.11+** (for local non-containerized development)
- **Docker 20.10+** and **Docker Compose v2** (for containerization)
- **kubectl** configured to your Kubernetes cluster (for K8s deployment)
- **helm** (optional, for package management)
- **git** for version control

### Optional Integrations

- **Google Maps Geocoding API** – for real address resolution (currently using mock database)
- **Live Traffic NSW / VicRoads / QLD Traffic APIs** – for real-time traffic
- **Bureau of Meteorology (BOM) API** – for real weather data
- **Sentry** – for error tracking

## Local Development

### Option 1: Bare Python (fastest iteration)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn src.app.main:app --reload --port 8000

# In another terminal, run mock traffic/weather API
uvicorn scripts.mock_api_server:app --port 8001

# Open browser
# http://localhost:8000
```

### Option 2: Docker Compose (full stack)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Remove volumes (including reports)
docker-compose down -v
```

## Docker Deployment

### Build Production Image

```bash
# Build the image
docker build -t route-optimizer:latest .

# Test locally
docker run -p 8000:8000 --env-file .env route-optimizer:latest
```

### Push to Container Registry

```bash
# Tag for your registry
docker tag route-optimizer:latest ghcr.io/yourorg/route-optimizer:1.0.0

# Push
docker push ghcr.io/yourorg/route-optimizer:1.0.0
```

### Docker Run (standalone)

```bash
docker run -d \
  --name route-optimizer \
  -p 8000:8000 \
  --restart unless-stopped \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/src/data:/app/src/data:ro \
  -e LIVE_TRAFFIC_NSW_API_KEY=${LIVE_TRAFFIC_NSW_API_KEY} \
  -e BOM_API_KEY=${BOM_API_KEY} \
  route-optimizer:latest
```

## Kubernetes Deployment

### 1. Namespace & Config

Apply namespace and config first:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
```

### 2. Persistent Volume Claim

```bash
kubectl apply -f k8s/pvc.yaml
```

> **Note**: The PVC uses the `standard` storage class. Adjust `storageClassName` for your cluster (e.g., `gp2` on AWS EKS, `managed-premium` on AKS).

### 3. Deploy Application

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 4. Ingress (optional, for external access)

```bash
kubectl apply -f k8s/ingress.yaml
```

If you don't have an ingress controller, use a LoadBalancer or NodePort service:

```bash
kubectl patch svc route-optimizer-api -n route-optimizer \
  -p '{"spec": {"type": "LoadBalancer"}}'
```

### 5. Horizontal Pod Autoscaler (autoscaling)

```bash
kubectl apply -f k8s/hpa.yaml
```

### Verify Deployment

```bash
# Check pods status
kubectl get pods -n route-optimizer

# Check service
kubectl get svc -n route-optimizer

# Check HPA
kubectl get hpa -n route-optimizer

# View logs
kubectl logs -f deployment/route-optimizer-api -n route-optimizer

# Port-forward for local testing
kubectl port-forward svc/route-optimizer-api 8000:80 -n route-optimizer
```

## Production Hardening

### Security

- **Use TLS**: Configure cert-manager for automatic Let's Encrypt certificates
- **Network Policies**: Restrict pod-to-pod communication
- **Secrets Management**: Use external secret stores (AWS Secrets Manager, HashiCorp Vault)
- **Image Scanning**: Scan container images for vulnerabilities
- **Run-as-NonRoot**: Already enabled in deployment

Example NetworkPolicy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: route-optimizer-allow-only-ingress
  namespace: route-optimizer
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8000
```

### Resource Tuning

Adjust resource limits based on load testing:

| Metric | Minimum | Recommended | Maximum |
|--------|---------|-------------|---------|
| CPU Request | 250m | 500m | 2 |
| CPU Limit | 500m | 1 | 4 |
| Memory Request | 256Mi | 512Mi | 2Gi |
| Memory Limit | 512Mi | 1Gi | 4Gi |

## Monitoring & Observability

### Prometheus Metrics

The application exposes `/metrics` endpoint (Prometheus format). Add ServiceMonitor if using Prometheus Operator:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: route-optimizer
  namespace: route-optimizer
spec:
  selector:
    matchLabels:
      app: route-optimizer
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

### Grafana Dashboard

Import a dashboard using the metrics:

- `http_requests_total` – total API calls
- `http_request_duration_seconds` – latency
- `route_optimization_duration_seconds` – optimization time
- `report_generation_total` – PDF reports generated

### Logging

Use structured JSON logging and ship to centralized logging:

```bash
# View logs with kubectl
kubectl logs -f deployment/route-optimizer-api -n route-optimizer -c api
```

Consider using **Fluentd**, **Loki**, or **Datadog** agents.

## Troubleshooting

### Pod CrashLoopBackOff

1. Check logs: `kubectl logs <pod-name> -n route-optimizer`
2. Common causes:
   - Missing secrets – ensure secret resources applied
   - Reports directory not writable – check PVC is bound
   - Insufficient memory – increase memory limits

### 502 Bad Gateway (Ingress)

- Ensure readiness probe passes: `kubectl describe pod <pod>`
- Check service: `kubectl get endpoints -n route-optimizer`
- Verify Nginx ingress logs

### Slow Response Times

- Check database/IO wait: `kubectl top pod`
- Increase CPU limits or replica count
- Enable Redis caching for route optimizations (stretch goal)

### Cannot Access Reports

Reports are stored in `reports/` volume. Ensure PVC is mounted and not full:

```bash
kubectl exec -it <pod> -n route-optimizer -- df -h /app/reports
```

## Upgrading

Perform a rolling update:

```bash
# Update image version in deployment (or use helm upgrade)
kubectl set image deployment/route-optimizer-api \
  api=ghcr.io/yourorg/route-optimizer:1.1.0 \
  -n route-optimizer

# Watch rollout status
kubectl rollout status deployment/route-optimizer-api -n route-optimizer
```

## Scaling for High Load

- Use HPA with custom metrics (queue length, request rate)
- Consider **Redis** for route result caching
- Add CDN for static assets and report downloads
- Deploy additional replicas across multiple AZs for HA

---

For more operational guidance, refer to GitHub repository's `docs/` directory.
