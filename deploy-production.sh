#!/bin/bash

# AIA Enterprise Platform - Production Deployment Script
# Complete system deployment to Google Cloud Platform
set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

# Project Configuration
export GCP_PROJECT_ID="aia-475022"
export GCP_REGION="us-central1"
export GCP_ZONE="us-central1-a"
export CLUSTER_NAME="aia-production-cluster"

# Domain Configuration
export PRIMARY_DOMAIN="aia.013a.tech"
export API_DOMAIN="api.013a.tech"
export ENTERPRISE_DOMAIN="enterprise.013a.tech"

# Cloudflare Configuration
export ZONE_ID="47bb98a473fc1c1c3c0fcb67135a2988"
export CLOUDFLARE_API_TOKEN="xV56DpeGA3ixpfhPhojMUQ9u3r6ZlcRlZkY4aNtB"

# Container Registry
export CONTAINER_REGISTRY="gcr.io/${GCP_PROJECT_ID}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check required tools
    local required_tools=("gcloud" "kubectl" "docker" "curl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed. Please install it and try again."
            exit 1
        fi
    done

    # Check GCP authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "No active GCP authentication found. Please run 'gcloud auth login'"
        exit 1
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi

    log_success "All prerequisites met"
}

configure_gcp_project() {
    log_info "Configuring GCP project..."

    # Set project
    gcloud config set project "${GCP_PROJECT_ID}"

    # Enable required APIs
    local required_apis=(
        "container.googleapis.com"
        "containerregistry.googleapis.com"
        "cloudbuild.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "compute.googleapis.com"
        "dns.googleapis.com"
        "storage-api.googleapis.com"
        "cloudsql.googleapis.com"
        "redis.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
    )

    for api in "${required_apis[@]}"; do
        log_info "Enabling API: $api"
        gcloud services enable "$api"
    done

    log_success "GCP project configured"
}

create_gke_cluster() {
    log_info "Creating GKE cluster..."

    # Check if cluster exists
    if gcloud container clusters describe "${CLUSTER_NAME}" --zone="${GCP_ZONE}" &> /dev/null; then
        log_warning "Cluster ${CLUSTER_NAME} already exists"
        return 0
    fi

    # Create cluster
    gcloud container clusters create "${CLUSTER_NAME}" \
        --zone="${GCP_ZONE}" \
        --machine-type="e2-standard-4" \
        --num-nodes=3 \
        --min-nodes=1 \
        --max-nodes=10 \
        --enable-autoscaling \
        --enable-autorepair \
        --enable-autoupgrade \
        --disk-type="pd-ssd" \
        --disk-size="100GB" \
        --enable-network-policy \
        --enable-ip-alias \
        --scopes="https://www.googleapis.com/auth/cloud-platform" \
        --addons=HorizontalPodAutoscaling,HttpLoadBalancing,NetworkPolicy \
        --enable-shielded-nodes

    # Get cluster credentials
    gcloud container clusters get-credentials "${CLUSTER_NAME}" --zone="${GCP_ZONE}"

    log_success "GKE cluster created and configured"
}

build_and_push_images() {
    log_info "Building and pushing container images..."

    # List of services to build
    local services=(
        "infrastructure:docker-compose.infrastructure.yml"
        "backend:docker-compose.backend.yml"
        "backend-extended:docker-compose.backend-extended.yml"
        "frontend:docker-compose.frontend.yml"
        "agents:docker-compose.agents.yml"
        "atomic-dkg:docker-compose.atomic-dkg.yml"
        "fortune500:docker-compose.fortune500.yml"
    )

    # Configure Docker for GCR
    gcloud auth configure-docker

    # Build and push each service group
    for service_group in "${services[@]}"; do
        local name="${service_group%%:*}"
        local compose_file="${service_group##*:}"

        log_info "Building and pushing $name services..."

        # Build images
        docker-compose -f "$compose_file" build

        # Tag and push images
        local image_names
        image_names=$(docker-compose -f "$compose_file" config --services)

        while IFS= read -r service; do
            if [[ -n "$service" ]]; then
                local image="aia-system/${service}:latest"
                local gcr_image="${CONTAINER_REGISTRY}/${service}:latest"

                if docker image inspect "$image" &> /dev/null; then
                    log_info "Pushing $image to GCR..."
                    docker tag "$image" "$gcr_image"
                    docker push "$gcr_image"
                fi
            fi
        done <<< "$image_names"
    done

    log_success "All images built and pushed to GCR"
}

