# 013a AIA System - Operations Runbook

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Access & Authentication](#access--authentication)
3. [Monitoring & Alerting](#monitoring--alerting)
4. [Deployment Procedures](#deployment-procedures)
5. [Troubleshooting](#troubleshooting)
6. [Backup & Recovery](#backup--recovery)
7. [Emergency Procedures](#emergency-procedures)

## System Architecture

### Component Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Frontend      │    │   API Gateway   │
│   (GCP LB)      │───▶│   (React)       │───▶│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Database      │    │   Cache         │
│   (Grafana)     │    │   (PostgreSQL)  │◀───│   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Network Architecture
- **Production Namespace**: `aia-production`
- **Monitoring Namespace**: `aia-monitoring`
- **Security**: Workload Identity, RBAC, Network Policies
- **Scaling**: HPA (2-5 replicas), Vertical Pod Autoscaling

## Access & Authentication

### Cluster Access
```bash
# Configure kubectl
gcloud container clusters get-credentials aia-cluster \
  --region=us-central1 \
  --project=a-467519

# Verify access
kubectl cluster-info
```

### Service Endpoints
- **Grafana Dashboard**: http://35.192.183.84
- **API Service**: http://35.225.214.87:8000
- **Frontend**: http://34.41.147.160:3000

### Secret Management
```bash
# View secrets (requires appropriate RBAC)
kubectl get secrets -n aia-production
kubectl get externalsecrets -n aia-production

# Update secrets in GCP Secret Manager
gcloud secrets versions add aia-database-url --data-file=/path/to/secret
```

## Monitoring & Alerting

### Grafana Access
- **URL**: http://35.192.183.84
- **Default Credentials**: admin/admin (change on first login)

### Key Metrics to Monitor
1. **Application Health**
   - Pod readiness/liveness
   - HTTP response times
   - Error rates

2. **Infrastructure Health**
   - CPU/Memory utilization
   - Disk space
   - Network latency

3. **Database Performance**
   - Connection pool status
   - Query performance
   - Lock contention

### Prometheus Queries
```promql
# Pod memory usage
container_memory_usage_bytes{namespace="aia-production"}

# HTTP request rate
rate(http_requests_total{namespace="aia-production"}[5m])

# Error rate
rate(http_requests_total{namespace="aia-production",status=~"5.."}[5m])
```

### Setting Up Alerts
```yaml
# Example alert rule
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: High error rate detected
```

## Deployment Procedures

### Blue-Green Deployment Process

#### 1. Prepare Green Environment
```bash
# Create green deployment
kubectl apply -f aia-deployment-green.yaml

# Wait for pods to be ready
kubectl wait --for=condition=Ready pod -l version=green -n aia-production --timeout=300s
```

#### 2. Validate Green Environment
```bash
# Check pod status
kubectl get pods -l version=green -n aia-production

# Test green service
kubectl port-forward service/aia-api-green 8001:8000 -n aia-production
curl http://localhost:8001/health
```

#### 3. Switch Traffic
```bash
# Update service selector
kubectl patch service aia-api -n aia-production -p '{"spec":{"selector":{"version":"green"}}}'

# Verify traffic switch
kubectl describe service aia-api -n aia-production
```

#### 4. Cleanup Old Version
```bash
# After validation, remove blue deployment
kubectl delete deployment aia-api-blue -n aia-production
```

### Rolling Updates
```bash
# Update image
kubectl set image deployment/aia-api-blue api=gcr.io/a-467519/aia-system:new-version -n aia-production

# Monitor rollout
kubectl rollout status deployment/aia-api-blue -n aia-production

# Rollback if needed
kubectl rollout undo deployment/aia-api-blue -n aia-production
```

### Configuration Updates
```bash
# Update ConfigMap
kubectl patch configmap aia-config -n aia-production --patch '{"data":{"LOG_LEVEL":"DEBUG"}}'

# Restart pods to pick up changes
kubectl rollout restart deployment/aia-api-blue -n aia-production
```

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting
```bash
# Check pod status
kubectl get pods -n aia-production

# Describe problematic pod
kubectl describe pod <pod-name> -n aia-production

# Check logs
kubectl logs <pod-name> -n aia-production --previous
```

#### 2. Image Pull Issues
```bash
# Check image exists
gcloud container images list-tags gcr.io/a-467519/aia-system

# Verify node can pull images
kubectl get nodes -o wide
```

#### 3. Resource Constraints
```bash
# Check node resources
kubectl top nodes

# Check pod resource usage
kubectl top pods -n aia-production

# View resource quotas
kubectl describe resourcequota -n aia-production
```

#### 4. Database Connection Issues
```bash
# Check database connectivity from pod
kubectl exec -it <pod-name> -n aia-production -- nslookup mas-system-postgres

# Test database connection
kubectl exec -it <pod-name> -n aia-production -- psql $DATABASE_URL -c "SELECT 1;"
```

#### 5. Secret Management Issues
```bash
# Check external secret status
kubectl get externalsecrets -n aia-production
kubectl describe externalsecret aia-secrets -n aia-production

# Verify GCP Secret Manager access
gcloud secrets list
gcloud secrets access-secret aia-database-url
```

### Performance Troubleshooting

#### High CPU Usage
```bash
# Check CPU metrics
kubectl top pods -n aia-production --sort-by=cpu

# Scale up if needed
kubectl scale deployment aia-api-blue --replicas=5 -n aia-production
```

#### Memory Issues
```bash
# Check memory usage
kubectl top pods -n aia-production --sort-by=memory

# Check for memory leaks in logs
kubectl logs <pod-name> -n aia-production | grep -i "memory\|oom"
```

#### Storage Issues
```bash
# Check disk usage on nodes
kubectl describe nodes | grep -A5 "Allocated resources"

# Clean up unused images
kubectl get pods --all-namespaces | grep Evicted | awk '{print $1 " " $2}' | xargs -L1 kubectl delete pod -n
```

## Backup & Recovery

### Database Backups
```bash
# Create manual backup
gcloud sql backups create --instance=mas-system-postgres --description="Manual backup $(date)"

# List backups
gcloud sql backups list --instance=mas-system-postgres

# Restore from backup
gcloud sql backups restore <backup-id> --restore-instance=mas-system-postgres
```

### Configuration Backups
```bash
# Backup all configurations
kubectl get all,configmaps,secrets,ingresses -n aia-production -o yaml > backup-$(date +%Y%m%d).yaml

# Backup RBAC
kubectl get roles,rolebindings,serviceaccounts -n aia-production -o yaml > rbac-backup-$(date +%Y%m%d).yaml
```

### Disaster Recovery
```bash
# Complete namespace recreation
kubectl delete namespace aia-production
kubectl apply -f backup-$(date +%Y%m%d).yaml
```

## Emergency Procedures

### System Down
1. **Check cluster status**
   ```bash
   kubectl get nodes
   kubectl get pods --all-namespaces
   ```

2. **Check GCP services**
   ```bash
   gcloud compute instances list
   gcloud sql instances list
   ```

3. **Scale up critical services**
   ```bash
   kubectl scale deployment aia-api-blue --replicas=5 -n aia-production
   ```

### Database Emergency
1. **Check database status**
   ```bash
   gcloud sql instances describe mas-system-postgres
   ```

2. **Enable maintenance mode**
   ```bash
   kubectl patch configmap aia-config -n aia-production --patch '{"data":{"MAINTENANCE_MODE":"true"}}'
   ```

3. **Restore from backup if needed**
   ```bash
   gcloud sql backups restore <latest-backup-id> --restore-instance=mas-system-postgres
   ```

### Security Incident
1. **Isolate affected components**
   ```bash
   kubectl scale deployment <affected-deployment> --replicas=0 -n aia-production
   ```

2. **Check logs for suspicious activity**
   ```bash
   kubectl logs -n aia-production --since=1h | grep -E "(ERROR|WARN|unauthorized|failed)"
   ```

3. **Rotate secrets**
   ```bash
   gcloud secrets versions add <secret-name> --data-file=<new-secret-file>
   kubectl rollout restart deployment/aia-api-blue -n aia-production
   ```

## Contacts & Escalation

### On-Call Procedures
1. **Level 1**: Check monitoring dashboard
2. **Level 2**: Follow troubleshooting procedures
3. **Level 3**: Escalate to DevOps team
4. **Level 4**: Contact system architect

### Communication Channels
- **Slack**: #aia-production-alerts
- **Email**: devops@013a.tech
- **Phone**: Emergency hotline

---

**Document Version**: 1.0
**Last Updated**: September 13, 2025
**Next Review**: October 13, 2025