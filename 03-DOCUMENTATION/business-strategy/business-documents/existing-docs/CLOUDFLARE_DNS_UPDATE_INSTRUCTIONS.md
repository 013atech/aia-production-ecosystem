# Cloudflare DNS Configuration to Resolve 522 Error

## 🎯 Final Step to Fix https://013a.tech

### Current Issue
- **Domain**: 013a.tech currently points to old/incorrect IPs
- **New GCP IP**: 35.186.195.165 (europe-west4 deployment)
- **Status**: System deployed and working, just needs DNS update

### 📋 Cloudflare Configuration Steps

1. **Log into Cloudflare Dashboard**
   - Go to: https://dash.cloudflare.com/
   - Account: 7e17c2325b4bb22dabc9ea834162a71e
   - Token: m9D91CqxxOQPP5ctF7TvAKnbQ4fhtD7ptHzdhhxL

2. **Update DNS Records**
   ```
   Type: A
   Name: @
   Content: 35.186.195.165
   Proxy: Enabled (Orange Cloud)
   TTL: Auto

   Type: A
   Name: www
   Content: 35.186.195.165
   Proxy: Enabled (Orange Cloud)
   TTL: Auto
   ```

3. **Verify SSL/TLS Settings**
   - SSL/TLS → Overview → Set to "Full (strict)"
   - SSL/TLS → Edge Certificates → Enable "Always Use HTTPS"

### 🔄 Alternative: Automated DNS Update

Run this command to update DNS via Cloudflare API:

```bash
# Update main domain
curl -X PUT "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records/RECORD_ID" \
     -H "Authorization: Bearer m9D91CqxxOQPP5ctF7TvAKnbQ4fhtD7ptHzdhhxL" \
     -H "Content-Type: application/json" \
     --data '{
       "type": "A",
       "name": "013a.tech",
       "content": "35.186.195.165",
       "proxied": true
     }'
```

### ✅ Expected Result
After DNS propagation (2-5 minutes):
- https://013a.tech → **Fully functional AIA system**
- **No more 522 errors**
- **Immersive 3D interface** loads successfully
- **Multi-agent backend** accessible

### 🎊 System Features Now Available
- **Immersive 3D Analytics Dashboard**
- **Multi-Agent AI Orchestration**
- **Real-time Data Visualization**
- **Post-Quantum Cryptography**
- **Economic Token System**
- **Vertex AI Integration**

The AIA system deployment is **100% complete** - just needs the DNS update!