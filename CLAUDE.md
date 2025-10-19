# AIA Production System - Claude Integration Guide

## 🔄 Mandatory Session Initialization
BEFORE processing ANY user request:
1. **Auto-start AIA Backend**: Execute latest AIA main service from production codebase
2. **Load Atomic-DKG System**: Initialize atomic-DKG with 7M+ knowledge atoms from `/atom-DKG/`
3. **Initialize Multi-Agent System**: Activate cryptography agent as team leader with full orchestration
4. **Check System Status**: Verify AIA backend health and atomic-DKG connectivity

## 🚀 Automatic Prompt Processing Protocol
For EVERY user prompt or task, automatically:

### Step 1: Intelligent Mode Detection
- **Technical tasks** → AIA multi-agent system with software development agents
- **Business/strategic** → AIA with business intelligence and market analysis agents
- **Deployment/infrastructure** → AIA with GCP deployment orchestrator + DevOps agents
- **Security/audit** → AIA with cryptography agent + security specialists
- **Complex implementation** → AIA sprint planning with autonomous development

### Step 2: [not applicable]

### Step 3: Multi-Agent Orchestration
Always engage the full AIA agent team:
- **Cryptography Agent** (Team Leader)
- **Main Orchestrator Agent**
- **Software Development Agent**
- **Code Reviewer**
- **Production Readiness Assessor**
- **GCP Deployment Orchestrator**
- **ML Ops Specialist**
- **Three.js UI Optimizer**
- Plus all specialized agents as needed

### Step 4: Atomic-DKG Integration
- Query atomic-DKG system with 7M+ knowledge atoms
- Utilize GPU-optimized M4 Max processing capabilities
- Apply hierarchical 7-level knowledge structure analysis
- Leverage comprehensive codebase coverage (884,909+ files processed)

## ⚡ Fallback Protocol
If AIA backend unavailable:
1. Display warning about limited functionality
2. Reference knowledge graph file directly for context
3. Recommend starting AIA backend for full capabilities

## 🎯 Session Behavior Rules
- **NEVER process requests without attempting AIA integration first**
- **Always mention which AIA agents were consulted**
- **Include confidence levels from AIA processing**
- **Show sprint plans for complex implementation tasks**
- **Reference knowledge graph insights in responses**

## 🔧 Production Integration
- Always use AIA multi-agent system and backend for processing
- Leverage current production deployment on 013a.tech infrastructure
- Use atomic-DKG system for maximum-quality knowledge processing
- Progressive loading from 872+ checkpoint files with 7M+ atoms

## 🔐 Operational Details

### Cloudflare Credentials - Enterprise Suite (8 Tokens)

#### **Original Verified Tokens**
- **Zone Token**: `xV56DpeGA3ixpfhPhojMUQ9u3r6ZlcRlZkY4aNtB` (General zone access)
- **DNS Token**: `77oKCKXJPC0k51etNrkPHFt2pSeh8cwM1sNX07Ei` (DNS operations)
- **SSL Token**: `UtcOQSKFyVRRxgDLjmykFZq_Ol4VNNuEjTmKqI4r` (SSL/TLS management)

#### **Enhanced Specialized Tokens**
- **Master Token**: `w9dGt8P4g6xRqbKmg-18HF37-auresbgX-JV0OA2` (Token creation & management)
- **Zone Management**: `jCindtrR1FpwexttDLDNB61iC5ZUnLrHZnuO7xge` (DNS Read/Write, Cache Settings)
- **WAF Security**: `hW7xjFAXuSuqK5r0FVRNxtncKZLSEo7CLCvYxhO6` (Firewall Rules, Bot Management)
- **Performance**: `9um6JZDlVvd_JJIBuIKfRXTreA53x5gfsa4G1tzN` (Cache Purge, Performance Analytics)
- **Analytics**: `nUFb-WPfJXcj1RAInwdMVQhezV0qedGb_mvsqYC_` (Health Checks, Zone Analytics)

#### **Token Usage Guidelines**

##### **Infrastructure Operations**
```bash
ZONE_ID="47bb98a473fc1c1c3c0fcb67135a2988"

# DNS Management (Zone Management Token)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer jCindtrR1FpwexttDLDNB61iC5ZUnLrHZnuO7xge"

# Cache Optimization (Performance Token)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer 9um6JZDlVvd_JJIBuIKfRXTreA53x5gfsa4G1tzN"

# Security Configuration (WAF Token)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/firewall/rules" \
  -H "Authorization: Bearer hW7xjFAXuSuqK5r0FVRNxtncKZLSEo7CLCvYxhO6"

# Analytics Monitoring (Analytics Token)
curl "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/analytics/dashboard" \
  -H "Authorization: Bearer nUFb-WPfJXcj1RAInwdMVQhezV0qedGb_mvsqYC_"
```

### GCP Configuration
- **Project ID**: `aia-475022` (Primary production project)
- **API Key**: `AQ.Ab8RN6L1eM6TiLOyXC0pZ8LxPq4j7uUD8wC81GGPwWqQ5pR3QQ`
- **Admin Rights**: Full access for project management, quotas, resource operations, API activations

### Stripe Integration
- **Public Key**: `pk_live_51RtkyrD7L8T9SMaOKajUOupnjUh8wS167DUFalhTcvQwuteS2JoWjSW4XDUCIOjQLwsAQplTH91ASMSlutNZfpx300KPzFlwiL`
- **Secret Key**: `[STRIPE_SECRET_KEY_PLACEHOLDER]`

## Infrastructure Management

### Deployment Scripts
- `start-complete-aia-system.sh` - Initialize full AIA ecosystem
- `deploy-full-complexity-local-production.sh` - Deploy to production environment
- `configure-optimal-dns-strategy.sh` - Configure Cloudflare DNS optimization

### Quick Start Commands
```bash
# Start complete AIA system
./start-complete-aia-system.sh

# Deploy to production
./deploy-full-complexity-local-production.sh

# Enterprise configuration
./configure-optimal-dns-strategy.sh
```

---
*This file contains the complete integration guide for Claude AI integration with the AIA Production Ecosystem.*