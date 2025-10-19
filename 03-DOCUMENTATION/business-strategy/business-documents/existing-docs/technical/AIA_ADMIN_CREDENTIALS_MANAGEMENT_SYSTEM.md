# AIA Production System - Admin Credentials Management System
## Enterprise-Grade Security and Access Control

**Document Version**: 1.0
**Last Updated**: October 3, 2025
**Classification**: CONFIDENTIAL - ADMIN ONLY
**System**: AIA Production (013a.tech)

---

## 🔐 CRITICAL SECURITY NOTICE

**⚠️ WARNING: This document contains sensitive security information. Access is restricted to authorized personnel only.**

- Store credentials in encrypted password managers only
- Never commit credentials to version control
- Rotate all credentials every 90 days
- Monitor access logs for unauthorized usage
- Report security incidents immediately

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [GCP Infrastructure Access](#gcp-infrastructure-access)
3. [Kubernetes Cluster Management](#kubernetes-cluster-management)
4. [Database Access Credentials](#database-access-credentials)
5. [Monitoring System Access](#monitoring-system-access)
6. [Secret Management](#secret-management)
7. [Cloudflare CDN Management](#cloudflare-cdn-management)
8. [Emergency Access Procedures](#emergency-access-procedures)
9. [Credential Rotation Schedule](#credential-rotation-schedule)
10. [Access Audit Log](#access-audit-log)

---

## 🏗️ SYSTEM OVERVIEW

### Production Environment Details

| Component | Service | Status | Access Method |
|-----------|---------|--------|---------------|
| **Live URL** | https://013a.tech | ✅ Active | Cloudflare Proxy |
| **API Endpoint** | https://api.013a.tech | ✅ Active | GCP Load Balancer |
| **GCP Project** | `aia-system-prod-1759055445` | ✅ Active | Service Account |
| **Kubernetes** | `aia-production-eu-cluster` | ✅ Active | kubectl |
| **Database** | PostgreSQL + Redis | ✅ Active | Internal network |
| **Monitoring** | Prometheus/Grafana | ✅ Active | Port forwarding |

### Architecture Summary
```
Internet → Cloudflare → GCP Load Balancer → Kubernetes Ingress → Services
                                         ↓
                              PostgreSQL + Redis (Internal)
                                         ↓
                              Prometheus + Grafana (Monitoring)
```

---

## ☁️ GCP INFRASTRUCTURE ACCESS

### Project Information
- **Project ID**: `aia-system-prod-1759055445`
- **Project Name**: AIA System Production
- **Region**: `europe-west4` (Netherlands)
- **Zone**: `europe-west4-a`

### Service Account Access

#### Primary Admin Service Account
```json
{
  "type": "service_account",
  "project_id": "aia-system-prod-1759055445",
  "private_key_id": "[SECURE_VAULT_REFERENCE]",
  "client_email": "aia-admin@aia-system-prod-1759055445.iam.gserviceaccount.com",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

**⚠️ SECURITY NOTE**: Private key stored in encrypted vault system only.

#### Admin Access Setup
```bash
# Authenticate with service account
gcloud auth activate-service-account aia-admin@aia-system-prod-1759055445.iam.gserviceaccount.com \
  --key-file=/secure/path/to/service-account-key.json

# Set project context
gcloud config set project aia-system-prod-1759055445

# Verify access
gcloud projects describe aia-system-prod-1759055445
```

### IAM Roles and Permissions

#### Admin Roles (Production Access)
| Email | Role | Permissions | Last Login |
|-------|------|-------------|------------|
| `admin@013a.tech` | Project Owner | Full access to all resources | [Monitor] |
| `aia-admin@aia-system-prod-1759055445.iam.gserviceaccount.com` | Kubernetes Admin | Cluster management | [Active] |
| `monitoring@013a.tech` | Monitoring Admin | Read-only + alerting | [Monitor] |

#### Emergency Access
- **Break-glass Account**: `emergency-admin@013a.tech`
- **MFA Required**: Yes (Hardware token + SMS)
- **Session Duration**: 2 hours maximum
- **Approval Process**: Requires 2-person authorization

---

## ⚡ KUBERNETES CLUSTER MANAGEMENT

### Cluster Configuration
- **Cluster Name**: `aia-production-eu-cluster`
- **Location**: `europe-west4-a`
- **Node Count**: Auto-scaling (2-10 nodes)
- **Machine Type**: `e2-standard-4`
- **Kubernetes Version**: `1.28.x` (Auto-upgrade enabled)

### Kubectl Access Setup
```bash
# Get cluster credentials
gcloud container clusters get-credentials aia-production-eu-cluster \
  --zone europe-west4-a \
  --project aia-system-prod-1759055445

# Verify cluster access
kubectl cluster-info

# Check cluster status
kubectl get nodes -o wide
```

### Active Namespaces
| Namespace | Purpose | Services | Status |
|-----------|---------|----------|---------|
| `aia-production` | Main application | Backend, Frontend, DB | ✅ Active |
| `013a-analytics-production` | Analytics services | Analytics API | ✅ Active |
| `aia-production-clean-slate` | Clean deployment | Backup system | ✅ Active |
| `aia-unified-production` | Unified services | Orchestration | ✅ Active |
| `kube-system` | System services | K8s core components | ✅ Active |

### Critical Services Status
```bash
# Check all services across namespaces
kubectl get services --all-namespaces | grep -E "aia|013a"

# Monitor pod health
kubectl get pods --all-namespaces -l app.kubernetes.io/name=aia

# View resource utilization
kubectl top nodes
kubectl top pods --all-namespaces
```

---

## 🗄️ DATABASE ACCESS CREDENTIALS

### PostgreSQL Configuration

#### Primary Database (Production)
- **Host**: `aia-postgres.aia-production.svc.cluster.local`
- **Port**: `5432`
- **Database**: `aia_production`
- **Username**: `aia_user`
- **Password**: `[SECURE_VAULT_REFERENCE]`
- **Connection Pool**: 20 connections max
- **SSL Mode**: `require`

#### Connection Examples
```bash
# Port-forward for external access
kubectl port-forward -n aia-production svc/aia-postgres 5432:5432

# Connect using psql
psql -h localhost -p 5432 -U aia_user -d aia_production

# Connection string (application)
postgresql://aia_user:[PASSWORD]@aia-postgres.aia-production.svc.cluster.local:5432/aia_production?sslmode=require
```

#### Database Schema
```sql
-- Key tables
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public';

-- User management
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM agent_performance;
SELECT COUNT(*) FROM session_logs;
```

### Redis Cache Configuration

#### Cache Service Details
- **Host**: `aia-redis.aia-production.svc.cluster.local`
- **Port**: `6379`
- **Auth**: Required (password protected)
- **Password**: `[SECURE_VAULT_REFERENCE]`
- **Memory Limit**: 256MB
- **Eviction Policy**: `allkeys-lru`

#### Redis Access
```bash
# Port-forward for access
kubectl port-forward -n aia-production svc/aia-redis 6379:6379

# Connect with redis-cli
redis-cli -h localhost -p 6379 -a [PASSWORD]

# Monitor cache performance
redis-cli -h localhost -p 6379 -a [PASSWORD] INFO memory
redis-cli -h localhost -p 6379 -a [PASSWORD] MONITOR
```

---

## 📊 MONITORING SYSTEM ACCESS

### Prometheus Configuration
- **Service**: `prometheus.aia-monitoring.svc.cluster.local`
- **Port**: `9090`
- **Web UI**: http://localhost:9090 (via port-forward)
- **Retention**: 30 days
- **Scrape Interval**: 15 seconds

#### Prometheus Access
```bash
# Port-forward to access Prometheus UI
kubectl port-forward -n aia-monitoring svc/prometheus-service 9090:9090

# Query examples
curl -X GET 'http://localhost:9090/api/v1/query?query=up'
curl -X GET 'http://localhost:9090/api/v1/query?query=aia_request_duration_seconds'
```

### Grafana Configuration
- **Service**: `grafana.aia-monitoring.svc.cluster.local`
- **Port**: `3000`
- **Web UI**: http://localhost:3000 (via port-forward)
- **Admin Username**: `admin`
- **Admin Password**: `[SECURE_VAULT_REFERENCE]`

#### Grafana Access
```bash
# Port-forward to access Grafana UI
kubectl port-forward -n aia-monitoring svc/grafana-service 3000:3000

# Login: admin / [SECURE_PASSWORD]
# Navigate to: http://localhost:3000
```

### Key Monitoring Dashboards
1. **AIA System Overview**: System health and performance
2. **API Performance**: Request latency and error rates
3. **Database Metrics**: PostgreSQL and Redis performance
4. **Kubernetes Resources**: Pod and node utilization
5. **Security Monitoring**: Authentication and access logs

---

## 🔑 SECRET MANAGEMENT

### Kubernetes Secrets

#### Current Secrets Inventory
```bash
# List all secrets
kubectl get secrets --all-namespaces | grep -E "aia|013a"

# View secret details (without values)
kubectl describe secret aia-secrets -n aia-production
```

#### Secret Rotation Procedure
```bash
# Create new secret
kubectl create secret generic aia-secrets-new \
  --from-literal=DATABASE_PASSWORD='new_secure_password' \
  --from-literal=REDIS_PASSWORD='new_redis_password' \
  --from-literal=JWT_SECRET='new_jwt_secret' \
  -n aia-production

# Update deployment to use new secret
kubectl patch deployment aia-backend-simple \
  -n aia-production \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"aia-api","envFrom":[{"secretRef":{"name":"aia-secrets-new"}}]}]}}}}'

# Verify deployment
kubectl rollout status deployment/aia-backend-simple -n aia-production

# Delete old secret after verification
kubectl delete secret aia-secrets -n aia-production
kubectl label secret aia-secrets-new name=aia-secrets -n aia-production
```

### Environment Variables

#### Critical Environment Variables
| Variable | Purpose | Location | Rotation Period |
|----------|---------|----------|-----------------|
| `DATABASE_URL` | PostgreSQL connection | K8s Secret | 90 days |
| `REDIS_URL` | Redis connection | K8s Secret | 90 days |
| `JWT_SECRET_KEY` | API authentication | K8s Secret | 30 days |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | ConfigMap | Stable |
| `ENVIRONMENT` | Environment flag | ConfigMap | Stable |

---

## 🌐 CLOUDFLARE CDN MANAGEMENT

### Account Information
- **Account ID**: `[SECURE_VAULT_REFERENCE]`
- **Email**: `admin@013a.tech`
- **API Token**: `[SECURE_VAULT_REFERENCE]`
- **Zone ID (013a.tech)**: `[SECURE_VAULT_REFERENCE]`

### DNS Configuration
| Record | Type | Name | Content | Proxy |
|--------|------|------|---------|-------|
| Primary | A | 013a.tech | `34.118.226.10` | ✅ Proxied |
| WWW | CNAME | www.013a.tech | `013a.tech` | ✅ Proxied |
| API | A | api.013a.tech | `34.118.226.10` | ✅ Proxied |

### SSL/TLS Configuration
- **SSL Mode**: Full (strict)
- **Certificate**: Universal SSL (Auto-renewal)
- **TLS Version**: 1.3 minimum
- **HSTS**: Enabled (max-age: 31536000)
- **Certificate Transparency**: Enabled

### Cloudflare API Access
```bash
# Update DNS record
curl -X PUT "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{RECORD_ID}" \
  -H "Authorization: Bearer {API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"013a.tech","content":"NEW_IP_ADDRESS","proxied":true}'

# Check zone status
curl -X GET "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}" \
  -H "Authorization: Bearer {API_TOKEN}" \
  -H "Content-Type: application/json"
```

---

## 🚨 EMERGENCY ACCESS PROCEDURES

### Incident Response Team
| Role | Contact | Primary | Backup | Response Time |
|------|---------|---------|---------|---------------|
| **System Admin** | admin@013a.tech | 24/7 | admin-backup@013a.tech | < 15 min |
| **Security Officer** | security@013a.tech | Business Hours | security-oncall@013a.tech | < 30 min |
| **DevOps Lead** | devops@013a.tech | 24/7 | devops-backup@013a.tech | < 15 min |

### Emergency Procedures

#### Service Outage (P1 Incident)
1. **Immediate Response** (0-5 minutes)
   ```bash
   # Check system status
   kubectl get pods --all-namespaces | grep -E "aia|013a"

   # Check ingress status
   kubectl get ingress --all-namespaces

   # Check external connectivity
   curl -I https://013a.tech
   ```

2. **Assessment** (5-15 minutes)
   ```bash
   # Check logs
   kubectl logs -f deployment/aia-backend-simple -n aia-production

   # Check events
   kubectl get events --all-namespaces --sort-by=.metadata.creationTimestamp
   ```

3. **Escalation** (15+ minutes)
   - Page on-call engineer
   - Create incident in monitoring system
   - Activate backup systems if needed

#### Security Incident (P0 Incident)
1. **Immediate Actions**
   - Disable compromised accounts
   - Rotate all affected credentials
   - Enable enhanced logging
   - Notify security team

2. **Investigation**
   - Preserve evidence
   - Analyze access logs
   - Identify impact scope
   - Document timeline

3. **Recovery**
   - Implement security patches
   - Restore from clean backups
   - Verify system integrity
   - Update security measures

---

## 🔄 CREDENTIAL ROTATION SCHEDULE

### Automated Rotation (Recommended)
| Credential Type | Rotation Frequency | Automation Status | Next Due |
|----------------|-------------------|-------------------|----------|
| JWT Secrets | 30 days | ✅ Automated | Oct 15, 2025 |
| Database Passwords | 90 days | ⚠️ Manual | Dec 1, 2025 |
| API Keys | 60 days | ✅ Automated | Nov 15, 2025 |
| SSL Certificates | 90 days | ✅ Auto-renewal | Jan 1, 2026 |

### Manual Rotation Procedures

#### Database Password Rotation
```bash
# 1. Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update database user
kubectl exec -it aia-postgres-0 -n aia-production -- \
  psql -U aia_user -d aia_production -c "ALTER USER aia_user PASSWORD '$NEW_PASSWORD';"

# 3. Update Kubernetes secret
kubectl create secret generic aia-secrets \
  --from-literal=DATABASE_PASSWORD="$NEW_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# 4. Restart applications
kubectl rollout restart deployment/aia-backend-simple -n aia-production
```

#### Service Account Key Rotation
```bash
# 1. Create new service account key
gcloud iam service-accounts keys create new-key.json \
  --iam-account=aia-admin@aia-system-prod-1759055445.iam.gserviceaccount.com

# 2. Test new key
gcloud auth activate-service-account --key-file=new-key.json
gcloud projects describe aia-system-prod-1759055445

# 3. Update systems to use new key
# 4. Delete old key after verification
gcloud iam service-accounts keys delete OLD_KEY_ID \
  --iam-account=aia-admin@aia-system-prod-1759055445.iam.gserviceaccount.com
```

---

## 📝 ACCESS AUDIT LOG

### Access Monitoring
```bash
# View kubectl access logs
kubectl logs -n kube-system deployment/kube-apiserver | grep -E "admin|aia-admin"

# View GCP audit logs
gcloud logging read 'protoPayload.authenticationInfo.principalEmail="aia-admin@aia-system-prod-1759055445.iam.gserviceaccount.com"' \
  --limit=50 --format=json
```

### Regular Audit Checklist

#### Weekly Audit (Every Monday)
- [ ] Review access logs for anomalies
- [ ] Check service health status
- [ ] Verify backup integrity
- [ ] Review security alerts
- [ ] Update access documentation

#### Monthly Audit (First Monday)
- [ ] Review user permissions
- [ ] Audit service account usage
- [ ] Check certificate expiration dates
- [ ] Review and update security policies
- [ ] Test disaster recovery procedures

#### Quarterly Audit (First Monday of Quarter)
- [ ] Full security assessment
- [ ] Penetration testing
- [ ] Access control review
- [ ] Incident response drill
- [ ] Documentation update

---

## 📞 SUPPORT AND ESCALATION

### Internal Support
- **Level 1**: DevOps team (monitoring, routine maintenance)
- **Level 2**: System administrators (complex issues, configuration)
- **Level 3**: Security team (security incidents, compliance)

### External Support
- **Google Cloud Support**: Enterprise support plan active
- **Cloudflare Support**: Business plan support
- **Third-party Security**: 24/7 SOC monitoring service

### Contact Information
```
Emergency Hotline: +1-XXX-XXX-XXXX
System Status Page: https://status.013a.tech
Internal Chat: #aia-production-alerts
Email: admin@013a.tech
```

---

## ⚖️ COMPLIANCE AND SECURITY

### Security Standards
- **SOC 2 Type II**: Compliance maintained
- **ISO 27001**: Information security management
- **GDPR**: Data protection compliance
- **OWASP**: Application security standards

### Regular Security Practices
- Monthly vulnerability scans
- Quarterly penetration testing
- Annual security audits
- Continuous compliance monitoring
- Security awareness training

---

**Document Control:**
- Created: October 3, 2025
- Last Modified: October 3, 2025
- Next Review: November 3, 2025
- Owner: System Administration Team
- Approver: Chief Technology Officer

**⚠️ CONFIDENTIALITY NOTICE:**
This document contains confidential and proprietary information. Distribution is restricted to authorized personnel only. Unauthorized access, use, or disclosure is prohibited and may result in legal action.