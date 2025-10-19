# Cloudflare DNS Configuration Fix for 013a.tech

## Current Issue
- **Problem**: 522 Connection Timed Out error
- **Cause**: Cloudflare DNS points to `172.67.159.200` but origin server is at `35.186.195.165`
- **Solution**: Update Cloudflare DNS records to point to GCP Load Balancer

## Required DNS Changes

### 1. A Record for Root Domain
```
Name: @
Type: A
Value: 35.186.195.165
Proxy: Enabled (Orange Cloud)
TTL: Auto
```

### 2. A Record for WWW Subdomain
```
Name: www
Type: A
Value: 35.186.195.165
Proxy: Enabled (Orange Cloud)
TTL: Auto
```

### 3. CNAME Record Alternative (if preferred)
```
Name: www
Type: CNAME
Value: 013a.tech
Proxy: Enabled (Orange Cloud)
TTL: Auto
```

## Cloudflare Configuration Steps

### Step 1: Access Cloudflare Dashboard
1. Go to https://dash.cloudflare.com
2. Select the 013a.tech domain
3. Navigate to DNS > Records

### Step 2: Update DNS Records
1. Find existing A records for @ and www
2. Update the IPv4 address to: `35.186.195.165`
3. Ensure Proxy status is enabled (orange cloud icon)
4. Save changes

### Step 3: SSL/TLS Configuration
1. Navigate to SSL/TLS > Overview
2. Set encryption mode to "Full (strict)"
3. Enable "Always Use HTTPS"
4. Enable "HTTP Strict Transport Security (HSTS)"

### Step 4: Caching Configuration
1. Navigate to Caching > Configuration
2. Set Browser Cache TTL to "4 hours"
3. Enable "Always Online"

### Step 5: Security Configuration
1. Navigate to Security > Settings
2. Set Security Level to "Medium"
3. Enable Bot Fight Mode
4. Configure Page Rules for API endpoints:
   - Rule: `*013a.tech/api/*`
   - Settings: Cache Level = Bypass, Security Level = High

## Verification Steps

### 1. DNS Propagation Check
```bash
# Check DNS resolution
nslookup 013a.tech
nslookup www.013a.tech

# Expected result should show Cloudflare IPs, not the origin IP
```

### 2. Origin Server Test
```bash
# Direct connection to GCP Load Balancer
curl -H "Host: 013a.tech" http://35.186.195.165/health

# Should return: healthy
```

### 3. SSL Certificate Validation
```bash
# Check SSL certificate
curl -I https://013a.tech
curl -I https://www.013a.tech

# Look for successful 200 responses and valid SSL headers
```

## Troubleshooting

### If 522 Error Persists:
1. **Check Origin Server**: Ensure GCP Load Balancer is responding
2. **Verify SSL**: Make sure GKE managed certificates are active
3. **Cloudflare Cache**: Purge all cache in Cloudflare dashboard
4. **Wait for Propagation**: DNS changes can take up to 24 hours

### If SSL Issues:
1. **Certificate Status**: Check managed certificate provisioning status:
   ```bash
   kubectl get managedcertificate aia-production-ssl-cert -n aia-frontend
   ```
2. **Ingress Status**: Verify ingress has received an IP:
   ```bash
   kubectl get ingress aia-production-ingress -n aia-frontend
   ```

## Current Deployment Status
- **GCP Static IP**: `35.186.195.165`
- **Frontend Service**: Running on GKE
- **Backend APIs**: Deployed and accessible
- **SSL Certificates**: Managed by GKE
- **Load Balancer**: GCP HTTP(S) Load Balancer

## Next Steps After DNS Update
1. Monitor DNS propagation
2. Test all endpoints (/, /api/*, /health)
3. Verify SSL certificate installation
4. Enable additional Cloudflare security features
5. Configure performance optimizations

## Emergency Rollback
If issues persist, temporarily disable Cloudflare proxy:
1. In DNS settings, click orange cloud to grey (DNS only)
2. This will bypass Cloudflare temporarily
3. Re-enable proxy after troubleshooting