# AIA v3.0 GitHub CI/CD Deployment Checklist

## ✅ Pre-Deployment Validation

### 1. GitHub Repository Setup
- [x] Repository: Uses existing GitHub repo with CI/CD
- [x] Branch: Working on `main` branch
- [x] Secrets: GCP service account key configured
- [x] Workflow: `deploy-production.yml` exists and functional

### 2. Code Readiness Check
```bash
# Test local imports work
cd aia && python -c "
try:
    from main import app
    from economic.tokens.aia_token import AIA
    from dkg.enhanced.dkg_manager import DKGManager
    print('✅ Core imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test structured system
python test_structured_system.py

# Validate API starts
cd aia && python -m uvicorn main:app --reload &
sleep 5 && curl -f http://localhost:8000/health
kill %1
```

### 3. Docker Configuration
```dockerfile
# Verify aia/Dockerfile.production exists and is correct
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY aia/ ./aia/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "aia.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🚀 Deployment Process

### Step 1: Prepare Release Branch
```bash
# Create release branch
git checkout -b release/v3.0.0

# Final validation
python test_structured_system.py
pytest aia/tests/ -v

# Commit any final fixes
git add .
git commit -m "feat: AIA System v3.0 production release"
git push origin release/v3.0.0
```

### Step 2: Create Pull Request
```bash
# Create PR to main branch
# GitHub UI: Create Pull Request from release/v3.0.0 to main
# This triggers CI tests without deployment
```

### Step 3: Production Deployment
```bash
# Option A: Merge to main (automatic deployment)
git checkout main
git merge release/v3.0.0
git push origin main
# ↑ This triggers deploy-production.yml automatically

# Option B: Manual deployment (recommended)
# Go to GitHub Actions → Deploy to Production (GCP) → Run workflow
# Select: environment: production
```

### Step 4: Monitor Deployment
```bash
# GitHub Actions will show:
# 1. Tests running
# 2. Docker build progress  
# 3. GKE deployment status
# 4. Health checks
# 5. Success/failure notifications
```

## 📊 GitHub Actions Pipeline Steps

### Current Pipeline Analysis:
```yaml
Jobs in deploy-production.yml:
1. test: 
   - Python 3.11 setup ✅
   - Install dependencies ✅
   - Run linting ✅
   - Run tests ✅
   - Upload coverage ✅

2. build:
   - Docker buildx setup ✅
   - GCP authentication ✅
   - Build & push to Artifact Registry ✅
   - Multi-arch support ✅

3. deploy:
   - GKE credentials ✅
   - Create namespace ✅
   - Update secrets ✅  
   - Deploy application ✅
   - Wait for rollout ✅
   - Run smoke tests ✅

4. monitor:
   - Health checks ✅
   - Metrics validation ✅
   - Slack notifications ✅
```

## 🔍 Deployment Monitoring

### GitHub Actions Dashboard
```bash
# Monitor at: https://github.com/{repo}/actions
# Real-time logs for:
- Test execution
- Docker build progress
- GKE deployment status
- Health check results
```

### GCP Console Monitoring  
```bash
# Monitor at: https://console.cloud.google.com
# Project: a-467519
# Cluster: aia-cluster
# Namespace: aia-system
```

### Application Health
```bash
# Once deployed, verify:
curl -f https://013a.tech/health
curl -f https://013a.tech/docs
curl -f https://013a.tech/
```

## 🚨 Rollback Strategy

### Automatic Rollback
```yaml
# GitHub Actions will auto-rollback if:
- Health checks fail
- Smoke tests fail  
- Deployment timeout (600s)
```

### Manual Rollback
```bash
# Via GitHub Actions:
# 1. Go to Actions → Deploy to Production
# 2. Select "Re-run failed jobs" on previous successful deployment

# Via kubectl (emergency):
kubectl rollout undo deployment/aia-api -n aia-system
```

## 📈 Success Criteria

### Deployment Success Indicators:
- ✅ All GitHub Actions jobs pass (green checkmarks)
- ✅ Health endpoint returns 200: https://013a.tech/health  
- ✅ API documentation accessible: https://013a.tech/docs
- ✅ Core features functional (tokens, DKG, reports, etc.)
- ✅ Response time <500ms
- ✅ Error rate <1%

### Business Success Indicators:
- ✅ All AIA v3.0 features operational
- ✅ Token economics active
- ✅ Agent hierarchy functional  
- ✅ Venture discovery working
- ✅ Performance management active

## ⏱️ Expected Timeline

```
Preparation: 30 minutes
├── Final code validation
├── Create release branch  
├── Run local tests

Deployment: 15-20 minutes  
├── GitHub Actions execution
├── Docker build: ~5 min
├── GKE deployment: ~10 min
├── Health checks: ~5 min

Validation: 10 minutes
├── Smoke tests
├── Feature validation
├── Performance check
```

**Total Time**: ~60 minutes from commit to fully operational

## 🎯 Next Steps

1. **Validate current state** ✅
2. **Fix any import issues** (if needed)
3. **Create release branch**
4. **Trigger GitHub Actions deployment** 
5. **Monitor deployment progress**
6. **Validate production functionality**
7. **Celebrate successful deployment** 🎉