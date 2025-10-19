# AIA SYSTEM - System Administrator Operations Guide
## Advanced Intelligence Architecture Platform - Infrastructure Operations Manual

**System Administrator Manual**
**Prepared for:** DevOps Engineers, Site Reliability Engineers, Infrastructure Teams, IT Operations
**Date:** October 3, 2025
**Version:** 4.0 Production Operations Guide

---

## 🎯 OPERATIONS OVERVIEW

This comprehensive guide provides system administrators with the knowledge and procedures required to deploy, monitor, maintain, and troubleshoot the AIA production environment. The platform is designed for high availability, scalability, and security in enterprise environments.

### Infrastructure Architecture Summary

**Production Environment Specifications**
- **Platform**: Google Kubernetes Engine (GKE) on Google Cloud Platform
- **Deployment Model**: Multi-zone, auto-scaling microservices architecture
- **High Availability**: 99.9% uptime SLA with automatic failover
- **Geographic Distribution**: Primary (us-central1), Secondary (us-east1)
- **Security Model**: Defense-in-depth with zero-trust principles

**Core Components**
- **Frontend**: React/TypeScript Progressive Web App with 3D rendering
- **Backend**: FastAPI microservices with multi-agent orchestration
- **Database**: PostgreSQL 16 with Redis caching layer
- **Monitoring**: Prometheus/Grafana with Alertmanager
- **Security**: TLS 1.3, JWT authentication, WAF protection

---

## 🚀 DEPLOYMENT PROCEDURES

### Initial Production Deployment

**Prerequisites Checklist**
```bash
# Verify required tools installation
kubectl version --client
gcloud --version
helm version
terraform --version

# Verify GCP project access and permissions
gcloud auth list
gcloud config get-value project
gcloud projects get-iam-policy $PROJECT_ID
```

**Step 1: Infrastructure Provisioning**
```bash
# Set environment variables
export PROJECT_ID="aia-system-production-2025"
export REGION="us-central1"
export CLUSTER_NAME="aia-production-cluster"

# Create GKE cluster
gcloud container clusters create $CLUSTER_NAME \
  --region=$REGION \
  --num-nodes=3 \
  --min-nodes=3 \
  --max-nodes=50 \
  --enable-autoscaling \
  --enable-autorepair \
  --machine-type=e2-standard-4 \
  --disk-size=100GB \
  --enable-network-policy \
  --enable-ip-alias
```

**Step 2: Kubernetes Configuration**
```bash
# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Create namespace
kubectl create namespace aia-production

# Apply network policies
kubectl apply -f kubernetes/network-policies.yaml

# Set up RBAC
kubectl apply -f kubernetes/rbac-config.yaml
```

**Step 3: Database Deployment**
```bash
# Deploy PostgreSQL with persistent storage
kubectl apply -f kubernetes/postgres-deployment.yaml

# Deploy Redis cluster
kubectl apply -f kubernetes/redis-deployment.yaml

# Initialize database schema
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -f /scripts/init-schema.sql
```

**Step 4: Application Deployment**
```bash
# Deploy backend services
kubectl apply -f kubernetes/backend-deployment.yaml

# Deploy frontend services
kubectl apply -f kubernetes/frontend-deployment.yaml

# Configure ingress and SSL
kubectl apply -f kubernetes/ingress-config.yaml

# Verify deployment status
kubectl get pods -n aia-production
kubectl get services -n aia-production
kubectl get ingress -n aia-production
```

### Continuous Deployment Pipeline

**GitOps Workflow**
```yaml
# .github/workflows/production-deploy.yml
name: Production Deployment
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup GCloud
        uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      - name: Build and Push Images
        run: |
          gcloud builds submit --config cloudbuild.yaml
      - name: Deploy to GKE
        run: |
          gcloud container clusters get-credentials aia-production-cluster --region us-central1
          kubectl set image deployment/aia-backend aia-api=gcr.io/$PROJECT_ID/aia-backend:$GITHUB_SHA -n aia-production
          kubectl rollout status deployment/aia-backend -n aia-production
```

**Blue-Green Deployment Strategy**
```bash
# Deploy new version to staging slot
kubectl apply -f kubernetes/blue-green-staging.yaml

# Run health checks and validation
./scripts/health-check.sh staging

# Switch traffic to new version
kubectl patch service aia-backend-service -p '{"spec":{"selector":{"version":"green"}}}'

# Monitor metrics for 10 minutes
sleep 600

# Validate deployment success or rollback
if ./scripts/validate-deployment.sh; then
  echo "Deployment successful"
  kubectl delete -f kubernetes/blue-green-staging.yaml
else
  echo "Rolling back deployment"
  kubectl patch service aia-backend-service -p '{"spec":{"selector":{"version":"blue"}}}'
fi
```

