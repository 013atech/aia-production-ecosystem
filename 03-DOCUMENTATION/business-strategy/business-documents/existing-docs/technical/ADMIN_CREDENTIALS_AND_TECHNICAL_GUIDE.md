# AIA System Admin Credentials & Technical Guide
*Generated: October 5, 2025*

## 🔐 Admin Access Credentials

### Production Environment Access
- **Primary Domain**: https://013a.tech
- **API Endpoint**: https://api.013a.tech
- **Admin Dashboard**: https://013a.tech/admin (when implemented)
- **Monitoring**: Grafana/Prometheus (deployed in aia-monitoring namespace)

### GCP Infrastructure Access
- **Project ID**: aia-system-prod-1759055445
- **Cluster Name**: aia-production-us-central1
- **Region**: us-central1
- **Static IP**: 34.45.144.118

### Kubernetes Access
```bash
# Connect to production cluster
gcloud container clusters get-credentials aia-production-us-central1 \
  --zone us-central1 --project aia-system-prod-1759055445

# View all deployments
kubectl get deployments -n aia-production

# View services and load balancers
kubectl get services -n aia-production

# Check pod status
kubectl get pods -n aia-production
```

## 🛠️ Technical System Architecture

### Core Services Deployed
1. **aia-frontend**: React/TypeScript frontend (3 replicas)
2. **aia-backend**: FastAPI Python backend (3 replicas)
3. **aia-ml-processor**: ML/AI processing service
4. **aia-payment-processor**: Payment handling service
5. **aia-enterprise-partners**: Enterprise integration service
6. **aia-security-service**: Security middleware
7. **aia-subscription-manager**: Subscription management

### Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **AlertManager**: Alert routing (future)

### Enterprise Integrations Active
- ✅ EY Global Integration
- ✅ JPMorgan Financial AI
- ✅ Google Cloud A2A Framework
- ✅ Apple Vision Analytics

## 📊 System Management Commands

### Health Checks
```bash
# Overall system health
curl https://013a.tech/health

# Backend API health
kubectl get pods -n aia-production -l app=aia-backend

# Frontend availability
curl -I https://013a.tech
```

### Scaling Operations
```bash
# Scale frontend replicas
kubectl scale deployment aia-frontend --replicas=5 -n aia-production

# Scale backend replicas
kubectl scale deployment aia-backend --replicas=5 -n aia-production

# Auto-scaling (configured for 3-10 replicas based on CPU/memory)
kubectl get hpa -n aia-production
```

### Log Access
```bash
# Backend logs
kubectl logs -f deployment/aia-backend -n aia-production

# Frontend logs
kubectl logs -f deployment/aia-frontend -n aia-production

# All services logs
kubectl logs -l app.kubernetes.io/name=aia-system -n aia-production
```

## 🔧 Configuration Management

### Environment Variables
Core secrets managed via Kubernetes secrets:
- `aia-secrets`: Database connections, API keys
- `enterprise-secrets`: Partner integration credentials

### DNS & SSL Configuration
- **DNS Provider**: Cloudflare
- **SSL**: Full (strict) with edge certificates
- **CDN**: Enabled with optimizations
- **Security**: High level with DDoS protection

### Database Connections
- **Primary**: Cloud SQL instance (connection may need restoration)
- **Redis**: In-cluster caching
- **Monitoring**: Prometheus metrics storage

## 📈 Monitoring & Analytics

### Key Metrics to Monitor
1. **Response Times**: < 100ms target
2. **Uptime**: 99.9% SLA target
3. **Error Rates**: < 0.1% target
4. **Resource Usage**: CPU < 70%, Memory < 80%

### AIA Backend Processing
- **Local Development**: http://localhost:8000
- **Knowledge Graph**: Semantic search enabled
- **Business Intelligence**: Automated cycles active
- **Multi-Agent System**: Fully operational

### Verification Cycles
- **Unlimited verification cycles**: Active background process
- **Cycle interval**: 60 seconds
- **Results**: Saved to verification_cycle_*.json files

## 🚨 Troubleshooting

### Common Issues
1. **Pods in Pending State**: Usually resource quota limitations
2. **502/503 Errors**: Check backend deployment health
3. **SSL Issues**: Verify Cloudflare SSL mode (Full/Strict)

### Emergency Procedures
```bash
# Restart all services
kubectl rollout restart deployment -n aia-production

# Emergency scale down
kubectl scale deployment --all --replicas=1 -n aia-production

# Check resource quotas
gcloud compute project-info describe --project=aia-system-prod-1759055445
```

## 📞 Support & Maintenance

### Daily Operations
1. Monitor verification cycle results
2. Check system health endpoints
3. Review resource usage metrics
4. Validate all enterprise integrations

### Weekly Operations
1. Review and rotate logs
2. Update security patches
3. Performance optimization review
4. Backup verification

### System Updates
All deployments managed via:
- `deploy-full-complexity-aia.sh`: Complete system deployment
- `holistic_deployment_strategy.py`: Strategic deployment planning
- `unlimited_verification_cycles.py`: Continuous monitoring

---
*This guide provides comprehensive technical access for AIA system administration. Keep credentials secure and follow security best practices.*