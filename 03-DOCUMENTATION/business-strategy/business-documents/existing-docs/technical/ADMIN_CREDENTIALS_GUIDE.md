# AIA System - Admin Credentials and Access Guide
**Production System v3.0.0 - October 3, 2025**

---

## 🔐 Critical Security Notice

**This document contains sensitive credentials and should be stored securely.**
- Encrypt this document when storing
- Limit access to authorized personnel only
- Rotate credentials regularly (quarterly minimum)
- Never commit this file to version control

---

## 🌐 Production System Overview

**Primary Domain**: https://013a.tech
**API Endpoint**: https://api.013a.tech
**External IP**: 35.204.144.16
**Infrastructure**: Google Cloud Platform (GKE)
**Project**: aia-system-production-2025

---

## 🎯 Admin Access Credentials

### Google Cloud Platform (GCP)

**Project**: `aia-system-production-2025`
**Service Account**: `aia-admin@aia-system-production-2025.iam.gserviceaccount.com`

```bash
# Set project context
gcloud config set project aia-system-production-2025

# Authenticate with service account
gcloud auth activate-service-account --key-file=aia-admin-sa-key.json

# Connect to Kubernetes cluster
gcloud container clusters get-credentials aia-production-cluster --zone=us-central1-a
```

### Kubernetes Cluster Access

**Cluster**: `aia-production-cluster`
**Zone**: `us-central1-a`
**Namespaces**:
- `aia-production-clean-slate` (primary)
- `aia-temp-working` (current live)
- `aia-monitoring` (monitoring stack)

```bash
# Quick cluster access
kubectl config use-context gke_aia-system-production-2025_us-central1-a_aia-production-cluster

# Check system status
kubectl get pods --all-namespaces
kubectl get services --all-namespaces
kubectl get ingress --all-namespaces
```

### Database Access

**PostgreSQL Production Database**:
- **Host**: Internal cluster IP (via k8s service)
- **Database**: `aia_production`
- **Username**: `aia_admin`
- **Password**: Stored in Google Secret Manager as `aia-db-password`

```bash
# Access via kubectl port-forward
kubectl port-forward -n aia-temp-working svc/postgres 5432:5432
psql -h localhost -U aia_admin -d aia_production
```

**Redis Cache**:
- **Host**: Internal cluster IP
- **Port**: 6379
- **Password**: Stored in Google Secret Manager as `aia-redis-password`

```bash
# Access via kubectl port-forward
kubectl port-forward -n aia-temp-working svc/redis 6379:6379
redis-cli -h localhost -p 6379 -a <password>
```

---

## 📊 Monitoring and Observability

### Grafana Dashboard

**URL**: `https://grafana.013a.tech` (when configured)
**Internal Access**: Via kubectl port-forward to grafana service
**Default Credentials**: admin / admin (change on first login)

```bash
# Access Grafana locally
kubectl port-forward -n aia-monitoring svc/grafana 3000:3000
# Open http://localhost:3000
```

### Prometheus Metrics

**Internal Endpoint**: Via kubectl port-forward to prometheus service
**Metrics Collection**: Automatic every 15 seconds

```bash
# Access Prometheus locally
kubectl port-forward -n aia-monitoring svc/prometheus 9090:9090
# Open http://localhost:9090
```

---

## 🔒 Cloudflare Management

### DNS Management Token
**Token**: `uT4LRHwxzw4n4xWfgIGcXIe72yM5Hb3sogOsW7cp`
**Scope**: DNS edit for 013a.tech zone
**Expires**: October 4, 2025 ⚠️ **RENEWAL REQUIRED**

### SSL Management Token
**Token**: `UtcOQSKFyVRRxgDLjmykFZq_Ol4VNNuEjTmKqI4r`
**Scope**: SSL certificate management
**Status**: Active

```bash
# Verify token access
curl "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer UtcOQSKFyVRRxgDLjmykFZq_Ol4VNNuEjTmKqI4r"
```

---

## 💳 Payment System Access

### Stripe Production
**Publishable Key**: `pk_live_51RtkyrD7L8T9SMaOKajUOupnjUh8wS167DUFalhTcvQwuteS2JoWjSW4XDUCIOjQLwsAQplTH91ASMSlutNZfpx300KPzFlwiL`
**Secret Key**: `[STRIPE_LIVE_KEY_PLACEHOLDER]`

⚠️ **Security**: Secret key should be stored in Google Secret Manager, not in plain text.

---

## 🛠️ Emergency Procedures

### System Restart
```bash
# Restart main application pods
kubectl rollout restart deployment aia-backend-deployment -n aia-temp-working
kubectl rollout restart deployment aia-frontend-deployment -n aia-temp-working

# Check rollout status
kubectl rollout status deployment aia-backend-deployment -n aia-temp-working
```

### Scaling Operations
```bash
# Scale backend pods
kubectl scale deployment aia-backend-deployment --replicas=5 -n aia-temp-working

# Scale frontend pods
kubectl scale deployment aia-frontend-deployment --replicas=3 -n aia-temp-working
```

### Database Backup
```bash
# Create database backup
kubectl exec -n aia-temp-working postgres-deployment -- pg_dump -U aia_admin aia_production > backup_$(date +%Y%m%d).sql

# Store backup in GCS bucket
gsutil cp backup_$(date +%Y%m%d).sql gs://aia-production-backups/
```

---

## 📞 Contact Information

**Primary Administrator**: Technical Lead
**Emergency Contact**: System Operations Team
**Escalation Path**: CTO → Technical Lead → DevOps Team

---

## 🔄 Credential Rotation Schedule

| Credential Type | Frequency | Last Rotation | Next Due |
|-----------------|-----------|---------------|----------|
| Cloudflare DNS Token | Quarterly | Sept 2025 | **Oct 4, 2025** ⚠️ |
| Database Passwords | Monthly | Oct 1, 2025 | Nov 1, 2025 |
| API Keys | Quarterly | Sept 2025 | Dec 2025 |
| SSL Certificates | Auto-renewal | Active | Auto-managed |

---

**Document Version**: 1.0
**Last Updated**: October 3, 2025
**Next Review**: November 3, 2025

⚠️ **URGENT**: Cloudflare DNS token expires tomorrow (Oct 4, 2025) - renewal required immediately.