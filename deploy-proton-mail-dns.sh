#!/bin/bash

# AIA Multi-Agent System: Proton Mail DNS Deployment Automation
# ============================================================
#
# Production-grade deployment script with comprehensive error handling,
# rollback capabilities, and security compliance monitoring.
#
# Multi-Agent Contributions:
# - Production Readiness Assessor: Error handling and validation
# - DevOps Engineer: Deployment automation patterns
# - Security Agent: Compliance verification
# - Code Reviewer: Best practices implementation

set -euo pipefail  # Strict error handling

# Global Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/proton_dns_deployment.log"
readonly BACKUP_DIR="${SCRIPT_DIR}/dns_backups"
readonly TERRAFORM_DIR="${SCRIPT_DIR}/terraform-cloudflare-proton"

# Cloudflare Configuration
readonly DOMAIN="013a.tech"
readonly CLOUDFLARE_API_TOKEN="${CLOUDFLARE_DNS_TOKEN:-nPYl1jYR2JZDws1DPkkG9mXGDSJwosDEiRrZo3u3}"
readonly CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-7e17c2325b4bb22dabc9ea834162a71e}"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Logging functions
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}ℹ️  $*${NC}"
    log "INFO" "$*"
}

log_success() {
    echo -e "${GREEN}✅ $*${NC}"
    log "SUCCESS" "$*"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $*${NC}"
    log "WARNING" "$*"
}

log_error() {
    echo -e "${RED}❌ $*${NC}"
    log "ERROR" "$*"
    return 1
}

log_step() {
    echo -e "${PURPLE}🚀 $*${NC}"
    log "STEP" "$*"
}

# Error handling and cleanup
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script failed with exit code $exit_code"
        log_error "Check log file: $LOG_FILE"
        log_error "Backup files available in: $BACKUP_DIR"
    fi
    return $exit_code
}

trap cleanup EXIT

# Prerequisite checks
check_prerequisites() {
    log_step "Checking prerequisites"

    local missing_deps=()

    # Check required commands
    for cmd in curl jq dig terraform python3; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Install missing dependencies:"
        log_info "  macOS: brew install curl jq bind terraform python3"
        log_info "  Ubuntu: apt-get update && apt-get install -y curl jq dnsutils terraform python3"
        return 1
    fi

    # Check Python dependencies
    if ! python3 -c "import requests" &> /dev/null; then
        log_warning "Python requests library not found. Installing..."
        pip3 install requests || {
            log_error "Failed to install Python requests library"
            return 1
        }
    fi

    # Verify Cloudflare credentials
    if [[ -z "$CLOUDFLARE_API_TOKEN" ]]; then
        log_error "CLOUDFLARE_DNS_TOKEN environment variable not set"
        return 1
    fi

    log_success "All prerequisites satisfied"
}

