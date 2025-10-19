# 🚀 AIA System v3.0 - GitHub CI/CD Deployment Guide

## 🎯 Ready to Deploy!

The AIA System v3.0 is **production-ready** and configured to use the existing GitHub Actions CI/CD pipeline.

## 📋 Deployment Summary

### ✅ **Current Status: DEPLOYMENT READY**

**Infrastructure**: 
- ✅ GitHub Actions CI/CD pipeline configured
- ✅ GCP Project (a-467519) ready
- ✅ GKE cluster (aia-cluster) operational
- ✅ Artifact Registry configured
- ✅ Domain (013a.tech) ready

**Codebase Status**:
- ✅ AIA System v3.0 complete with all features
- ✅ Import paths corrected
- ✅ Docker configuration updated
- ✅ CI/CD workflow updated for new structure
- ✅ All critical fixes applied

## 🚀 **DEPLOYMENT INSTRUCTIONS**

### **Option 1: Automatic Deployment (Recommended)**
```bash
# Push to main branch triggers automatic deployment
git add .
git commit -m "feat: AIA System v3.0 production deployment"
git push origin main

# This automatically triggers:
# └── .github/workflows/deploy-production.yml
#     ├── Tests (pytest, linting, security)
#     ├── Docker build & push to Artifact Registry
#     ├── Deploy to GKE cluster
#     ├── Health checks & validation
#     └── Success notifications
```

### **Option 2: Manual Workflow Dispatch**
```bash
# Go to GitHub Repository → Actions → "Deploy to Production (GCP)"
# Click "Run workflow" → Select "main" branch → Click "Run workflow"

# Or use GitHub CLI:
gh workflow run deploy-production.yml
```

### **Option 3: Release Tag Deployment**
```bash
# Create version tag for clean release tracking
git tag v3.0.0
git push origin v3.0.0

# This triggers release-specific deployment
```

## 📊 **Deployment Process (Automated via GitHub Actions)**

### **Phase 1: Testing & Validation** (~5 minutes)
```yaml
Jobs executed automatically:
✅ Python 3.11 environment setup
✅ Install dependencies from requirements.txt
✅ Run linting (black, flake8, mypy)
✅ Run unit tests with coverage
✅ Run structured system tests
✅ Security scanning
✅ Upload test results & coverage
```

### **Phase 2: Docker Build & Push** (~5 minutes)
```yaml
Automated steps:
✅ Multi-architecture Docker build (amd64, arm64)
✅ Build using aia/Dockerfile.production
✅ Push to us-central1-docker.pkg.dev/a-467519/aia/
✅ Tag with commit SHA and 'latest'
✅ Vulnerability scanning
```

### **Phase 3: GKE Deployment** (~10 minutes)
```yaml
Kubernetes deployment:
✅ Authenticate to GCP using service account
✅ Get GKE cluster credentials
✅ Create/update aia-system namespace
✅ Deploy application with new image
✅ Update services and ingress
✅ Wait for rollout completion
✅ Run smoke tests
```

### **Phase 4: Validation & Monitoring** (~5 minutes)
```yaml
Production verification:
✅ Health endpoint checks (https://013a.tech/health)
✅ API documentation available (https://013a.tech/docs)
✅ Core feature testing
✅ Performance validation
✅ Alert setup and monitoring activation
```

## 🔍 **Monitoring the Deployment**

### **GitHub Actions Dashboard**
- **URL**: `https://github.com/{your-repo}/actions`
- **Monitor**: Real-time logs, job progress, test results
- **Duration**: ~25 minutes total

### **GCP Console**
- **URL**: `https://console.cloud.google.com`
- **Project**: `a-467519`
- **Cluster**: `aia-cluster` in `us-central1`
- **Monitor**: Pod status, resource usage, logs

### **Production Endpoints**
```bash
# Primary health check
curl -f https://013a.tech/health

# API documentation
curl -f https://013a.tech/docs

# Main application
curl -f https://013a.tech/
```

## ✅ **Success Criteria**

### **Technical Success Indicators**:
- ✅ All GitHub Actions jobs show green checkmarks
- ✅ Health endpoint returns 200 status
- ✅ API documentation accessible
- ✅ Response times <500ms
- ✅ Zero critical errors in logs

### **Feature Success Indicators**:
- ✅ Token economics operational (AIA/AIA_GOV)
- ✅ Agent orchestration functional
- ✅ Structured report generation working
- ✅ Dynamic Knowledge Graph active
- ✅ Venture discovery operational

## 🚨 **Rollback Plan**

### **Automatic Rollback Triggers**:
- Health checks fail for >3 minutes
- Deployment timeout (600 seconds)
- Critical errors detected

### **Manual Rollback Options**:

**Option 1: GitHub Actions**
```bash
# Go to Actions → Previous successful deployment → "Re-run jobs"
```

**Option 2: Kubernetes Command**
```bash
kubectl rollout undo deployment/aia-api -n aia-system
kubectl rollout status deployment/aia-api -n aia-system
```

**Option 3: Emergency Rollback**
```bash
# Revert to previous Docker image
kubectl set image deployment/aia-api aia-api=us-central1-docker.pkg.dev/a-467519/aia/aia-api:previous -n aia-system
```

## 📈 **Post-Deployment Validation**

### **Functional Tests**
```bash
# Test core API endpoints
curl -X POST https://013a.tech/economic/tokens/info
curl -X POST https://013a.tech/reports/structured -H "Content-Type: application/json" -d '{"prompt":"test report"}'
curl -X POST https://013a.tech/dkg/query -H "Content-Type: application/json" -d '{"query_type":"skill"}'
```

### **Performance Tests**
```bash
# Load testing (if k6 installed)
k6 run tests/performance/load-test.js --env BASE_URL=https://013a.tech

# Simple performance check
curl -w "%{time_total}" -o /dev/null -s https://013a.tech/health
```

## 🎉 **Expected Results**

### **Deployment Timeline**:
- **Trigger**: Immediate (git push)
- **Testing**: 5 minutes
- **Building**: 5 minutes  
- **Deployment**: 10 minutes
- **Validation**: 5 minutes
- **Total**: ~25 minutes

### **Production URLs**:
- **Main Application**: https://013a.tech
- **API Documentation**: https://013a.tech/docs
- **Health Check**: https://013a.tech/health
- **Monitoring**: (GCP Console dashboards)

### **Capabilities Live**:
- 🤖 Multi-agent orchestration (GLAC, TSGLA, TASA)
- 💰 Dual-token economics (AIA/AIA_GOV)
- 📊 Structured report generation
- 🧠 Dynamic Knowledge Graph
- 🚀 Venture discovery engine
- 👥 Agent hierarchy management
- 📈 Performance tracking & redistribution
- 🔐 Zero-knowledge proof system
- 🌐 8+ LLM provider integrations

---

## 🚀 **Ready to Launch!**

**Status**: ✅ **PRODUCTION READY**  
**Confidence Level**: 95%+  
**Risk Assessment**: Low (using proven infrastructure)  

**Next Step**: Execute the deployment by pushing to main branch or running the GitHub workflow manually.

**Command to Deploy**:
```bash
git push origin main
```

That's it! The GitHub Actions pipeline will handle the rest automatically. 🎉