---

## 📊 MONITORING AND ALERTING

### Monitoring Stack Configuration

**Prometheus Configuration**
```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true

  - job_name: 'aia-backend'
    static_configs:
      - targets: ['aia-backend-service:8080']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'aia-frontend'
    static_configs:
      - targets: ['aia-frontend-service:3000']
    metrics_path: /api/metrics
```

**Grafana Dashboard Setup**
```bash
# Install Grafana with Helm
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.enabled=true \
  --set adminPassword=$GRAFANA_PASSWORD

# Import AIA custom dashboards
curl -X POST \
  -H "Content-Type: application/json" \
  -d @dashboards/aia-system-overview.json \
  http://admin:$GRAFANA_PASSWORD@grafana:3000/api/dashboards/db
```

**Key Metrics to Monitor**

**Application Metrics**
- **Response Time**: API endpoint response times (target: <100ms p95)
- **Throughput**: Requests per second (target: >1000 RPS sustained)
- **Error Rate**: HTTP 4xx/5xx error percentage (target: <0.1%)
- **Active Users**: Concurrent user connections (target: 10,000+)

**Infrastructure Metrics**
- **CPU Utilization**: Per-pod and cluster-wide CPU usage (alert: >80%)
- **Memory Usage**: Memory consumption patterns (alert: >85%)
- **Disk I/O**: Database and storage performance (alert: >90% utilization)
- **Network Traffic**: Ingress/egress bandwidth monitoring

**Business Metrics**
- **User Engagement**: Session duration and interaction rates
- **Feature Adoption**: 3D visualization usage statistics
- **Data Processing**: Volume and velocity of data ingestion
- **Revenue Impact**: Transaction monitoring and conversion rates

### Alerting Configuration

**Critical Alerts (PagerDuty Integration)**
```yaml
# alertmanager-config.yaml
groups:
  - name: critical-alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: DatabaseConnectionFailure
        expr: postgresql_up == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database is unreachable"
```

**Warning Alerts (Slack Integration)**
```yaml
  - name: warning-alerts
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"

      - alert: HighMemoryUsage
        expr: memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 0.5
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "API response time is slow"
```

---

## 🔧 MAINTENANCE PROCEDURES

### Routine Maintenance Tasks

**Daily Operations Checklist**
```bash
#!/bin/bash
# daily-health-check.sh

echo "=== AIA System Daily Health Check ==="
echo "Date: $(date)"

# Check cluster health
kubectl get nodes
kubectl top nodes

# Check pod status
kubectl get pods -n aia-production -o wide

# Check service endpoints
kubectl get endpoints -n aia-production

# Verify database connections
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "SELECT version();"

# Check Redis cluster status
kubectl exec -it redis-cluster-0 -n aia-production -- \
  redis-cli cluster nodes

# Review recent logs for errors
kubectl logs -n aia-production -l app=aia-backend --tail=100 | grep -i error

# Check SSL certificate expiration
echo | openssl s_client -connect 013a.tech:443 -servername 013a.tech 2>/dev/null | \
  openssl x509 -noout -dates

echo "=== Health Check Complete ==="
```

**Weekly Maintenance Tasks**
```bash
#!/bin/bash
# weekly-maintenance.sh

# Update system packages in containers
kubectl set image deployment/aia-backend aia-api=gcr.io/$PROJECT_ID/aia-backend:latest -n aia-production

# Database maintenance
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "VACUUM ANALYZE;"

# Clean up old logs and temporary files
kubectl exec -it aia-backend-0 -n aia-production -- find /tmp -type f -mtime +7 -delete

# Review and rotate API keys
./scripts/rotate-api-keys.sh

# Update monitoring dashboards
./scripts/update-grafana-dashboards.sh

# Run security vulnerability scan
trivy image gcr.io/$PROJECT_ID/aia-backend:latest
trivy image gcr.io/$PROJECT_ID/aia-frontend:latest
```

**Monthly Maintenance Tasks**
- **Capacity Planning**: Review resource utilization trends and adjust scaling policies
- **Security Updates**: Apply security patches to base images and dependencies
- **Backup Verification**: Test database backup and restoration procedures
- **Performance Tuning**: Analyze query performance and optimize slow operations
- **Cost Optimization**: Review cloud resource usage and optimize for cost efficiency

### Database Administration

