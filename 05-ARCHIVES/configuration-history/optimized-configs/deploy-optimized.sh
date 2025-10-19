#!/bin/bash
set -e

# AIA System Optimized Deployment Script
# =====================================

NAMESPACE="aia-system"
CLUSTER_NAME="aia-production-cluster"
REGION="us-central1"
PROJECT_ID="a-467519"

echo "🚀 Starting AIA System Deployment..."

# Authenticate with GCP
echo "🔑 Authenticating with Google Cloud..."
gcloud auth configure-docker --quiet

# Get cluster credentials
echo "🔧 Configuring kubectl..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets
echo "🔐 Applying secrets..."
kubectl apply -f k8s-deployments/aia-secrets.yaml -n $NAMESPACE

# Deploy database and Redis
echo "📊 Deploying database and Redis..."
kubectl apply -f k8s-deployments/aia-postgres.yaml -n $NAMESPACE
kubectl apply -f k8s-deployments/aia-redis.yaml -n $NAMESPACE

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/aia-postgres -n $NAMESPACE

# Deploy core services
echo "🏗️ Deploying core services..."
kubectl apply -f k8s-deployments/aia-optimized-api-deployment.yaml -n $NAMESPACE
kubectl apply -f k8s-deployments/aia-optimized-frontend-deployment.yaml -n $NAMESPACE

# Deploy multi-agent system
echo "🤖 Deploying multi-agent orchestrator..."
kubectl apply -f k8s-deployments/aia-mas-deployment.yaml -n $NAMESPACE

# Deploy monitoring
echo "📈 Deploying monitoring stack..."
kubectl apply -f k8s-deployments/aia-monitoring.yaml -n aia-monitoring

# Apply ingress
echo "🌐 Configuring ingress..."
kubectl apply -f k8s-deployments/aia-optimized-ingress.yaml -n $NAMESPACE

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/aia-comprehensive-api -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/aia-comprehensive-frontend -n $NAMESPACE

# Health check
echo "🏥 Performing health checks..."
API_URL=$(kubectl get ingress aia-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -f http://$API_URL/health || exit 1

echo "✅ AIA System deployed successfully!"
echo "🌐 Frontend: https://013a.tech"
echo "🔧 API: http://$API_URL"
echo "📊 Monitoring: https://monitoring.013a.tech"

# Optional: Run integration tests
if [[ "$RUN_TESTS" == "true" ]]; then
    echo "🧪 Running integration tests..."
    python3 comprehensive_integration_test.py
fi

echo "🎉 Deployment completed successfully!"
