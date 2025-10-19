# AIA-Only Implementation Guide

## Quick Start

This guide shows how to implement the comprehensive AIA-only deployment strategy that ensures only your repository's AIA system is deployed to GCP, with automatic cleanup of all non-AIA resources.

## 🎯 What This Solves

✅ **Eliminates "latest" tag problems** - Uses semantic versioning only  
✅ **Ensures AIA-only deployments** - Removes all non-repository systems  
✅ **Prevents version drift** - Immutable tagging prevents overwrites  
✅ **Enforces repository code sync** - All AIA services run current repository code  
✅ **Detects outdated deployments** - Automatically identifies services with old code  
✅ **Automates cleanup** - Removes orphaned resources and unauthorized namespaces  
✅ **Provides safe rollbacks** - Version history with automated rollback  
✅ **Enforces consistency** - Only repository-defined resources with current code exist  

## 📁 Files Created

| File | Purpose |
|------|---------|
| `EFFICIENT_DEPLOYMENT_STRATEGY.md` | Complete strategy documentation |
| `scripts/version-manager.sh` | Core version management and cleanup tool |
| `cloudbuild-aia-only.yaml` | Cloud Build config without "latest" tags |
| `deploy-aia-only.sh` | Main deployment script |

## 🚀 Implementation Steps

### Step 1: Make Scripts Executable

```bash
cd /Users/wXy/dev/Projects/aia
chmod +x scripts/version-manager.sh
chmod +x deploy-aia-only.sh
```

### Step 2: Audit Current Environment

```bash
# See what non-AIA resources exist
./scripts/version-manager.sh audit

# Get detailed deployment status
./scripts/version-manager.sh status
```

### Step 3: Clean Up Non-AIA Resources (Optional)

```bash
# Conservative cleanup (AIA resources only)
./scripts/version-manager.sh cleanup

# OR: Comprehensive cleanup (removes ALL non-AIA resources)
./scripts/version-manager.sh full-cleanup
```

### Step 4: Deploy with New Strategy

```bash
# Deploy current version with AIA-only enforcement
./deploy-aia-only.sh deploy

# OR: Deploy specific version
./deploy-aia-only.sh deploy v1.2.3
```

## 🔧 Daily Operations

### Deploy New Version

```bash
# Option 1: Use the deployment script (recommended)
./deploy-aia-only.sh deploy

# Option 2: Use Cloud Build directly
gcloud builds submit --config cloudbuild-aia-only.yaml

# Option 3: Use version manager for manual control
./scripts/version-manager.sh build
./scripts/version-manager.sh deploy
```

### Check Deployment Status

```bash
# Show all deployed versions (detects version drift)
./scripts/version-manager.sh status

# Check if AIA services are running current repository code
./scripts/version-manager.sh check-drift

# Audit for any non-AIA resources
./scripts/version-manager.sh audit
```

### Sync Repository Code

```bash
# Force all AIA services to run current repository code
./deploy-aia-only.sh sync-repo

# OR: Using version manager directly
./scripts/version-manager.sh sync-repo-code

# Check for version drift first
./scripts/version-manager.sh check-drift
```

### Emergency Rollback

```bash
# Rollback using deployment script
./deploy-aia-only.sh rollback

# OR: Rollback using version manager
./scripts/version-manager.sh rollback
```

### Periodic Cleanup

```bash
# Clean up old AIA resources (keeps last 10 versions)
./scripts/version-manager.sh cleanup

# Aggressively clean old AIA versions (keep only 3 most recent)
./scripts/version-manager.sh cleanup-old-versions 3

# Remove any new non-AIA resources
./scripts/version-manager.sh cleanup-namespaces
./scripts/version-manager.sh cleanup-images

# Ensure all AIA services are current
./scripts/version-manager.sh sync-repo-code
```

## 🛡️ Safety Features

### 1. Interactive Confirmations
All destructive operations require confirmation unless `--force` is used:

```bash
# Safe (asks for confirmation)
./scripts/version-manager.sh full-cleanup

# Automated (skips confirmation)
FORCE_CLEANUP=true ./scripts/version-manager.sh full-cleanup
```

### 2. Protected Namespaces
System namespaces are automatically protected:
- `kube-system`
- `kube-public`
- `gke-system`
- `default`

### 3. Immutable Tags
- Images with existing tags cannot be overwritten
- Prevents accidental overwrites
- Ensures deployment consistency

### 4. Version Validation
- Enforces semantic versioning format
- Validates before build/deploy
- Prevents invalid deployments

## 📊 Version Management

### Automatic Version Detection

The system automatically creates semantic versions:

```bash
# On a git tag (production release)
git tag v1.2.3
git push origin v1.2.3
# Results in: v1.2.3

# On development commit (not tagged)
# Results in: v1.2.2-dev.5.abc1234
```

### Manual Version Override

```bash
# Deploy specific version
./deploy-aia-only.sh deploy v1.2.3

# Build specific version
./scripts/version-manager.sh build v1.2.3
```