**Database Backup Procedures**
```bash
# Automated backup script
#!/bin/bash
# db-backup.sh

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="/backups/aia-production-$BACKUP_DATE.sql"

# Create database backup
kubectl exec -it postgres-primary-0 -n aia-production -- \
  pg_dump -U aia_user -d aia_production --verbose --clean --no-owner --no-acl \
  --file=$BACKUP_PATH

# Upload to Cloud Storage
gsutil cp $BACKUP_PATH gs://aia-database-backups/

# Verify backup integrity
kubectl exec -it postgres-primary-0 -n aia-production -- \
  pg_restore --list $BACKUP_PATH > /dev/null && echo "Backup verified successfully"

# Clean up local backup file
rm $BACKUP_PATH

# Retain only last 30 days of backups
gsutil ls gs://aia-database-backups/ | grep "aia-production" | \
  sort | head -n -30 | xargs -I {} gsutil rm {}
```

**Database Performance Monitoring**
```sql
-- Query performance analysis
SELECT
  query,
  calls,
  total_time,
  mean_time,
  stddev_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Connection monitoring
SELECT
  count(*) as connection_count,
  state,
  client_addr
FROM pg_stat_activity
GROUP BY state, client_addr
ORDER BY connection_count DESC;

-- Database size monitoring
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

### Security Management

**SSL Certificate Management**
```bash
# Check certificate expiration
openssl x509 -in /path/to/cert.pem -noout -dates

# Renew Let's Encrypt certificates
certbot renew --nginx --dry-run

# Update Kubernetes TLS secret
kubectl create secret tls aia-tls-secret \
  --cert=/path/to/cert.pem \
  --key=/path/to/key.pem \
  --namespace=aia-production \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify certificate deployment
kubectl describe secret aia-tls-secret -n aia-production
```

**Security Scanning Procedures**
```bash
# Container image vulnerability scanning
trivy image --severity HIGH,CRITICAL gcr.io/$PROJECT_ID/aia-backend:latest

# Kubernetes cluster security scanning
kube-bench run --targets node,policies,managedservices

# Network security validation
kubectl exec -it security-scanner -n aia-production -- \
  nmap -sS -O 013a.tech

# Configuration security check
kubectl-who-can create pods --namespace aia-production
```

---

## 🚨 TROUBLESHOOTING GUIDE

### Common Issues and Resolutions

**Application Performance Issues**

*Issue: High response times (>500ms)*
```bash
# Diagnosis steps
kubectl top pods -n aia-production
kubectl logs -n aia-production -l app=aia-backend --tail=100
kubectl describe pod aia-backend-xyz -n aia-production

# Resolution steps
# 1. Scale up replicas
kubectl scale deployment aia-backend --replicas=5 -n aia-production

# 2. Check database performance
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "
    SELECT pid, query, state, query_start
    FROM pg_stat_activity
    WHERE state = 'active';"

# 3. Clear Redis cache if stale
kubectl exec -it redis-cluster-0 -n aia-production -- redis-cli flushall
```

*Issue: Memory leaks in application pods*
```bash
# Monitor memory usage over time
kubectl top pod -n aia-production --sort-by=memory

# Check for memory leaks in logs
kubectl logs -n aia-production aia-backend-xyz | grep -i "memory\|heap\|garbage"

# Restart affected pods
kubectl delete pod aia-backend-xyz -n aia-production
kubectl rollout status deployment/aia-backend -n aia-production
```

**Database Issues**

*Issue: PostgreSQL connection failures*
```bash
# Check PostgreSQL pod status
kubectl get pods -n aia-production -l app=postgres

# Verify service endpoints
kubectl get endpoints postgres-service -n aia-production

# Check connection limits
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "SHOW max_connections;"

# Monitor active connections
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "
    SELECT count(*) as active_connections
    FROM pg_stat_activity
    WHERE state = 'active';"
```

*Issue: Database disk space full*
```bash
# Check disk usage
kubectl exec -it postgres-primary-0 -n aia-production -- df -h

# Identify large tables
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "
    SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
    FROM pg_tables
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
    LIMIT 5;"

# Clean up old data (adjust retention policy)
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "
    DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days';"

# Vacuum database
kubectl exec -it postgres-primary-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "VACUUM FULL;"
```

**Networking Issues**

*Issue: Ingress not routing traffic correctly*
```bash
# Check ingress status
kubectl get ingress -n aia-production
kubectl describe ingress aia-ingress -n aia-production

# Verify backend services
kubectl get services -n aia-production
kubectl get endpoints -n aia-production

