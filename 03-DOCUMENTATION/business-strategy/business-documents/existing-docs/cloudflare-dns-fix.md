# Cloudflare DNS Configuration Fix for 013a.tech

## CRITICAL ISSUE ANALYSIS
The SSL certificate provisioning is failing because:
1. Cloudflare is proxying the domain (orange cloud enabled)
2. Google Cloud cannot validate domain ownership through HTTP/DNS challenges
3. All managed certificates show `FAILED_NOT_VISIBLE` status

## IMMEDIATE RESOLUTION STEPS

### Option A: Temporary Cloudflare Proxy Disable
1. Login to Cloudflare dashboard
2. Navigate to DNS records for 013a.tech
3. Set the following records to DNS Only (grey cloud):
   - A record: 013a.tech → 35.186.195.165
   - A record: www.013a.tech → 35.186.195.165
   - A record: api.013a.tech → 35.186.195.165
4. Wait 5-10 minutes for propagation
5. Google Cloud will then be able to validate the domain

### Option B: Use Cloudflare Origin Certificates
1. Generate an origin certificate in Cloudflare
2. Upload to GCP as a custom certificate
3. Configure SSL mode to Full (strict) in Cloudflare

## VERIFICATION COMMANDS
```bash
# Check certificate status
gcloud compute ssl-certificates describe mcrt-e81a9a99-2569-4545-a5f4-f8cebcc66690 --global

# Test direct GCP access
curl -k -H "Host: 013a.tech" https://35.186.195.165

# Monitor certificate provisioning
watch -n 30 'gcloud compute ssl-certificates list | grep 013a.tech'
```

## POST-RESOLUTION
Once certificate is ACTIVE, re-enable Cloudflare proxy for additional security and performance benefits.