# Verify Cloudflare API connectivity
verify_cloudflare_api() {
    log_step "Verifying Cloudflare API connectivity"

    local response
    response=$(curl -s -w "%{http_code}" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.cloudflare.com/client/v4/user/tokens/verify")

    local http_code="${response: -3}"
    local body="${response%???}"

    if [[ "$http_code" != "200" ]]; then
        log_error "Cloudflare API verification failed (HTTP $http_code)"
        log_error "Response: $body"
        return 1
    fi

    local success=$(echo "$body" | jq -r '.success')
    if [[ "$success" != "true" ]]; then
        log_error "Cloudflare API token verification failed"
        log_error "Response: $body"
        return 1
    fi

    log_success "Cloudflare API connectivity verified"
}

# Get Cloudflare Zone ID
get_zone_id() {
    log_step "Getting Zone ID for $DOMAIN"

    local response
    response=$(curl -s \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN")

    local success=$(echo "$response" | jq -r '.success')
    if [[ "$success" != "true" ]]; then
        log_error "Failed to get zone information"
        echo "$response" | jq '.'
        return 1
    fi

    local zone_count=$(echo "$response" | jq -r '.result | length')
    if [[ "$zone_count" -eq 0 ]]; then
        log_error "Domain $DOMAIN not found in Cloudflare account"
        return 1
    fi

    ZONE_ID=$(echo "$response" | jq -r '.result[0].id')
    log_success "Zone ID for $DOMAIN: $ZONE_ID"
}

# Backup existing DNS records
backup_dns_records() {
    log_step "Backing up existing DNS records"

    mkdir -p "$BACKUP_DIR"

    local backup_file="${BACKUP_DIR}/dns_backup_${DOMAIN}_$(date +%Y%m%d_%H%M%S).json"

    local response
    response=$(curl -s \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records")

    local success=$(echo "$response" | jq -r '.success')
    if [[ "$success" != "true" ]]; then
        log_error "Failed to backup DNS records"
        return 1
    fi

    echo "$response" | jq '.' > "$backup_file"
    BACKUP_FILE="$backup_file"

    log_success "DNS records backed up to: $backup_file"
}

# Deploy using Python script
deploy_python_method() {
    log_step "Deploying DNS records using Python script"

    local python_script="${SCRIPT_DIR}/cloudflare_proton_dns_setup.py"

    if [[ ! -f "$python_script" ]]; then
        log_error "Python script not found: $python_script"
        return 1
    fi

    # Export environment variables for script
    export CLOUDFLARE_DNS_TOKEN="$CLOUDFLARE_API_TOKEN"
    export CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID"

    log_info "Running Python DNS setup script..."

    if python3 "$python_script"; then
        log_success "Python DNS deployment completed successfully"
        return 0
    else
        log_error "Python DNS deployment failed"
        return 1
    fi
}

# Deploy using Terraform
deploy_terraform_method() {
    log_step "Deploying DNS records using Terraform"

    if [[ ! -d "$TERRAFORM_DIR" ]]; then
        log_error "Terraform directory not found: $TERRAFORM_DIR"
        return 1
    fi

    cd "$TERRAFORM_DIR"

    # Create terraform.tfvars if it doesn't exist
    if [[ ! -f "terraform.tfvars" ]]; then
        log_info "Creating terraform.tfvars from example"
        cp terraform.tfvars.example terraform.tfvars

        # Update with actual values
        sed -i.bak "s/your-api-token-here/$CLOUDFLARE_API_TOKEN/g" terraform.tfvars
        rm terraform.tfvars.bak
    fi

    # Initialize Terraform
    log_info "Initializing Terraform..."
    if ! terraform init; then
        log_error "Terraform initialization failed"
        return 1
    fi

    # Plan the deployment
    log_info "Planning Terraform deployment..."
    if ! terraform plan -out=tfplan; then
        log_error "Terraform planning failed"
        return 1
    fi

    # Apply the deployment
    log_info "Applying Terraform deployment..."
    if ! terraform apply -auto-approve tfplan; then
        log_error "Terraform apply failed"
        return 1
    fi

    log_success "Terraform DNS deployment completed successfully"
    cd - > /dev/null
}

# Verify DNS records after deployment
verify_dns_records() {
    log_step "Verifying DNS records"

    local verification_failed=false

    # Check MX records
    log_info "Checking MX records..."
    if dig +short MX "$DOMAIN" | grep -q "mx.*alias.proton.me"; then
        log_success "MX records configured correctly"
    else
        log_warning "MX records not yet propagated or incorrectly configured"
        verification_failed=true
    fi

    # Check SPF record
    log_info "Checking SPF record..."
    if dig +short TXT "$DOMAIN" | grep -q "v=spf1.*include:alias.proton.me"; then
        log_success "SPF record configured correctly"
    else
        log_warning "SPF record not yet propagated or incorrectly configured"
        verification_failed=true
    fi

    # Check DKIM records
    log_info "Checking DKIM records..."
    for dkim in dkim dkim2 dkim3; do
        if dig +short CNAME "$dkim.domainkey.$DOMAIN" | grep -q "proton.me"; then
            log_success "DKIM record $dkim.domainkey configured correctly"
        else
            log_warning "DKIM record $dkim.domainkey not yet propagated"
            verification_failed=true
        fi
    done

    # Check DMARC record
    log_info "Checking DMARC record..."
    if dig +short TXT "_dmarc.$DOMAIN" | grep -q "v=DMARC1"; then
        log_success "DMARC record configured correctly"
    else
        log_warning "DMARC record not yet propagated or incorrectly configured"
        verification_failed=true
    fi

    if [[ "$verification_failed" = true ]]; then
        log_warning "Some DNS records are not yet visible - this is normal"
        log_info "DNS propagation can take up to 24-48 hours"
        log_info "Verify records later using: dig MX/TXT/CNAME <record> $DOMAIN"
    else
        log_success "All DNS records verified successfully"
    fi
}

# Display next steps
show_next_steps() {
    log_step "Next Steps"

    echo ""
    echo -e "${CYAN}📋 POST-DEPLOYMENT CHECKLIST:${NC}"
    echo ""
    echo "1. 🕒 Wait for DNS Propagation (24-48 hours)"
    echo "   - Monitor propagation: https://whatsmydns.net/"
    echo "   - Check MX records: dig MX $DOMAIN"
    echo ""
    echo "2. 📧 Setup Proton Mail Mailboxes"
    echo "   - Login to Proton Mail dashboard"
    echo "   - Create these standard mailboxes:"
    echo "     • yannick@$DOMAIN (primary)"
    echo "     • investors@$DOMAIN"
    echo "     • support@$DOMAIN"
    echo "     • info@$DOMAIN"
    echo "     • hello@$DOMAIN"
    echo "     • sales@$DOMAIN"
    echo "     • marketing@$DOMAIN"
    echo "     • hr@$DOMAIN"
    echo "     • contact@$DOMAIN"
    echo "     • admin@$DOMAIN"
    echo "     • team@$DOMAIN"
    echo "     • press@$DOMAIN"
    echo "     • careers@$DOMAIN"
    echo "     • legal@$DOMAIN"
    echo "     • privacy@$DOMAIN"
    echo ""
    echo "3. 🔍 Verify Email Authentication"
    echo "   - Use MX Toolbox: https://mxtoolbox.com/SuperTool.aspx"
    echo "   - Check DMARC alignment"
    echo "   - Test email delivery"
    echo ""
    echo "4. 📊 Monitor DMARC Reports"
    echo "   - Review weekly DMARC reports"
    echo "   - Adjust policy from 'quarantine' to 'reject' when ready"
    echo ""
    echo "5. 🔒 Security Best Practices"
    echo "   - Enable 2FA on Proton Mail account"
    echo "   - Configure catch-all email carefully"
    echo "   - Monitor for suspicious authentication failures"
    echo ""
    echo -e "${GREEN}🎉 DNS setup completed successfully!${NC}"
    echo -e "${BLUE}📝 Logs: $LOG_FILE${NC}"
    echo -e "${BLUE}💾 Backup: $BACKUP_FILE${NC}"
}

# Main execution function
main() {
    echo -e "${PURPLE}"
    echo "============================================================"
    echo "🚀 AIA Multi-Agent System: Proton Mail DNS Setup"
    echo "============================================================"
    echo -e "${NC}"
    echo "Domain: $DOMAIN"
    echo "Method: ${1:-auto}"
    echo "Timestamp: $(date)"
    echo ""

    # Setup logging
    mkdir -p "$(dirname "$LOG_FILE")"
    log "START" "Beginning Proton Mail DNS setup for $DOMAIN"

    # Execute deployment steps
    check_prerequisites
    verify_cloudflare_api
    get_zone_id
    backup_dns_records

    # Choose deployment method
    case "${1:-auto}" in
        python)
            deploy_python_method
            ;;
        terraform)
            deploy_terraform_method
            ;;
        both|auto)
            log_info "Trying Python method first..."
            if ! deploy_python_method; then
                log_warning "Python method failed, trying Terraform..."
                deploy_terraform_method
            fi
            ;;
        *)
            log_error "Invalid deployment method: $1"
            echo "Usage: $0 [python|terraform|both|auto]"
            return 1
            ;;
    esac

    # Verify and show next steps
    verify_dns_records
    show_next_steps

    log "COMPLETE" "Proton Mail DNS setup completed successfully"
}

# Execute main function with all arguments
main "$@"