# Test internal connectivity
kubectl run debug-pod --image=busybox -n aia-production --rm -it -- /bin/sh
# Inside debug pod:
nslookup aia-backend-service
wget -qO- http://aia-backend-service:8000/health

# Check DNS resolution
kubectl exec -it aia-backend-xyz -n aia-production -- nslookup google.com
```

*Issue: SSL certificate problems*
```bash
# Check certificate status
kubectl describe secret aia-tls-secret -n aia-production

# Verify certificate validity
echo | openssl s_client -connect 013a.tech:443 -servername 013a.tech 2>/dev/null | \
  openssl x509 -noout -text

# Check Let's Encrypt certificate renewal
kubectl logs -n cert-manager cert-manager-xyz

# Manually renew if needed
kubectl annotate certificate aia-certificate cert-manager.io/issue-temporary-certificate=true -n aia-production
```

### Incident Response Procedures

**Severity Level Classification**
- **P0 (Critical)**: System down, data loss, security breach
- **P1 (High)**: Major feature unusable, significant performance degradation
- **P2 (Medium)**: Minor feature issues, moderate performance impact
- **P3 (Low)**: Cosmetic issues, minor inconveniences

**P0 Incident Response**
```bash
# 1. Immediate assessment (within 5 minutes)
kubectl get pods -n aia-production --show-labels
kubectl get events -n aia-production --sort-by='.lastTimestamp'
kubectl logs -n aia-production -l app=aia-backend --tail=50

# 2. Implement immediate mitigation
# Rollback to last known good deployment
kubectl rollout undo deployment/aia-backend -n aia-production
kubectl rollout status deployment/aia-backend -n aia-production

# 3. Escalation notification
curl -X POST https://api.pagerduty.com/incidents \
  -H "Authorization: Token token=$PAGERDUTY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "incident": {
      "type": "incident",
      "title": "AIA System P0 Incident",
      "service": {"id": "$SERVICE_ID", "type": "service_reference"}
    }
  }'

# 4. Communication to stakeholders
# Post to incident response Slack channel
# Update status page
# Notify key stakeholders via email
```

---

## 📈 PERFORMANCE OPTIMIZATION

### Scaling Strategies

**Horizontal Pod Autoscaler (HPA) Configuration**
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
    name: aia-backend
  minReplicas: 3
  maxReplicas: 50
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
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

**Cluster Autoscaler Configuration**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-status
  namespace: kube-system
data:
  nodes.max: "50"
  nodes.min: "3"
  scale-down-delay-after-add: "10m"
  scale-down-unneeded-time: "10m"
  skip-nodes-with-local-storage: "false"
  skip-nodes-with-system-pods: "false"
```

**Database Connection Pooling**
```yaml
# PgBouncer configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: pgbouncer-config
data:
  pgbouncer.ini: |
    [databases]
    aia_production = host=postgres-service port=5432 dbname=aia_production

    [pgbouncer]
    listen_addr = 0.0.0.0
    listen_port = 5432
    auth_type = md5
    auth_file = /etc/pgbouncer/userlist.txt
    pool_mode = transaction
    max_client_conn = 1000
    default_pool_size = 25
    min_pool_size = 5
    reserve_pool_size = 5
    max_db_connections = 100
```

### Caching Strategies

**Redis Cache Configuration**
```yaml
# Redis cluster configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
data:
  redis.conf: |
    maxmemory 2gb
    maxmemory-policy allkeys-lru
    save 900 1
    save 300 10
    save 60 10000
    cluster-enabled yes
    cluster-config-file nodes.conf
    cluster-node-timeout 5000
    appendonly yes
```

**Application-Level Caching**
```python
# Cache decorator for API endpoints
from functools import wraps
import redis
import json

redis_client = redis.Redis(host='redis-service', port=6379, decode_responses=True)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))

            return result
        return wrapper
    return decorator
```

---

## 🔐 SECURITY OPERATIONS

### Access Control Management

**RBAC Configuration**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: aia-admin
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints", "persistentvolumeclaims"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: aia-admin-binding
subjects:
- kind: User
  name: admin@013a.tech
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: aia-admin
  apiGroup: rbac.authorization.k8s.io