deploy_infrastructure() {
    log_info "Deploying infrastructure components..."

    # Create namespaces
    kubectl create namespace aia-infrastructure --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace aia-backend --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace aia-frontend --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace aia-agents --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace aia-atomic-dkg --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace aia-fortune500 --dry-run=client -o yaml | kubectl apply -f -

    # Deploy infrastructure
    kubectl apply -k ./k8s/infrastructure/ -n aia-infrastructure

    # Wait for infrastructure to be ready
    kubectl wait --for=condition=available --timeout=600s deployment --all -n aia-infrastructure

    log_success "Infrastructure deployed"
}

deploy_backend_services() {
    log_info "Deploying backend services..."

    # Deploy core backend services
    kubectl apply -k ./k8s/backend/ -n aia-backend

    # Wait for backend services to be ready
    kubectl wait --for=condition=available --timeout=600s deployment --all -n aia-backend

    log_success "Backend services deployed"
}

deploy_frontend_applications() {
    log_info "Deploying frontend applications..."

    # Deploy frontend services
    kubectl apply -k ./k8s/frontend/ -n aia-frontend

    # Wait for frontend services to be ready
    kubectl wait --for=condition=available --timeout=300s deployment --all -n aia-frontend

    log_success "Frontend applications deployed"
}

deploy_multi_agent_system() {
    log_info "Deploying multi-agent system..."

    # Deploy agent services
    kubectl apply -k ./k8s/agents/ -n aia-agents

    # Wait for agent services to be ready
    kubectl wait --for=condition=available --timeout=300s deployment --all -n aia-agents

    log_success "Multi-agent system deployed"
}

deploy_atomic_dkg() {
    log_info "Deploying Atomic-DKG system..."

    # Deploy DKG services
    kubectl apply -k ./k8s/atomic-dkg/ -n aia-atomic-dkg

    # Wait for DKG services to be ready
    kubectl wait --for=condition=available --timeout=600s deployment --all -n aia-atomic-dkg

    log_success "Atomic-DKG system deployed"
}

deploy_fortune500_integrations() {
    log_info "Deploying Fortune 500 integrations..."

    # Deploy integration services
    kubectl apply -k ./k8s/fortune500/ -n aia-fortune500

    # Wait for integration services to be ready
    kubectl wait --for=condition=available --timeout=300s deployment --all -n aia-fortune500

    log_success "Fortune 500 integrations deployed"
}

