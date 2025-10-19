# Cloudflare DNS Management Token - Usage Guide

## Secret Manager Details

**Secret Name**: `cloudflare-dns-management-token`
**GCP Project**: Current project (accessible via `gcloud config get-value project`)
**Created**: 2025-09-18
**Expiry**: 2026-09-18 (1 year validity)

## Token Information

**Token ID**: `8b554c4eca9478336bdc628a891cbe00`
**Token Name**: `013a-aia-dns-management-token`
**Zone Access**: `013a.tech` (Zone ID: `47bb98a473fc1c1c3c0fcb67135a2988`)

### Permissions
- **Zone Read**: View zone settings and configuration
- **DNS Read**: List and view DNS records
- **DNS Write**: Create, update, and delete DNS records

## How to Use This Token

### 1. Retrieve Token from Secret Manager
```bash
# Get the token value
export CLOUDFLARE_DNS_TOKEN=$(gcloud secrets versions access latest --secret="cloudflare-dns-management-token")

# Verify token is active
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer $CLOUDFLARE_DNS_TOKEN"
```

### 2. Common DNS Operations

#### List DNS Records
```bash
curl -s "https://api.cloudflare.com/client/v4/zones/47bb98a473fc1c1c3c0fcb67135a2988/dns_records" \
     -H "Authorization: Bearer $CLOUDFLARE_DNS_TOKEN"
```

#### Update DNS Record (Example: Change A record)
```bash
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/47bb98a473fc1c1c3c0fcb67135a2988/dns_records/{RECORD_ID}" \
     -H "Authorization: Bearer $CLOUDFLARE_DNS_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"content": "NEW_IP_ADDRESS"}'
```

#### Enable/Disable Cloudflare Proxy
```bash
# Enable proxy
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/47bb98a473fc1c1c3c0fcb67135a2988/dns_records/{RECORD_ID}" \
     -H "Authorization: Bearer $CLOUDFLARE_DNS_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"proxied": true}'

# Disable proxy
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/47bb98a473fc1c1c3c0fcb67135a2988/dns_records/{RECORD_ID}" \
     -H "Authorization: Bearer $CLOUDFLARE_DNS_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"proxied": false}'
```

#### Create New DNS Record
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/47bb98a473fc1c1c3c0fcb67135a2988/dns_records" \
     -H "Authorization: Bearer $CLOUDFLARE_DNS_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "type": "A",
       "name": "subdomain.013a.tech",
       "content": "IP_ADDRESS",
       "ttl": 300,
       "proxied": true
     }'
```

## When to Use This Token

### 🔧 **Deployment Automation**
- **Infrastructure as Code**: Use in Terraform/Pulumi for DNS record management
- **CI/CD Pipelines**: Automate DNS updates during deployments
- **Blue/Green Deployments**: Switch traffic between environments

### 🚨 **Emergency Response**
- **SSL Certificate Issues**: Enable/disable proxy to resolve certificate problems
- **Traffic Routing**: Redirect traffic during outages or maintenance
- **Load Balancing**: Update backend IPs for load distribution

### 🔄 **Maintenance Operations**
- **IP Address Changes**: Update records when backend services move
- **Subdomain Management**: Create/update records for new services
- **Security Updates**: Modify DNS settings for security configurations

### 📊 **Monitoring Integration**
- **Health Checks**: Programmatically update DNS based on service health
- **Auto-scaling**: Dynamic DNS updates for auto-scaling environments
- **Performance Optimization**: Enable/disable CDN based on performance metrics

## Security Best Practices

### Token Management
1. **Least Privilege**: Token only has DNS permissions, no zone settings access
2. **Expiry Management**: Token expires 2026-09-18, set calendar reminder for renewal
3. **Audit Trail**: All API calls are logged in Cloudflare dashboard
4. **Access Control**: Only store in GCP Secret Manager, never in code repositories

### Usage Guidelines
```bash
# Always verify token before critical operations
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer $CLOUDFLARE_DNS_TOKEN" | jq .

# Test DNS changes with non-critical records first
# Use dry-run equivalent by checking current state before modifications

# Implement rollback procedures
# Always note the original configuration before making changes
```

## Current DNS Configuration Status (as of 2025-09-18)

### SSL Resolution Applied
- **013a.tech**: A record pointing to `35.186.195.165` with **Cloudflare proxy ENABLED**
- **www.013a.tech**: CNAME to `013a.tech` with **Cloudflare proxy ENABLED**
- **Other subdomains**: Various configurations, mostly proxied to `34.9.218.172`

### Applied Fix for SSL Issue
The primary SSL certificate issue was resolved by enabling Cloudflare proxy for the main domain records. This provides:
1. **SSL Termination**: Cloudflare handles SSL certificates automatically
2. **Security**: DDoS protection and Web Application Firewall
3. **Performance**: CDN caching and optimization
4. **Reliability**: Global network with high availability

## Troubleshooting

### Token Issues
```bash
# Check token status
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer $CLOUDFLARE_DNS_TOKEN"

# If token expired, create new one with same permissions
# Follow same process as original creation
```

### DNS Propagation
```bash
# Check DNS resolution
dig 013a.tech
nslookup 013a.tech

# Test from different locations
curl "https://dns.google/resolve?name=013a.tech&type=A"
```

### SSL Verification
```bash
# Test SSL certificate
openssl s_client -connect 013a.tech:443 -servername 013a.tech

# Check SSL rating
curl -s "https://api.ssllabs.com/api/v3/analyze?host=013a.tech"
```

## Emergency Contact Information

### Cloudflare Support
- **Dashboard**: https://dash.cloudflare.com/
- **Zone ID**: `47bb98a473fc1c1c3c0fcb67135a2988`
- **Support Docs**: https://developers.cloudflare.com/api/

### GCP Secret Manager
```bash
# Access secret
gcloud secrets versions access latest --secret="cloudflare-dns-management-token"

# List versions
gcloud secrets versions list cloudflare-dns-management-token

# Add new version (for token rotation)
gcloud secrets versions add cloudflare-dns-management-token --data-file=path/to/new/token
```

---

**Important**: This token provides comprehensive DNS management capabilities for the 013a.tech domain. Use responsibly and always test changes in a safe manner. The token is secured in GCP Secret Manager and should never be exposed in code repositories or logs.