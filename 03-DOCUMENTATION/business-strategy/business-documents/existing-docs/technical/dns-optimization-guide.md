# DNS Optimization Guide for 013a.tech

## Current Situation
- **Domain**: 013a.tech
- **Current DNS**: Cloudflare (104.21.90.188, 172.67.159.200)
- **Status**: HTTP 522 Backend Connection Error
- **Issue**: Cloudflare cannot reach the backend services

## Recommended DNS Configuration

### Option 1: Direct IP Routing (Immediate)
```
A Record: 013a.tech → 35.204.248.206
A Record: www.013a.tech → 35.204.248.206
A Record: api.013a.tech → 35.204.248.206
```

### Option 2: Cloudflare Proxy (Optimized)
1. Update Cloudflare DNS to point to 35.204.248.206
2. Configure Cloudflare proxy settings
3. Enable SSL/TLS encryption
4. Configure caching rules for optimal performance

## Implementation Steps

1. **Access Cloudflare Dashboard**
   - Login to Cloudflare account
   - Select 013a.tech domain

2. **Update A Records**
   ```
   Type: A
   Name: @
   Content: 35.204.248.206
   Proxy: Enabled (orange cloud)
   TTL: Auto
   ```

3. **Verify Configuration**
   ```bash
   nslookup 013a.tech
   curl -I https://013a.tech
   ```

## Expected Results
- **DNS Propagation**: 5-15 minutes
- **Full Propagation**: Up to 24 hours globally
- **Immediate Access**: Available via 35.204.248.206

## Testing Commands
```bash
# Test direct IP
curl http://35.204.248.206/api/status

# Test after DNS update
curl https://013a.tech/api/status

# Verify DNS resolution
dig 013a.tech A
```