### Version Format

```
v{MAJOR}.{MINOR}.{PATCH}[-{PRERELEASE}][+{BUILD}]

Examples:
v1.2.3                    # Production release
v1.2.3-rc.1               # Release candidate  
v1.2.3-dev.5.abc1234      # Development build
```

## 🔍 Monitoring and Troubleshooting

### Check Image Registry

```bash
# List all AIA images
gcloud container images list --repository="gcr.io/$PROJECT_ID" | grep aia

# List versions for specific service
gcloud container images list-tags "gcr.io/$PROJECT_ID/aia-api"
```

### Check Kubernetes Resources

```bash
# List all namespaces
kubectl get namespaces

# Check deployments in AIA namespace
kubectl get deployments -n aia-production

# Check running pods
kubectl get pods -n aia-production -o wide
```

### View Deployment History

```bash
# Kubernetes rollout history
kubectl rollout history deployment/aia-api -n aia-production

# Check deployment labels
kubectl get deployment aia-api -n aia-production -o yaml | grep -A 5 labels
```

## 🚨 Emergency Procedures

### Complete System Recovery

```bash
# 1. Audit current state
./scripts/version-manager.sh audit

# 2. Full cleanup (removes ALL non-AIA resources)
./deploy-aia-only.sh full-cleanup --force

# 3. Deploy latest version
./deploy-aia-only.sh deploy

# 4. Verify deployment
./scripts/version-manager.sh status
```

### Rollback to Specific Version

```bash
# Find available versions
gcloud container images list-tags "gcr.io/$PROJECT_ID/aia-api"

# Deploy specific version
./scripts/version-manager.sh deploy v1.2.1
```

### Handle Stuck Deployments

```bash
# Check deployment status
kubectl get deployments -n aia-production

# Force restart deployment
kubectl rollout restart deployment/aia-api -n aia-production

# Check pod logs
kubectl logs -l app=aia-api -n aia-production --tail=100
```

## 📋 Configuration Reference

### Environment Variables

```bash
# Core configuration
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export CLUSTER="aia-production-cluster"

# Cleanup behavior
export FORCE_CLEANUP="false"          # Skip confirmations
export MAX_VERSIONS_TO_KEEP="10"      # Image retention
export MAX_AGE_DAYS="90"              # Maximum image age
```

### Allowed Namespaces

The system protects these namespaces from deletion:

```yaml
allowed_namespaces:
  - aia-production      # AIA production environment
  - aia-staging         # AIA staging environment  
  - aia-monitoring      # AIA monitoring stack
  - kube-system         # Kubernetes system (protected)
  - kube-public         # Kubernetes public (protected)
  - gke-system          # GKE system (protected)
  - default             # Default namespace (often has system resources)
```

### AIA Services

The system recognizes these as AIA services:

```yaml
aia_services:
  - api                 # Main API service
  - frontend            # Frontend application
  - orchestrator        # Orchestration service
  - economic            # Economic management
  - database            # Database service
  - redis               # Redis cache
  - monitoring          # Monitoring stack
```

## 🎯 Advanced Usage

### Custom Cloud Build Triggers

```bash
# Create trigger for main branch
gcloud builds triggers create github \
  --repo-name="aia" \
  --repo-owner="your-org" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild-aia-only.yaml" \
  --substitutions="_PROJECT_ID=$PROJECT_ID"
```

### Automated Cleanup Schedule

```bash
# Create cron job for daily cleanup
cat << 'EOF' > cleanup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: aia-cleanup
  namespace: aia-production
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: google/cloud-sdk:latest
            command:
            - /bin/bash
            - -c
            - |
              # Add cleanup commands here
              echo "Running scheduled cleanup..."
          restartPolicy: OnFailure
EOF

kubectl apply -f cleanup-cronjob.yaml
```

### Integration with CI/CD

```yaml
# GitHub Actions example
name: AIA Deployment
on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Google Cloud
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.PROJECT_ID }}
    
    - name: Deploy AIA System
      run: |
        chmod +x deploy-aia-only.sh
        ./deploy-aia-only.sh deploy --force
```

## ✅ Verification Checklist

After implementation, verify:

- [ ] No images tagged with "latest"
- [ ] All images use semantic versions
- [ ] Only allowed namespaces exist
- [ ] All deployments have version labels
- [ ] Health checks pass
- [ ] Rollback functionality works
- [ ] Cleanup removes non-AIA resources
- [ ] Version manager commands work
- [ ] Cloud Build uses new configuration

## 🔗 Related Resources

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Semantic Versioning](https://semver.org/)
- [Container Registry Documentation](https://cloud.google.com/container-registry/docs)

---

**Result**: Your GCP environment will contain ONLY the AIA system from your repository, with all services running the current repository code, proper versioning, automated cleanup, and safe rollback capabilities. No old versions, no non-AIA systems, only fresh repository code.