```

**Network Security Policies**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aia-backend-netpol
  namespace: aia-production
spec:
  podSelector:
    matchLabels:
      app: aia-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: aia-frontend
    - namespaceSelector:
        matchLabels:
          name: aia-production
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### Security Monitoring

**Security Event Logging**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-config
data:
  falco.yaml: |
    rules_file:
      - /etc/falco/falco_rules.yaml
      - /etc/falco/k8s_audit_rules.yaml

    json_output: true
    json_include_output_property: true

    webserver:
      enabled: true
      listen_port: 8765
      k8s_audit_endpoint: /k8s-audit

    grpc:
      enabled: true
      bind_address: "0.0.0.0:5060"

    grpc_output:
      enabled: true
```

**Intrusion Detection Rules**
```yaml
# Custom Falco rules for AIA system
- rule: Unauthorized API Access
  desc: Detect unauthorized access to AIA API endpoints
  condition: >
    ka and ka.verb in (create, update, delete) and
    ka.target.resource startswith "aia-" and
    not ka.user.name in (aia-service-account, admin@013a.tech)
  output: >
    Unauthorized API access detected (user=%ka.user.name verb=%ka.verb
    resource=%ka.target.resource)
  priority: WARNING

- rule: Suspicious Database Access
  desc: Detect unusual database connection patterns
  condition: >
    proc and proc.name=postgres and
    fd.type=ipv4 and fd.ip != 127.0.0.1 and
    not fd.ip in (aia_backend_ips)
  output: >
    Suspicious database connection (ip=%fd.rip port=%fd.rport command=%proc.cmdline)
  priority: HIGH
```

---

## 📊 REPORTING AND ANALYTICS

### System Health Reports

**Daily Operations Report**
```bash
#!/bin/bash
# generate-daily-report.sh

REPORT_DATE=$(date +%Y-%m-%d)
REPORT_FILE="/reports/aia-daily-report-$REPORT_DATE.html"

cat > $REPORT_FILE << EOF
<!DOCTYPE html>
<html>
<head>
    <title>AIA System Daily Report - $REPORT_DATE</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { background: #f5f5f5; padding: 10px; margin: 10px 0; }
        .good { color: green; }
        .warning { color: orange; }
        .critical { color: red; }
    </style>
</head>
<body>
    <h1>AIA System Daily Report - $REPORT_DATE</h1>

    <h2>System Overview</h2>
    <div class="metric">
        <strong>Uptime:</strong> $(kubectl top nodes | awk 'NR>1 {print $1, $2}')
    </div>

    <h2>Application Metrics</h2>
    <div class="metric">
        <strong>Active Pods:</strong> $(kubectl get pods -n aia-production --no-headers | grep Running | wc -l)
    </div>

    <h2>Performance Metrics</h2>
    <div class="metric">
        <strong>Average Response Time:</strong> $(grep "response_time" /var/log/aia/access.log | tail -1000 | awk '{sum+=$NF} END {print sum/NR "ms"}')
    </div>

    <h2>Error Summary</h2>
    <div class="metric">
        <strong>Error Rate:</strong> $(grep "ERROR" /var/log/aia/application.log | wc -l) errors in last 24h
    </div>

</body>
</html>
EOF

# Email report to operations team
mail -s "AIA Daily Report - $REPORT_DATE" -a "Content-Type: text/html" \
  operations@013a.tech < $REPORT_FILE
```

**Weekly Performance Analysis**
```bash
#!/bin/bash
# weekly-performance-analysis.sh

# Generate performance metrics for last 7 days
START_DATE=$(date -d "7 days ago" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)

# Query Prometheus for metrics
curl -G "http://prometheus:9090/api/v1/query_range" \
  --data-urlencode "query=rate(http_requests_total[5m])" \
  --data-urlencode "start=$START_DATE" \
  --data-urlencode "end=$END_DATE" \
  --data-urlencode "step=3600" > /tmp/request_rate.json

# Generate performance report
python3 /scripts/generate-performance-report.py \
  --metrics-file /tmp/request_rate.json \
  --output-file /reports/weekly-performance-$END_DATE.pdf
```

### Cost Analysis and Optimization

**Resource Usage Analysis**
```bash
# Generate cost analysis report
kubectl top nodes --sort-by=cpu > /tmp/node-usage.txt
kubectl top pods -n aia-production --sort-by=memory > /tmp/pod-usage.txt

# Calculate cost breakdown
python3 /scripts/calculate-costs.py \
  --node-usage /tmp/node-usage.txt \
  --pod-usage /tmp/pod-usage.txt \
  --output /reports/cost-analysis-$(date +%Y%m).json
```

---

**Contact Information:**
System Administration Team
AIA Infrastructure Operations
Email: sysadmin@013a.tech
Emergency Hotline: +1-XXX-XXX-XXXX
Operations Portal: https://013a.tech/ops-dashboard