configure_load_balancers() {
    log_info "Configuring load balancers..."

    # Deploy ingress controllers
    kubectl apply -f ./k8s/ingress/nginx-ingress.yaml
    kubectl apply -f ./k8s/ingress/aia-ingress.yaml

    # Wait for load balancer IP
    log_info "Waiting for load balancer IP assignment..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        local lb_ip
        lb_ip=$(kubectl get service nginx-ingress-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

        if [[ -n "$lb_ip" ]]; then
            log_success "Load balancer IP assigned: $lb_ip"
            export LOAD_BALANCER_IP="$lb_ip"
            break
        fi

        log_info "Attempt $attempt/$max_attempts: Waiting for load balancer IP..."
        sleep 10
        ((attempt++))
    done

    if [[ -z "${LOAD_BALANCER_IP:-}" ]]; then
        log_error "Failed to get load balancer IP after $max_attempts attempts"
        exit 1
    fi

    log_success "Load balancers configured"
}

configure_dns() {
    log_info "Configuring DNS records..."

    if [[ -z "${LOAD_BALANCER_IP:-}" ]]; then
        log_error "Load balancer IP not set. Cannot configure DNS."
        exit 1
    fi

    # Configure DNS records via Cloudflare API
    local domains=("$PRIMARY_DOMAIN" "$API_DOMAIN" "$ENTERPRISE_DOMAIN")

    for domain in "${domains[@]}"; do
        log_info "Configuring DNS for $domain..."

        # Create or update A record
        curl -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
            -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
            -H "Content-Type: application/json" \
            --data "{\"type\":\"A\",\"name\":\"$domain\",\"content\":\"${LOAD_BALANCER_IP}\",\"proxied\":true}" \
            --silent
    done

    log_success "DNS records configured"
}

configure_ssl() {
    log_info "Configuring SSL certificates..."

    # Install cert-manager
    kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.13.0/cert-manager.yaml

    # Wait for cert-manager to be ready
    kubectl wait --for=condition=available --timeout=300s deployment --all -n cert-manager

    # Apply certificate issuer
    kubectl apply -f ./k8s/ssl/cluster-issuer.yaml

    # Apply certificates
    kubectl apply -f ./k8s/ssl/certificates.yaml

    log_success "SSL certificates configured"
}

run_health_checks() {
    log_info "Running comprehensive health checks..."

    # Check all namespaces
    local namespaces=("aia-infrastructure" "aia-backend" "aia-frontend" "aia-agents" "aia-atomic-dkg" "aia-fortune500")

    for ns in "${namespaces[@]}"; do
        log_info "Checking health in namespace: $ns"

        # Check deployments
        local unhealthy_deployments
        unhealthy_deployments=$(kubectl get deployments -n "$ns" --no-headers | awk '$2 != $4 {print $1}' || true)

        if [[ -n "$unhealthy_deployments" ]]; then
            log_warning "Unhealthy deployments in $ns: $unhealthy_deployments"
        else
            log_success "All deployments healthy in $ns"
        fi

        # Check pods
        local failing_pods
        failing_pods=$(kubectl get pods -n "$ns" --field-selector=status.phase!=Running --no-headers | awk '{print $1}' || true)

        if [[ -n "$failing_pods" ]]; then
            log_warning "Non-running pods in $ns: $failing_pods"
        else
            log_success "All pods running in $ns"
        fi
    done

    # Test endpoints
    local endpoints=(
        "https://${PRIMARY_DOMAIN}/health"
        "https://${API_DOMAIN}/health"
        "https://${ENTERPRISE_DOMAIN}/health"
    )

    for endpoint in "${endpoints[@]}"; do
        log_info "Testing endpoint: $endpoint"

        if curl -f -s "$endpoint" > /dev/null; then
            log_success "Endpoint $endpoint is healthy"
        else
            log_warning "Endpoint $endpoint is not responding"
        fi
    done

    log_success "Health checks completed"
}

generate_deployment_report() {
    log_info "Generating deployment report..."

    local report_file="deployment-report-$(date +%Y%m%d-%H%M%S).md"

    cat > "$report_file" << EOF
# AIA Enterprise Platform - Deployment Report

**Deployment Date**: $(date)
**GCP Project**: ${GCP_PROJECT_ID}
**Cluster**: ${CLUSTER_NAME}
**Load Balancer IP**: ${LOAD_BALANCER_IP:-Not assigned}

## Domains
- Primary: https://${PRIMARY_DOMAIN}
- API: https://${API_DOMAIN}
- Enterprise: https://${ENTERPRISE_DOMAIN}

## Service Status
EOF

    # Add service status to report
    local namespaces=("aia-infrastructure" "aia-backend" "aia-frontend" "aia-agents" "aia-atomic-dkg" "aia-fortune500")

    for ns in "${namespaces[@]}"; do
        echo "" >> "$report_file"
        echo "### Namespace: $ns" >> "$report_file"
        kubectl get deployments -n "$ns" -o custom-columns=NAME:.metadata.name,READY:.status.readyReplicas,AVAILABLE:.status.availableReplicas --no-headers >> "$report_file" 2>/dev/null || echo "No deployments found" >> "$report_file"
    done

    echo "" >> "$report_file"
    echo "## Next Steps" >> "$report_file"
    echo "1. Verify all services are responding correctly" >> "$report_file"
    echo "2. Configure monitoring and alerting" >> "$report_file"
    echo "3. Set up backup procedures" >> "$report_file"
    echo "4. Configure CI/CD pipelines" >> "$report_file"
    echo "5. Perform load testing" >> "$report_file"

    log_success "Deployment report generated: $report_file"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    log_info "Starting AIA Enterprise Platform production deployment..."

    # Phase 1: Prerequisites and Setup
    check_prerequisites
    configure_gcp_project

    # Phase 2: Infrastructure
    create_gke_cluster
    build_and_push_images

    # Phase 3: Core Deployment
    deploy_infrastructure
    deploy_backend_services
    deploy_frontend_applications

    # Phase 4: Advanced Components
    deploy_multi_agent_system
    deploy_atomic_dkg
    deploy_fortune500_integrations

    # Phase 5: Networking and Security
    configure_load_balancers
    configure_dns
    configure_ssl

    # Phase 6: Verification
    run_health_checks
    generate_deployment_report

    log_success "🎉 AIA Enterprise Platform deployment completed successfully!"
    log_info "Access your platform at:"
    log_info "  Primary: https://${PRIMARY_DOMAIN}"
    log_info "  API: https://${API_DOMAIN}"
    log_info "  Enterprise: https://${ENTERPRISE_DOMAIN}"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi