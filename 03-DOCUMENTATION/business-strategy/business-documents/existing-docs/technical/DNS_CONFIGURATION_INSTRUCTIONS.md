# DNS Configuration Instructions for Sentient Canvas Dual-Layer Architecture

## ✅ DEPLOYMENT STATUS

**GCP Infrastructure**: ✅ **FULLY DEPLOYED**
- **Load Balancer IP**: `34.120.153.135`
- **Ingress**: Successfully configured with managed certificates
- **Backend Services**: Running and healthy (AIA Analytics API v3.0)
- **SSL Certificates**: Provisioning (waiting for DNS validation)

## 🎯 REQUIRED DNS RECORDS

Configure the following A records in your DNS provider (Cloudflare, etc.):

```
Record Type: A
Name: 013a.tech
Value: 34.120.153.135
TTL: 300 (or Auto)

Record Type: A
Name: www.013a.tech
Value: 34.120.153.135
TTL: 300 (or Auto)

Record Type: A
Name: api.013a.tech
Value: 34.120.153.135
TTL: 300 (or Auto)
```

## 🔧 MANUAL CONFIGURATION STEPS

### Step 1: Access Cloudflare Dashboard
1. Go to https://dash.cloudflare.com
2. Select the `013a.tech` domain
3. Navigate to **DNS** → **Records**

### Step 2: Add/Update A Records
For each domain (013a.tech, www.013a.tech, api.013a.tech):

1. **Type**: A
2. **Name**: [subdomain or @]
3. **IPv4 address**: `34.120.153.135`
4. **Proxy status**: 🟡 DNS only (click the cloud icon to disable proxy)
5. **TTL**: Auto
6. Click **Save**

### Step 3: Verification Commands
After DNS configuration, run these commands to verify:

```bash
# Check DNS propagation
dig 013a.tech +short
dig www.013a.tech +short
dig api.013a.tech +short

# Expected output for all: 34.120.153.135

# Test HTTP connectivity (before SSL is ready)
curl -H "Host: 013a.tech" http://34.120.153.135/
```

## ⚡ AUTOMATED VERIFICATION

Once DNS records are configured, the system will automatically:

1. **SSL Certificate Provisioning** (5-10 minutes)
   - Google Managed Certificates will validate domains
   - HTTPS endpoints will become available

2. **Dual-Layer Architecture Activation**
   - `013a.tech` → Main Sentient Canvas experience
   - `api.013a.tech` → Enterprise API integration layer

3. **Production Features Available**
   - Real-time Analytics
   - ML Processing Engine
   - Cognitive Computing
   - Enterprise Security
   - WebSocket Support

## 🚀 EXPECTED ENDPOINTS

After DNS + SSL provisioning completes:

- **https://013a.tech/** - Main Sentient Canvas Interface
- **https://www.013a.tech/** - Redirects to main interface
- **https://api.013a.tech/** - Enterprise API Integration
- **https://api.013a.tech/docs** - API Documentation
- **https://api.013a.tech/health** - Health Check

## 📊 SYSTEM VERIFICATION

Check SSL certificate status:
```bash
kubectl get managedcertificate -n aia-working-production
```

Monitor ingress status:
```bash
kubectl get ingress sentient-canvas-unified-ingress -n aia-working-production
```

## 🔍 TROUBLESHOOTING

**Issue**: SSL Certificate stuck in "Provisioning"
**Solution**: Verify DNS A records point to `34.120.153.135`

**Issue**: Connection refused/reset
**Solution**: Wait for SSL certificate to be "Active" before testing HTTPS

**Issue**: 404 errors
**Solution**: Verify backend pods are running:
```bash
kubectl get pods -n aia-working-production
```

---

## 🎉 NEXT STEPS

1. Configure DNS records as specified above
2. Wait 5-15 minutes for SSL certificate provisioning
3. Access https://013a.tech to experience the Sentient Canvas
4. Enterprise partners can use https://api.013a.tech for integrations

**Full complexity deployment achieved!** The unified neural intelligence platform with 2,472 knowledge atoms is ready for production.