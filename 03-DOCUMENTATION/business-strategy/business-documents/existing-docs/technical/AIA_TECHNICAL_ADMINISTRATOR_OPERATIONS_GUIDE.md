# AIA Technical Administrator Operations Guide
## Comprehensive System Administration and Maintenance Manual

**Document Version**: 1.0
**Last Updated**: October 3, 2025
**Target Audience**: Technical Administrators, DevOps Engineers, System Architects
**System**: AIA Production Environment (013a.tech)

---

## 📚 TABLE OF CONTENTS

1. [System Architecture Overview](#system-architecture-overview)
2. [Deployment and Maintenance Procedures](#deployment-and-maintenance-procedures)
3. [Troubleshooting Common Issues](#troubleshooting-common-issues)
4. [Performance Monitoring and Optimization](#performance-monitoring-and-optimization)
5. [Security Management](#security-management)
6. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
7. [Scaling and Capacity Planning](#scaling-and-capacity-planning)
8. [Maintenance Windows and Updates](#maintenance-windows-and-updates)
9. [Incident Response Procedures](#incident-response-procedures)
10. [Best Practices and Guidelines](#best-practices-and-guidelines)

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

### High-Level Architecture

```mermaid
graph TB
    Internet[Internet Traffic] --> CF[Cloudflare CDN]
    CF --> LB[GCP Load Balancer]
    LB --> Ingress[Kubernetes Ingress]

    Ingress --> Frontend[Frontend Service]
    Ingress --> Backend[Backend API Service]

    Frontend --> React[React App Pod]
    Backend --> API[FastAPI Pod]

    API --> DB[(PostgreSQL)]
    API --> Cache[(Redis Cache)]
    API --> MAS[Multi-Agent System]

    Monitor[Prometheus/Grafana] --> API
    Monitor --> DB
    Monitor --> Cache
```

### Core Components

#### Frontend Layer
- **Technology**: React 18 + TypeScript + Three.js
- **Build System**: Vite with optimized bundling
- **Deployment**: Nginx container serving static assets
- **CDN**: Cloudflare with asset optimization
- **Performance**: Code splitting, lazy loading, PWA features

#### Backend API Layer
- **Framework**: FastAPI (Python 3.12)
- **Architecture**: Multi-agent orchestration system
- **Authentication**: JWT with Redis session management
- **API Gateway**: Built-in FastAPI routing with CORS
- **Documentation**: Auto-generated OpenAPI/Swagger

#### Data Layer
- **Primary Database**: PostgreSQL 15 with extensions
  - UUID support, full-text search, JSON operations
  - Connection pooling with SQLAlchemy async
- **Cache Layer**: Redis 7 for session and data caching
- **Backup Strategy**: Automated daily backups with 30-day retention

#### Infrastructure Layer
- **Container Platform**: Google Kubernetes Engine (GKE)
- **Node Configuration**: Auto-scaling e2-standard-4 instances
- **Network**: VPC with private subnets and firewall rules
- **Load Balancing**: GCP Load Balancer with health checks
- **DNS**: Cloudflare DNS with 1-minute TTL

### Service Mesh Architecture

```yaml
# Service Dependencies
Frontend Service:
  - Depends on: Backend API Service
  - Port: 80 (HTTP)
  - Replicas: 2-5 (auto-scaling)

Backend API Service:
  - Depends on: PostgreSQL, Redis
  - Port: 8000 (HTTP), 8080 (Metrics)
  - Replicas: 2-10 (auto-scaling)

PostgreSQL:
  - Port: 5432
  - Replicas: 1 (primary) + read replicas
  - Storage: Persistent SSD

Redis:
  - Port: 6379
  - Replicas: 1 (with backup)
  - Memory: 256MB with LRU eviction
```

---

## 🚀 DEPLOYMENT AND MAINTENANCE PROCEDURES

### Standard Deployment Workflow

#### 1. Pre-Deployment Checks
```bash
#!/bin/bash
# Pre-deployment validation script

echo "🔍 Starting pre-deployment validation..."

# Check cluster health
kubectl get nodes -o wide
kubectl get pods --all-namespaces | grep -E "Error|CrashLoopBackOff|Pending"

# Verify external connectivity
curl -f https://013a.tech/health || echo "❌ Frontend health check failed"
curl -f https://api.013a.tech/health || echo "❌ API health check failed"

# Check resource utilization
kubectl top nodes
kubectl top pods --all-namespaces | head -20

# Verify database connectivity
kubectl exec -n aia-production deployment/aia-postgres -- \
  pg_isready -U aia_user -d aia_production

# Check Redis status
kubectl exec -n aia-production deployment/aia-redis -- \
  redis-cli ping

echo "✅ Pre-deployment validation complete"
```

#### 2. Backend Deployment Process
```bash
#!/bin/bash
# Backend deployment script

NAMESPACE="aia-production"
DEPLOYMENT="aia-backend-simple"
NEW_IMAGE="gcr.io/aia-system-prod-1759055445/aia-backend:${VERSION}"

echo "🚀 Deploying backend version: ${VERSION}"

# Update deployment image
kubectl set image deployment/${DEPLOYMENT} \
  aia-api=${NEW_IMAGE} \
  -n ${NAMESPACE}

# Wait for rollout
kubectl rollout status deployment/${DEPLOYMENT} \
  -n ${NAMESPACE} \
  --timeout=600s

# Verify health after deployment
sleep 30
kubectl exec -n ${NAMESPACE} deployment/${DEPLOYMENT} -- \
  curl -f http://localhost:8000/health

# Run post-deployment tests
python -m pytest tests/integration/ -v

echo "✅ Backend deployment complete"
```

#### 3. Frontend Deployment Process
```bash
#!/bin/bash
# Frontend deployment script

NAMESPACE="aia-production"
DEPLOYMENT="aia-frontend"
NEW_IMAGE="gcr.io/aia-system-prod-1759055445/aia-frontend:${VERSION}"

echo "🚀 Deploying frontend version: ${VERSION}"

# Build and push new image
docker build -t ${NEW_IMAGE} .
docker push ${NEW_IMAGE}

# Update deployment
kubectl set image deployment/${DEPLOYMENT} \
  frontend=${NEW_IMAGE} \
  -n ${NAMESPACE}

# Wait for rollout
kubectl rollout status deployment/${DEPLOYMENT} \
  -n ${NAMESPACE} \
  --timeout=600s

# Test frontend accessibility
curl -f https://013a.tech/ || echo "❌ Frontend deployment verification failed"

echo "✅ Frontend deployment complete"
```

### Database Migration Procedures

#### Schema Migration Process
```bash
#!/bin/bash
# Database migration script

NAMESPACE="aia-production"
DB_POD=$(kubectl get pods -n ${NAMESPACE} -l app=aia-postgresql -o jsonpath='{.items[0].metadata.name}')

echo "📊 Running database migrations..."

# Create backup before migration
kubectl exec -n ${NAMESPACE} ${DB_POD} -- \
  pg_dump -U aia_user aia_production > backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
kubectl exec -n ${NAMESPACE} deployment/aia-backend-simple -- \
  python -m alembic upgrade head

# Verify migration success
kubectl exec -n ${NAMESPACE} ${DB_POD} -- \
  psql -U aia_user -d aia_production -c "SELECT version_num FROM alembic_version;"

echo "✅ Database migration complete"
```

### Configuration Updates

#### ConfigMap Updates
```bash
#!/bin/bash
# Configuration update script

NAMESPACE="aia-production"
CONFIG_NAME="aia-backend-config"

# Update configuration
kubectl create configmap ${CONFIG_NAME}-new \
  --from-file=config/ \
  --dry-run=client -o yaml | kubectl apply -f -

# Update deployments to use new config
kubectl patch deployment aia-backend-simple \
  -n ${NAMESPACE} \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"aia-api","envFrom":[{"configMapRef":{"name":"'${CONFIG_NAME}'-new"}}]}]}}}}'

# Wait for rollout
kubectl rollout status deployment/aia-backend-simple -n ${NAMESPACE}

# Cleanup old config after verification
kubectl delete configmap ${CONFIG_NAME} -n ${NAMESPACE}
kubectl label configmap ${CONFIG_NAME}-new name=${CONFIG_NAME} -n ${NAMESPACE}
```

---

## 🔧 TROUBLESHOOTING COMMON ISSUES

### Issue Categories and Solutions

#### 1. Application Not Accessible (HTTP 502/503)

**Symptoms:**
- Users cannot access https://013a.tech
- HTTP 502 Bad Gateway or 503 Service Unavailable
- Load balancer health checks failing

**Diagnostic Steps:**
```bash
# Check ingress status
kubectl describe ingress --all-namespaces | grep -E "013a.tech|aia"

# Check backend pod status
kubectl get pods -n aia-production -l app=aia-backend-simple

# Check service endpoints
kubectl get endpoints -n aia-production

# Check logs for errors
kubectl logs -n aia-production deployment/aia-backend-simple --tail=100
```

**Common Solutions:**

1. **Pod Restart Required:**
```bash
kubectl rollout restart deployment/aia-backend-simple -n aia-production
kubectl rollout restart deployment/aia-frontend -n aia-production
```

2. **Service Configuration Issue:**
```bash
# Check service ports and selectors
kubectl describe service aia-backend-service-simple -n aia-production

# Verify pod labels match service selector
kubectl get pods -n aia-production --show-labels | grep aia-backend
```

3. **Resource Exhaustion:**
```bash
# Check resource usage
kubectl describe nodes
kubectl top pods -n aia-production

# Scale up if needed
kubectl scale deployment aia-backend-simple --replicas=4 -n aia-production
```

#### 2. Database Connection Issues

**Symptoms:**
- API returning database connection errors
- Slow query performance
- Connection pool exhaustion

**Diagnostic Steps:**
```bash
# Check PostgreSQL pod status
kubectl get pods -n aia-production -l app=aia-postgresql

# Check database connectivity
kubectl exec -n aia-production deployment/aia-postgres -- \
  pg_isready -U aia_user -d aia_production

# Monitor active connections
kubectl exec -n aia-production deployment/aia-postgres -- \
  psql -U aia_user -d aia_production -c "SELECT count(*) FROM pg_stat_activity;"
```

**Solutions:**

1. **Connection Pool Reset:**
```bash
# Restart API pods to reset connection pools
kubectl rollout restart deployment/aia-backend-simple -n aia-production
```

2. **Database Performance Tuning:**
```sql
-- Connect to database and run performance queries
SELECT * FROM pg_stat_activity WHERE state = 'active';
SELECT schemaname,tablename,attname,n_distinct,correlation FROM pg_stats;

-- Kill long-running queries if needed
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';
```

3. **Scale Database Resources:**
```bash
# Update PostgreSQL resource limits
kubectl patch deployment aia-postgres -n aia-production -p \
'{"spec":{"template":{"spec":{"containers":[{"name":"postgres","resources":{"limits":{"memory":"1Gi","cpu":"1000m"}}}]}}}}'
```

#### 3. High Memory/CPU Usage

**Symptoms:**
- Pods being OOMKilled
- High CPU utilization alerts
- Slow application response times

**Diagnostic Steps:**
```bash
# Check resource usage across all pods
kubectl top pods --all-namespaces | sort -k3 -nr

# Check node resource availability
kubectl describe nodes | grep -E "Allocated resources|Resource"

# Monitor specific pod resources
kubectl exec -n aia-production deployment/aia-backend-simple -- \
  ps aux | head -10
```

**Solutions:**

1. **Increase Resource Limits:**
```bash
kubectl patch deployment aia-backend-simple -n aia-production -p \
'{"spec":{"template":{"spec":{"containers":[{"name":"aia-api","resources":{"limits":{"memory":"1Gi","cpu":"1000m"},"requests":{"memory":"512Mi","cpu":"500m"}}}]}}}}'
```

2. **Scale Horizontally:**
```bash
kubectl scale deployment aia-backend-simple --replicas=5 -n aia-production
kubectl scale deployment aia-frontend --replicas=3 -n aia-production
```

3. **Optimize Application Code:**
- Review memory usage patterns in application logs
- Implement caching strategies
- Optimize database queries
- Use connection pooling effectively

#### 4. SSL/TLS Certificate Issues

**Symptoms:**
- SSL certificate warnings in browsers
- Certificate expiration alerts
- HTTPS connections failing

**Diagnostic Steps:**
```bash
# Check certificate status
echo | openssl s_client -servername 013a.tech -connect 013a.tech:443 2>/dev/null | \
  openssl x509 -noout -dates

# Check Cloudflare SSL status
curl -I https://013a.tech

# Verify DNS resolution
nslookup 013a.tech
dig 013a.tech A
```

**Solutions:**

1. **Cloudflare Certificate Renewal:**
   - Log into Cloudflare dashboard
   - Navigate to SSL/TLS > Edge Certificates
   - Check Universal SSL certificate status
   - Force renewal if necessary

2. **DNS Configuration Fix:**
```bash
# Update Cloudflare DNS via API
curl -X PUT "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{RECORD_ID}" \
  -H "Authorization: Bearer {API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"013a.tech","content":"34.118.226.10","proxied":true}'
```

---

## 📊 PERFORMANCE MONITORING AND OPTIMIZATION

### Monitoring Stack Configuration

#### Prometheus Metrics Collection
```yaml
# Key metrics to monitor
- aia_request_duration_seconds
- aia_request_total
- aia_active_connections
- aia_database_query_duration
- aia_cache_hit_ratio
- kubernetes_pod_container_resource_usage
```

#### Grafana Dashboard Setup
```bash
# Port-forward to access Grafana
kubectl port-forward -n aia-monitoring svc/grafana-service 3000:3000

# Import AIA system dashboard
curl -X POST http://admin:password@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana-aia-dashboard.json
```

### Performance Optimization Strategies

#### 1. Database Optimization

**Query Performance Monitoring:**
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries >1s
SELECT pg_reload_conf();

-- Identify slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_tup_read DESC;
```

**Index Optimization:**
```sql
-- Create performance-critical indexes
CREATE INDEX CONCURRENTLY idx_users_email_active ON users(email) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_session_logs_created_at ON session_logs(created_at);
CREATE INDEX CONCURRENTLY idx_agent_performance_timestamp ON agent_performance(created_at, agent_id);

-- Monitor index effectiveness
SELECT * FROM pg_stat_user_indexes WHERE idx_tup_read = 0;
```

#### 2. Application Performance Tuning

**Connection Pool Optimization:**
```python
# SQLAlchemy async pool configuration
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Base pool size
    max_overflow=30,  # Additional connections
    pool_timeout=30,  # Connection timeout
    pool_recycle=3600,  # Recycle connections hourly
    pool_pre_ping=True  # Validate connections
)
```

**Caching Strategy:**
```python
# Redis caching implementation
import redis.asyncio as redis
from functools import wraps

redis_client = redis.from_url("redis://aia-redis:6379")

async def cache_result(key: str, ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cached = await redis_client.get(key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            await redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

#### 3. Kubernetes Resource Optimization

**Horizontal Pod Autoscaling:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aia-backend-hpa
  namespace: aia-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: aia-backend-simple
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Vertical Pod Autoscaling:**
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: aia-backend-vpa
  namespace: aia-production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: aia-backend-simple
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: aia-api
      maxAllowed:
        cpu: "2"
        memory: "2Gi"
      minAllowed:
        cpu: "100m"
        memory: "128Mi"
```

### Performance Benchmarking

#### Load Testing Setup
```bash
#!/bin/bash
# Performance load testing script

# Install k6 if not available
curl -sLO https://github.com/grafana/k6/releases/download/v0.45.0/k6-v0.45.0-linux-amd64.tar.gz

# Run load test
k6 run --vus 50 --duration 300s load-test.js

# Monitor during test
kubectl top pods -n aia-production --sort-by=cpu
kubectl top nodes
```

**Load Test Script (load-test.js):**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up
    { duration: '5m', target: 50 }, // Stay at 50 VUs
    { duration: '2m', target: 0 },  // Ramp down
  ],
};

export default function() {
  // Test main page
  let response = http.get('https://013a.tech');
  check(response, {
    'homepage loads': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });

  // Test API health
  response = http.get('https://api.013a.tech/health');
  check(response, {
    'API health OK': (r) => r.status === 200,
    'API response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

---

## 🔐 SECURITY MANAGEMENT

### Security Monitoring and Compliance

#### Security Scanning Procedures
```bash
#!/bin/bash
# Security vulnerability scanning

# Scan container images
docker scan gcr.io/aia-system-prod-1759055445/aia-backend:latest
docker scan gcr.io/aia-system-prod-1759055445/aia-frontend:latest

# Kubernetes security scan
kubectl run --rm -it security-scan --image=aquasec/trivy:latest --restart=Never -- \
  image gcr.io/aia-system-prod-1759055445/aia-backend:latest

# Network policy validation
kubectl get networkpolicies -n aia-production
kubectl describe networkpolicy default-deny-all -n aia-production
```

#### Access Control Validation
```bash
#!/bin/bash
# RBAC and access control audit

# Check service account permissions
kubectl auth can-i --list --as=system:serviceaccount:aia-production:default

# Audit cluster-wide permissions
kubectl get clusterrolebindings -o wide

# Check pod security policies
kubectl get podsecuritypolicy
kubectl describe podsecuritypolicy restricted
```

### Incident Response Procedures

#### Security Incident Classification

| Level | Description | Response Time | Actions |
|-------|-------------|---------------|---------|
| **P0 - Critical** | Data breach, system compromise | 15 minutes | Immediate isolation, emergency team activation |
| **P1 - High** | Unauthorized access, malware detection | 30 minutes | Security team notification, enhanced monitoring |
| **P2 - Medium** | Policy violations, suspicious activity | 2 hours | Investigation, logging enhancement |
| **P3 - Low** | Configuration drift, minor issues | 24 hours | Routine remediation, documentation |

#### Incident Response Playbook

**1. Detection and Analysis**
```bash
#!/bin/bash
# Security incident detection script

# Check for suspicious activity
kubectl get events --all-namespaces | grep -E "Failed|Error|Warning"

# Audit recent access
kubectl logs -n kube-system deployment/kube-apiserver | \
  grep -E "authentication|authorization" | tail -50

# Check for unusual resource usage
kubectl top pods --all-namespaces | awk '$3 > 90 {print $0}'
```

**2. Containment and Eradication**
```bash
#!/bin/bash
# Incident containment procedures

# Isolate compromised pods
kubectl label pod suspicious-pod-name isolated=true -n aia-production
kubectl delete pod suspicious-pod-name -n aia-production --grace-period=0

# Rotate compromised credentials
kubectl delete secret aia-secrets -n aia-production
kubectl create secret generic aia-secrets --from-env-file=.env.secure

# Enable enhanced audit logging
kubectl patch configmap audit-policy -n kube-system --patch='
data:
  audit-policy.yaml: |
    apiVersion: audit.k8s.io/v1
    kind: Policy
    rules:
    - level: Request
      resources:
      - group: ""
        resources: ["*"]
'
```

**3. Recovery and Post-Incident**
```bash
#!/bin/bash
# Post-incident recovery

# Restore from clean backup
kubectl apply -f backup-manifests/clean-deployment.yaml

# Verify system integrity
kubectl get pods --all-namespaces -o wide
curl -f https://013a.tech/health
curl -f https://api.013a.tech/health

# Update security measures
kubectl apply -f security-hardening/
```

---

## 💾 BACKUP AND DISASTER RECOVERY

### Backup Strategy Overview

#### Backup Components
1. **Application Configuration**: Kubernetes manifests and configs
2. **Database Data**: PostgreSQL full backups + WAL archives
3. **User Data**: File uploads and generated content
4. **Infrastructure**: Terraform state and GCP resources

#### Backup Schedule
| Component | Frequency | Retention | Storage Location |
|-----------|-----------|-----------|------------------|
| Database | Daily at 02:00 UTC | 30 days | GCS + offsite |
| Configuration | On every deployment | 90 days | Git + GCS |
| Application State | Weekly | 12 weeks | GCS encrypted |
| Infrastructure | Daily | 30 days | Terraform Cloud |

### Database Backup Procedures

#### Automated Daily Backup
```yaml
# Kubernetes CronJob for database backup
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: aia-production
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15-alpine
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: aia-secrets
                  key: DATABASE_PASSWORD
            command:
            - /bin/bash
            - -c
            - |
              BACKUP_FILE="aia_backup_$(date +%Y%m%d_%H%M%S).sql"
              pg_dump -h aia-postgres -U aia_user aia_production > $BACKUP_FILE
              gsutil cp $BACKUP_FILE gs://aia-backups/database/
              gsutil lifecycle create gs://aia-backups/database/ <<EOF
              {
                "rule": [
                  {
                    "action": {"type": "Delete"},
                    "condition": {"age": 30}
                  }
                ]
              }
              EOF
          restartPolicy: OnFailure
```

#### Manual Backup Process
```bash
#!/bin/bash
# Manual database backup script

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="aia_manual_backup_${BACKUP_DATE}.sql"
GCS_BUCKET="gs://aia-backups/manual"

echo "🔄 Creating database backup: ${BACKUP_FILE}"

# Create full database dump
kubectl exec -n aia-production deployment/aia-postgres -- \
  pg_dump -U aia_user aia_production > ${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}

# Upload to Google Cloud Storage
gsutil cp ${BACKUP_FILE}.gz ${GCS_BUCKET}/

# Verify backup integrity
gunzip -c ${BACKUP_FILE}.gz | head -20

echo "✅ Backup completed: ${GCS_BUCKET}/${BACKUP_FILE}.gz"
```

### Disaster Recovery Procedures

#### Complete System Recovery

**1. Infrastructure Recovery**
```bash
#!/bin/bash
# Complete infrastructure recovery script

# Recreate GKE cluster
gcloud container clusters create aia-production-eu-cluster-recovery \
  --zone europe-west4-a \
  --num-nodes 3 \
  --machine-type e2-standard-4 \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10

# Get cluster credentials
gcloud container clusters get-credentials aia-production-eu-cluster-recovery \
  --zone europe-west4-a

# Restore from backup configurations
kubectl apply -f disaster-recovery/namespace-recovery.yaml
kubectl apply -f disaster-recovery/configmap-recovery.yaml
kubectl apply -f disaster-recovery/secret-recovery.yaml
```

**2. Database Recovery**
```bash
#!/bin/bash
# Database recovery from backup

# Deploy PostgreSQL instance
kubectl apply -f disaster-recovery/postgres-recovery.yaml

# Wait for pod to be ready
kubectl wait --for=condition=Ready pod -l app=aia-postgresql -n aia-production --timeout=300s

# Restore from latest backup
LATEST_BACKUP=$(gsutil ls gs://aia-backups/database/ | sort | tail -1)
gsutil cp ${LATEST_BACKUP} backup.sql.gz

# Restore database
gunzip backup.sql.gz
kubectl exec -i -n aia-production deployment/aia-postgres -- \
  psql -U aia_user aia_production < backup.sql

# Verify data integrity
kubectl exec -n aia-production deployment/aia-postgres -- \
  psql -U aia_user -d aia_production -c "SELECT COUNT(*) FROM users;"
```

**3. Application Recovery**
```bash
#!/bin/bash
# Application services recovery

# Deploy Redis cache
kubectl apply -f disaster-recovery/redis-recovery.yaml

# Deploy backend services
kubectl apply -f disaster-recovery/backend-recovery.yaml

# Deploy frontend services
kubectl apply -f disaster-recovery/frontend-recovery.yaml

# Restore ingress and load balancer
kubectl apply -f disaster-recovery/ingress-recovery.yaml

# Verify system functionality
curl -f https://013a.tech/health
curl -f https://api.013a.tech/health
```

#### Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)

| Service | RTO Target | RPO Target | Current RTO | Current RPO |
|---------|------------|------------|-------------|-------------|
| Frontend | 15 minutes | 1 hour | 10 minutes | 1 hour |
| Backend API | 30 minutes | 1 hour | 25 minutes | 1 hour |
| Database | 45 minutes | 24 hours | 40 minutes | 24 hours |
| Full System | 60 minutes | 24 hours | 55 minutes | 24 hours |

### Backup Verification and Testing

#### Monthly Backup Validation
```bash
#!/bin/bash
# Monthly backup validation script

echo "🧪 Starting monthly backup validation..."

# Get latest backup
LATEST_BACKUP=$(gsutil ls gs://aia-backups/database/ | sort | tail -1)

# Create test namespace
kubectl create namespace aia-backup-test

# Deploy test PostgreSQL instance
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-test
  namespace: aia-backup-test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres-test
  template:
    metadata:
      labels:
        app: postgres-test
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: aia_test
        - name: POSTGRES_USER
          value: test_user
        - name: POSTGRES_PASSWORD
          value: test_password
EOF

# Wait for pod ready
kubectl wait --for=condition=Ready pod -l app=postgres-test -n aia-backup-test --timeout=300s

# Restore backup to test instance
gsutil cp ${LATEST_BACKUP} test_backup.sql.gz
gunzip test_backup.sql.gz

kubectl exec -i -n aia-backup-test deployment/postgres-test -- \
  psql -U test_user aia_test < test_backup.sql

# Validate data integrity
USER_COUNT=$(kubectl exec -n aia-backup-test deployment/postgres-test -- \
  psql -U test_user -d aia_test -t -c "SELECT COUNT(*) FROM users;")

if [ "$USER_COUNT" -gt 0 ]; then
  echo "✅ Backup validation successful: $USER_COUNT users restored"
else
  echo "❌ Backup validation failed: No user data found"
fi

# Cleanup test environment
kubectl delete namespace aia-backup-test
rm test_backup.sql

echo "🧪 Backup validation complete"
```

---

## ⚡ SCALING AND CAPACITY PLANNING

### Auto-scaling Configuration

#### Horizontal Pod Autoscaler (HPA)
```bash
# Enable metrics server if not already installed
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Create HPA for backend
kubectl autoscale deployment aia-backend-simple \
  --cpu-percent=70 \
  --memory-percent=80 \
  --min=2 \
  --max=10 \
  -n aia-production

# Create HPA for frontend
kubectl autoscale deployment aia-frontend \
  --cpu-percent=70 \
  --min=2 \
  --max=5 \
  -n aia-production
```

#### Cluster Autoscaling
```bash
# Enable cluster autoscaler
gcloud container clusters update aia-production-eu-cluster \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 20 \
  --zone europe-west4-a

# Configure node pool autoscaling
gcloud container node-pools update default-pool \
  --cluster aia-production-eu-cluster \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 15 \
  --zone europe-west4-a
```

### Capacity Planning Guidelines

#### Resource Requirements by Load

| User Load | Frontend Pods | Backend Pods | DB CPU | DB Memory | Node Count |
|-----------|---------------|--------------|---------|-----------|------------|
| 100 concurrent | 2 | 2 | 200m | 512Mi | 2 |
| 500 concurrent | 3 | 4 | 500m | 1Gi | 3 |
| 1000 concurrent | 4 | 6 | 1 | 2Gi | 4 |
| 5000 concurrent | 5 | 10 | 2 | 4Gi | 8 |
| 10000 concurrent | 8 | 15 | 4 | 8Gi | 12 |

#### Performance Monitoring for Scaling Decisions
```bash
#!/bin/bash
# Capacity planning monitoring script

echo "📊 Collecting capacity planning metrics..."

# CPU and Memory utilization
kubectl top nodes
kubectl top pods --all-namespaces | grep aia

# Request latency monitoring
kubectl exec -n aia-production deployment/aia-backend-simple -- \
  curl -s http://localhost:8080/metrics | grep http_request_duration

# Database performance metrics
kubectl exec -n aia-production deployment/aia-postgres -- \
  psql -U aia_user -d aia_production -c "
    SELECT
      datname,
      numbackends,
      xact_commit,
      xact_rollback,
      blks_read,
      blks_hit,
      tup_returned,
      tup_fetched,
      tup_inserted,
      tup_updated,
      tup_deleted
    FROM pg_stat_database
    WHERE datname = 'aia_production';"

echo "📊 Capacity metrics collection complete"
```

---

## 🕐 MAINTENANCE WINDOWS AND UPDATES

### Maintenance Schedules

#### Regular Maintenance Windows
- **Weekly**: Every Sunday 02:00-04:00 UTC (Low traffic period)
- **Monthly**: First Sunday of month 01:00-05:00 UTC (Extended window)
- **Quarterly**: Security updates and major version upgrades

#### Emergency Maintenance
- **Hot fixes**: Can be deployed immediately with approval
- **Security patches**: Within 24 hours of release
- **Critical bugs**: Within 4 hours of detection

### Update Procedures

#### Kubernetes Cluster Updates
```bash
#!/bin/bash
# Cluster update procedure

# Check current version
kubectl version --short

# Check available updates
gcloud container get-server-config --zone europe-west4-a

# Update control plane first
gcloud container clusters upgrade aia-production-eu-cluster \
  --master \
  --zone europe-west4-a

# Update node pools (one at a time)
gcloud container clusters upgrade aia-production-eu-cluster \
  --zone europe-west4-a \
  --node-pool default-pool

# Verify cluster health after update
kubectl get nodes -o wide
kubectl get pods --all-namespaces | grep -E "Error|CrashLoopBackOff"
```

#### Application Updates (Blue-Green Deployment)
```bash
#!/bin/bash
# Blue-green deployment script

NAMESPACE="aia-production"
CURRENT_DEPLOYMENT="aia-backend-simple"
NEW_DEPLOYMENT="aia-backend-simple-green"
NEW_IMAGE="gcr.io/aia-system-prod-1759055445/aia-backend:${VERSION}"

echo "🔄 Starting blue-green deployment for version: ${VERSION}"

# Create green deployment
kubectl get deployment ${CURRENT_DEPLOYMENT} -n ${NAMESPACE} -o yaml | \
  sed "s/${CURRENT_DEPLOYMENT}/${NEW_DEPLOYMENT}/g" | \
  sed "s/app: aia-backend-simple/app: aia-backend-simple-green/g" | \
  sed "s|aia-backend:.*|aia-backend:${VERSION}|g" | \
  kubectl apply -f -

# Wait for green deployment to be ready
kubectl rollout status deployment/${NEW_DEPLOYMENT} -n ${NAMESPACE} --timeout=600s

# Test green deployment
kubectl run test-pod --rm -it --image=curlimages/curl --restart=Never -- \
  curl -f http://aia-backend-simple-green.${NAMESPACE}.svc.cluster.local:8000/health

# Switch service to green deployment
kubectl patch service aia-backend-service-simple -n ${NAMESPACE} -p \
  '{"spec":{"selector":{"app":"aia-backend-simple-green"}}}'

# Test production traffic
sleep 30
curl -f https://api.013a.tech/health

# If successful, clean up blue deployment
echo "✅ Green deployment successful, cleaning up blue deployment"
kubectl delete deployment ${CURRENT_DEPLOYMENT} -n ${NAMESPACE}

# Rename green to blue for next deployment
kubectl patch deployment ${NEW_DEPLOYMENT} -n ${NAMESPACE} -p \
  '{"metadata":{"name":"'${CURRENT_DEPLOYMENT}'"},"spec":{"selector":{"matchLabels":{"app":"aia-backend-simple"}},"template":{"metadata":{"labels":{"app":"aia-backend-simple"}}}}}'
```

---

## 🚨 INCIDENT RESPONSE PROCEDURES

### Incident Classification and Response

#### Incident Severity Levels

| Level | Impact | Example | Response Time | Team Size |
|-------|--------|---------|---------------|-----------|
| **P0** | Complete outage | Site down, data loss | 5 minutes | 5+ people |
| **P1** | Major degradation | Slow performance, errors | 15 minutes | 3-5 people |
| **P2** | Minor issues | Feature broken, warnings | 2 hours | 1-2 people |
| **P3** | Low impact | Cosmetic issues, monitoring | 24 hours | 1 person |

#### On-Call Rotation Schedule

| Week | Primary | Secondary | Database | Security |
|------|---------|-----------|----------|----------|
| Week 1 | DevOps Lead | SRE Engineer | DBA | Security Officer |
| Week 2 | SRE Engineer | DevOps Lead | DBA | Security Officer |
| Week 3 | Backend Lead | DevOps Lead | DBA | Security Officer |
| Week 4 | DevOps Lead | Backend Lead | DBA | Security Officer |

### Incident Response Runbook

#### P0 Incident Response (Complete Outage)

**1. Immediate Response (0-5 minutes)**
```bash
#!/bin/bash
# P0 Incident immediate response

echo "🚨 P0 INCIDENT DETECTED - COMPLETE OUTAGE"

# Check external connectivity
curl -I https://013a.tech || echo "❌ Frontend DOWN"
curl -I https://api.013a.tech/health || echo "❌ API DOWN"

# Check infrastructure status
kubectl get nodes
kubectl get pods --all-namespaces | grep -E "Error|CrashLoopBackOff|Pending"

# Check ingress and load balancer
kubectl get ingress --all-namespaces
gcloud compute forwarding-rules list

# Activate incident management
echo "📞 ACTIVATING INCIDENT RESPONSE TEAM"
# Send alerts to on-call team
# Create incident in monitoring system
```

**2. Assessment and Communication (5-15 minutes)**
```bash
#!/bin/bash
# Incident assessment phase

# Gather system status
kubectl cluster-info
kubectl get events --all-namespaces --sort-by=.metadata.creationTimestamp | tail -20

# Check monitoring dashboards
echo "📊 Check Grafana dashboards for anomalies"
echo "📈 Review Prometheus alerts"

# Collect logs from critical services
kubectl logs -n aia-production deployment/aia-backend-simple --tail=100
kubectl logs -n aia-production deployment/aia-frontend --tail=100
```

**3. Recovery Actions (15-60 minutes)**
```bash
#!/bin/bash
# Recovery actions based on root cause

# Common recovery actions
echo "🔄 Attempting automatic recovery..."

# Restart failed services
kubectl rollout restart deployment/aia-backend-simple -n aia-production
kubectl rollout restart deployment/aia-frontend -n aia-production

# Scale up critical services
kubectl scale deployment aia-backend-simple --replicas=5 -n aia-production

# Check database connectivity
kubectl exec -n aia-production deployment/aia-postgres -- pg_isready -U aia_user

# If needed, activate disaster recovery
if [ "$COMPLETE_FAILURE" = "true" ]; then
  echo "🚨 ACTIVATING DISASTER RECOVERY PROCEDURES"
  # Execute disaster recovery script
  ./disaster-recovery/full-system-recovery.sh
fi
```

#### P1 Incident Response (Major Degradation)

**1. Quick Assessment**
```bash
#!/bin/bash
# P1 Incident response

echo "⚠️ P1 INCIDENT - MAJOR DEGRADATION"

# Check performance metrics
kubectl top nodes
kubectl top pods -n aia-production

# Check error rates
kubectl logs -n aia-production deployment/aia-backend-simple | grep -i error | tail -10

# Check resource utilization
kubectl describe nodes | grep -E "Resource|Allocated"
```

**2. Performance Investigation**
```bash
#!/bin/bash
# Performance degradation investigation

# Database performance check
kubectl exec -n aia-production deployment/aia-postgres -- \
  psql -U aia_user -d aia_production -c "
    SELECT pid, state, query_start, query
    FROM pg_stat_activity
    WHERE state = 'active' AND query_start < NOW() - INTERVAL '30 seconds';"

# API response time check
curl -w "@curl-format.txt" -s -o /dev/null https://api.013a.tech/health

# Memory and CPU investigation
kubectl exec -n aia-production deployment/aia-backend-simple -- \
  ps aux | sort -k3 -nr | head -10
```

### Post-Incident Review Process

#### Incident Documentation Template
```markdown
# Post-Incident Review: [INCIDENT_ID]

**Date**: [DATE]
**Duration**: [START_TIME] - [END_TIME] UTC
**Severity**: [P0/P1/P2/P3]
**Impact**: [DESCRIPTION]

## Timeline
- [TIME]: Incident detected
- [TIME]: Response team activated
- [TIME]: Root cause identified
- [TIME]: Mitigation applied
- [TIME]: Full recovery confirmed

## Root Cause Analysis
**Primary Cause**: [DESCRIPTION]
**Contributing Factors**: [LIST]
**Technical Details**: [DETAILED_ANALYSIS]

## Response Effectiveness
**What went well**: [LIST]
**What could be improved**: [LIST]
**Response time**: [ACTUAL vs TARGET]

## Action Items
1. [ACTION_ITEM] - Owner: [NAME] - Due: [DATE]
2. [ACTION_ITEM] - Owner: [NAME] - Due: [DATE]

## Prevention Measures
- [MONITORING_IMPROVEMENT]
- [PROCESS_CHANGE]
- [TECHNICAL_IMPROVEMENT]
```

---

## 📋 BEST PRACTICES AND GUIDELINES

### Development and Deployment Best Practices

#### Code Quality Standards
```yaml
# Pre-commit hooks configuration (.pre-commit-config.yaml)
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
```

#### Security Guidelines
1. **Never commit secrets** - Use Kubernetes secrets and environment variables
2. **Least privilege principle** - Minimal required permissions only
3. **Regular updates** - Keep dependencies and base images updated
4. **Input validation** - Sanitize all user inputs
5. **Audit logging** - Log all security-relevant events

#### Performance Guidelines
1. **Resource limits** - Always set resource requests and limits
2. **Health checks** - Implement readiness and liveness probes
3. **Caching strategy** - Use Redis for frequently accessed data
4. **Database optimization** - Regular index maintenance and query optimization
5. **Monitoring** - Comprehensive metrics and alerting

### Operational Excellence

#### Documentation Standards
- All procedures documented in Markdown
- Code examples tested and verified
- Version control for all documentation
- Regular review and updates

#### Change Management
- All changes reviewed and approved
- Testing in staging environment first
- Gradual rollout with rollback plan
- Post-deployment verification

#### Communication Protocols
- Clear escalation paths
- Regular team updates
- Incident communication templates
- Knowledge sharing sessions

---

**Document Control:**
- **Version**: 1.0
- **Created**: October 3, 2025
- **Last Updated**: October 3, 2025
- **Next Review**: November 3, 2025
- **Owner**: Technical Operations Team
- **Approver**: Chief Technology Officer

**Change History:**
- v1.0: Initial creation of comprehensive technical operations guide