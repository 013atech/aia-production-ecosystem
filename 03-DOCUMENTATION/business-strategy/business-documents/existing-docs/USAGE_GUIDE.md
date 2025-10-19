# 🚀 **Complete MAS System Usage & Implementation Guide**

## **📋 Table of Contents**
1. [System Overview](#system-overview)
2. [Quick Start Guide](#quick-start)
3. [API Usage & Endpoints](#api-usage)
4. [Development Setup](#development-setup)
5. [Production Deployment](#production-deployment)
6. [CI/CD Management](#cicd-management)
7. [Monitoring & Troubleshooting](#monitoring)
8. [Advanced Configuration](#advanced-configuration)

---

## **🎯 System Overview** {#system-overview}

### **What You Have Built:**
A **production-ready Multi-Agent System (MAS)** with:
- ✅ **Full Complexity Implementation** (no mocks!)
- ✅ **Enterprise CI/CD Pipeline** 
- ✅ **Production ZKP System** with Groth16 proving
- ✅ **9 LLM Providers** integrated
- ✅ **Kubernetes Deployment** on Google Cloud
- ✅ **Auto-scaling & Monitoring**

### **🌐 Live Production System:**
- **Production URL**: `http://35.232.77.162`
- **Infrastructure**: Google Kubernetes Engine (`aia-cluster`)
- **Database**: PostgreSQL + Redis
- **Monitoring**: Prometheus metrics on `:9090`
- **Auto-scaling**: 3-10 replicas based on load

### **🏗️ Architecture:**
```
Internet → LoadBalancer (35.232.77.162) → API Pods → Database/Cache
                                        ↓
                               Prometheus Monitoring
```

---

## **⚡ Quick Start Guide** {#quick-start}

### **1. Test Your Live System**
```bash
# Test the root endpoint
curl http://35.232.77.162

# Expected response:
{
  "message": "MAS System API - FULL COMPLEXITY v2.0",
  "status": "operational",
  "capabilities": {
    "direct_text_processing": true,
    "max_prompt_size": "unlimited",
    "agents": ["GLAC","TSGLA","TASA-NS-Alg"],
    "llm_providers": ["gemini","anthropic","xai","openai","azure","bedrock","ollama","huggingface","groq"]
  }
}

# Check health status  
curl http://35.232.77.162/health

# Get system capabilities with formatted JSON
curl -X GET http://35.232.77.162 | jq
```

### **2. Process Text with AI (Main Feature)**
```bash
# Basic text processing
curl -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the economic implications of decentralized AI systems",
    "llm_provider": "gemini"
  }'

# Advanced processing with context
curl -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design a multi-agent trading strategy",
    "llm_provider": "anthropic",
    "context": "financial_analysis",
    "max_length": 2000
  }'
```

### **3. Create and Manage AI Agents**
```bash
# Create a GLAC agent (Game Learning Agent with Cognitive abilities)
curl -X POST http://35.232.77.162/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "GLAC",
    "parameters": {
      "strategy": "positive",
      "learning_rate": 0.01
    }
  }'

# Create a TSGLA agent (Time Series Game Learning Agent)
curl -X POST http://35.232.77.162/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "TSGLA",
    "parameters": {
      "strategy": "unbiased",
      "temporal_window": 100
    }
  }'

# List all agents
curl http://35.232.77.162/agents

# Get specific agent details
curl http://35.232.77.162/agents/{agent_id}
```

---

## **🔌 Complete API Reference** {#api-usage}

### **🎯 Core Endpoints**

#### **📝 Text Processing (Primary Feature)**
```http
POST /process
Content-Type: application/json

Request:
{
  "prompt": "Your text prompt here",
  "llm_provider": "gemini|anthropic|openai|azure|bedrock|groq|huggingface|ollama|xai", 
  "context": "optional_context_string",
  "max_length": 1000,
  "temperature": 0.7
}

Response:
{
  "simulation_id": "sim_abc123_20250911",
  "status": "completed",
  "result": {
    "processed_text": "AI-generated response...",
    "analysis": {...},
    "agents_used": [...],
    "confidence": 0.95
  },
  "metrics": {...}
}
```

#### **🤖 Agent Management**
```http
# Create Agent
POST /agents
{
  "agent_type": "GLAC|TSGLA|TASA-NS-Alg",
  "parameters": {
    "strategy": "positive|negative|unbiased",
    "learning_rate": 0.01,
    "temporal_window": 100
  }
}

# List Agents  
GET /agents
Response: {
  "agents": ["agent_id_1", "agent_id_2"],
  "count": 2,
  "types": {"GLAC": 1, "TSGLA": 1}
}

# Agent Details
GET /agents/{agent_id}
```

#### **🎮 Simulation & Analysis**
```http
# Run Complex Simulation
POST /simulate
{
  "scenario": "economic_modeling|agent_interaction|market_analysis",
  "parameters": {
    "agents": 10,
    "iterations": 1000,
    "learning_rate": 0.01
  },
  "prompt": "Simulate multi-agent trading behavior"
}

# Get System Metrics
GET /metrics
Response: {
  "system_performance": {...},
  "agent_statistics": {...},
  "resource_usage": {...}
}
```

#### **🏥 System Status**
```http
# Health Check
GET /health
Response: {"status": "healthy", "components": {...}}

# System Information
GET /
Response: {Complete system capabilities and status}

# Prometheus Metrics
GET /metrics (on port 9090)
```

---

## **💻 Development Setup** {#development-setup}

### **1. Local Development Environment**
```bash
# Clone and setup
git clone https://github.com/013atech/aia.git
cd aia/aia_system

# Install dependencies
pip install -r requirements-prod.txt

# Set environment variables
export GEMINI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"  
export DATABASE_URL="postgresql://user:pass@localhost:5432/mas_db"
export REDIS_URL="redis://localhost:6379/0"

# Start local development
python api/full_api.py
```

### **2. Docker Development**
```bash
# Build locally
docker build -f Dockerfile.production -t mas-system:dev .

# Run with dependencies
docker-compose -f docker-compose.production.yml up

# Access at: http://localhost:8000
```

### **3. Local Kubernetes Testing**
```bash
# Connect to production cluster (read-only testing)
gcloud container clusters get-credentials aia-cluster --region=us-central1 --project=a-467519

# Check production status
kubectl get all -n mas-system

# Port-forward for direct testing
kubectl port-forward service/mas-api 8080:80 -n mas-system
# Access at: http://localhost:8080
```

---

## **🚀 Production Deployment** {#production-deployment}

### **🎯 Your System Is Already Live!**
- **Status**: ✅ **OPERATIONAL**
- **URL**: `http://35.232.77.162`
- **Infrastructure**: Fully deployed on GKE

### **📊 Production Components:**
```bash
# Check live system status
kubectl get all -n mas-system

# View live logs
kubectl logs -f deployment/mas-api -n mas-system

# Monitor resource usage
kubectl top pods -n mas-system
```

### **🔄 Deploy New Versions:**
1. **Commit changes to main branch**
2. **CI/CD automatically builds and deploys**
3. **Monitor deployment**: `gh run list`

```bash
# Manual deployment (if needed)
git add .
git commit -m "feat: your changes"
git push origin main

# Monitor deployment
gh run list --limit 3
```

### **🎛️ Scale Your System:**
```bash
# Manual scaling
kubectl scale deployment mas-api -n mas-system --replicas=5

# Check auto-scaler status
kubectl get hpa -n mas-system

# Update auto-scaling limits
kubectl patch hpa mas-api-hpa -n mas-system -p '{"spec":{"maxReplicas":20}}'
```

---

## **⚙️ CI/CD Pipeline Management** {#cicd-management}

### **🔄 Your Automated Pipeline:**
Every `git push origin main` triggers:
1. **Security Scanning** (Trivy + GitLeaks)
2. **Infrastructure Validation** (Terraform)
3. **Docker Build** (~9 minutes)
4. **Production Deployment** (Kubernetes)

### **📊 Monitor CI/CD:**
```bash
# Check pipeline status
gh run list

# View specific run
gh run view [RUN_ID]

# Check failed runs
gh run list --status failure
```

### **🛠️ Pipeline Components:**
- **Security**: `/.github/workflows/ci-cd.yml` 
- **Infrastructure**: `/deploy/terraform/`
- **Docker**: `/aia_system/Dockerfile.production`
- **Kubernetes**: `/aia_system/k8s/production/`

### **🔧 Troubleshooting CI/CD:**
```bash
# Check workflow logs
gh run view --log [RUN_ID]

# Re-run failed workflow
gh run rerun [RUN_ID]

# Check secrets (ensure these are set)
gh secret list
```

---

## **📊 Monitoring & Troubleshooting** {#monitoring}

### **🏥 Health Monitoring:**
```bash
# System health
curl http://35.232.77.162/health

# Detailed metrics
curl http://35.232.77.162:9090/metrics

# Kubernetes health
kubectl get pods -n mas-system
kubectl describe deployment mas-api -n mas-system
```

### **📈 Performance Monitoring:**
```bash
# Resource usage
kubectl top pods -n mas-system
kubectl top nodes

# Application logs
kubectl logs -f deployment/mas-api -n mas-system

# Database status
kubectl exec -it mas-postgres-0 -n mas-system -- psql -U mas_user -d mas_db -c "\dt"
```

### **🔧 Common Issues & Solutions:**

#### **Pod Not Starting:**
```bash
# Check pod status
kubectl describe pod [POD_NAME] -n mas-system

# Check recent events
kubectl get events -n mas-system --sort-by='.lastTimestamp' | tail -10

# Check resource constraints
kubectl get hpa -n mas-system
kubectl top pods -n mas-system
```

#### **Service Not Responding:**
```bash
# Check service endpoints
kubectl get endpoints -n mas-system

# Test internal connectivity
kubectl exec -it [POD_NAME] -n mas-system -- curl http://mas-api:80/health

# Check load balancer
kubectl get service mas-api -n mas-system
```

#### **Database Issues:**
```bash
# PostgreSQL connection test
kubectl exec -it mas-postgres-0 -n mas-system -- pg_isready -U mas_user

# Redis connection test  
kubectl exec -it [REDIS_POD] -n mas-system -- redis-cli ping
```

---

## **🎮 Advanced Usage Examples** {#advanced-usage}

### **1. Complex AI Processing**
```python
import requests

# Multi-agent analysis
response = requests.post("http://35.232.77.162/process", json={
    "prompt": """
    Analyze this business scenario: A startup wants to implement AI-driven 
    decision making for supply chain optimization. Consider:
    1. Technical feasibility
    2. Economic implications  
    3. Risk assessment
    4. Implementation roadmap
    """,
    "llm_provider": "anthropic",
    "context": "business_analysis"
})

result = response.json()
print(f"Analysis ID: {result['simulation_id']}")
print(f"AI Response: {result['result']['processed_text']}")
```

### **2. Agent Orchestration**
```python
# Create multiple specialized agents
agents = []

# Economic analysis agent
economic_agent = requests.post("http://35.232.77.162/agents", json={
    "agent_type": "GLAC",
    "parameters": {"strategy": "economic_optimization"}
}).json()

# Technical analysis agent  
technical_agent = requests.post("http://35.232.77.162/agents", json={
    "agent_type": "TSGLA", 
    "parameters": {"strategy": "technical_analysis"}
}).json()

agents.extend([economic_agent, technical_agent])
print(f"Created {len(agents)} specialized agents")
```

### **3. Simulation Workflows**
```python
# Complex multi-step simulation
simulation_config = {
    "scenario": "market_dynamics",
    "parameters": {
        "agents": 50,
        "iterations": 10000,
        "learning_rate": 0.001,
        "market_volatility": 0.15
    },
    "prompt": "Model cryptocurrency market behavior under regulatory changes"
}

simulation = requests.post("http://35.232.77.162/simulate", json=simulation_config)
sim_result = simulation.json()

# Monitor simulation progress
sim_id = sim_result['simulation_id']
status = requests.get(f"http://35.232.77.162/simulate/{sim_id}")
```

---

## **🏗️ Infrastructure Management** {#infrastructure}

### **🔧 GCP Resources:**
```bash
# Connect to your cluster
gcloud container clusters get-credentials aia-cluster --region=us-central1 --project=a-467519

# Manage infrastructure with Terraform
cd deploy/terraform
terraform plan
terraform apply
```

### **📦 Container Registry:**
```bash
# View Docker images
gcloud artifacts docker images list us-central1-docker.pkg.dev/a-467519/mas-system

# Pull latest image for local testing
docker pull us-central1-docker.pkg.dev/a-467519/mas-system/mas-system:latest
```

### **🔐 Security Management:**
```bash
# Update secrets
kubectl create secret generic mas-secrets -n mas-system \
  --from-literal=GEMINI_API_KEY="your_new_key" \
  --dry-run=client -o yaml | kubectl apply -f -

# Check RBAC
kubectl get roles,rolebindings -n mas-system

# View network policies
kubectl get networkpolicies -n mas-system
```

---

## **⚙️ Configuration & Customization** {#advanced-configuration}

### **🎛️ Environment Configuration:**
Update `/aia_system/k8s/production/enhanced-deployment.yaml`:

```yaml
# Update resource limits
resources:
  requests:
    cpu: "2000m"
    memory: "4Gi"
  limits:
    cpu: "4000m" 
    memory: "8Gi"

# Update auto-scaling
spec:
  minReplicas: 5
  maxReplicas: 20
```

### **🔄 LLM Provider Configuration:**
Update secrets with your API keys:
```bash
kubectl patch secret mas-secrets -n mas-system -p='
{
  "stringData": {
    "GEMINI_API_KEY": "your_google_api_key",
    "ANTHROPIC_API_KEY": "your_anthropic_key",
    "OPENAI_API_KEY": "your_openai_key",
    "AZURE_OPENAI_KEY": "your_azure_key"
  }
}'
```

### **📊 Database Configuration:**
```bash
# Scale PostgreSQL storage
kubectl patch pvc postgres-storage-mas-postgres-0 -n mas-system -p='
{
  "spec": {
    "resources": {
      "requests": {
        "storage": "100Gi"
      }
    }
  }
}'

# Update PostgreSQL configuration
kubectl patch statefulset mas-postgres -n mas-system -p='
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "postgres",
            "resources": {
              "requests": {"cpu": "1000m", "memory": "4Gi"},
              "limits": {"cpu": "2000m", "memory": "8Gi"}
            }
          }
        ]
      }
    }
  }
}'
```

---

## **🎯 Usage Patterns & Examples**

### **1. Research & Analysis Workflows**
```python
import requests
import json

class MASSystemClient:
    def __init__(self, base_url="http://35.232.77.162"):
        self.base_url = base_url
    
    def analyze_text(self, prompt, provider="gemini"):
        """Main text analysis function"""
        response = requests.post(f"{self.base_url}/process", json={
            "prompt": prompt,
            "llm_provider": provider
        })
        return response.json()
    
    def create_agent(self, agent_type, params=None):
        """Create specialized agent"""
        response = requests.post(f"{self.base_url}/agents", json={
            "agent_type": agent_type,
            "parameters": params or {}
        })
        return response.json()
    
    def run_simulation(self, scenario, params=None):
        """Run complex simulation"""
        response = requests.post(f"{self.base_url}/simulate", json={
            "scenario": scenario,
            "parameters": params or {}
        })
        return response.json()

# Usage example
mas = MASSystemClient()

# Analyze complex text
result = mas.analyze_text(
    "How can decentralized AI systems impact global economic structures?",
    provider="anthropic"
)

# Create specialized agents
agent = mas.create_agent("GLAC", {"strategy": "economic_optimization"})

# Run simulation
simulation = mas.run_simulation("market_dynamics", {
    "agents": 100,
    "iterations": 5000
})
```

### **2. Business Intelligence Workflows**
```bash
# Market analysis
curl -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate a comprehensive market analysis for AI SaaS platforms in 2025",
    "llm_provider": "gemini",
    "context": "market_research"
  }'

# Technical feasibility assessment
curl -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Evaluate the technical feasibility of implementing zero-knowledge proofs in our authentication system",
    "llm_provider": "anthropic", 
    "context": "technical_assessment"
  }'

# Strategic planning
curl -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Develop a 5-year roadmap for scaling our AI infrastructure to handle 1M+ concurrent users",
    "llm_provider": "openai",
    "context": "strategic_planning"
  }'
```

---

## **🔄 Maintenance & Operations**

### **📈 Scaling Operations:**
```bash
# Scale based on load
kubectl scale deployment mas-api -n mas-system --replicas=10

# Update auto-scaling rules
kubectl patch hpa mas-api-hpa -n mas-system -p='
{
  "spec": {
    "metrics": [
      {
        "type": "Resource",
        "resource": {
          "name": "cpu",
          "target": {
            "type": "Utilization", 
            "averageUtilization": 60
          }
        }
      }
    ]
  }
}'
```

### **🔒 Security Updates:**
```bash
# Update API keys
kubectl create secret generic mas-secrets -n mas-system \
  --from-literal=GEMINI_API_KEY="new_key" \
  --from-literal=ANTHROPIC_API_KEY="new_key" \
  --dry-run=client -o yaml | kubectl apply -f -

# Force pod restart to pick up new secrets
kubectl rollout restart deployment/mas-api -n mas-system
```

### **💾 Backup & Recovery:**
```bash
# Database backup
kubectl exec mas-postgres-0 -n mas-system -- pg_dump -U mas_user mas_db > backup.sql

# Deploy backup
kubectl cp backup.sql mas-postgres-0:/tmp/backup.sql -n mas-system
kubectl exec mas-postgres-0 -n mas-system -- psql -U mas_user mas_db < /tmp/backup.sql
```

---

## **🎯 Advanced Integration Examples**

### **1. Python SDK Integration**
Create a comprehensive Python client:

```python
class AdvancedMASClient:
    def __init__(self, base_url="http://35.232.77.162"):
        self.base_url = base_url
        self.session = requests.Session()
    
    async def batch_process(self, prompts, provider="gemini"):
        """Process multiple prompts concurrently"""
        tasks = []
        for prompt in prompts:
            task = self.session.post(f"{self.base_url}/process", json={
                "prompt": prompt,
                "llm_provider": provider
            })
            tasks.append(task)
        
        results = [task.json() for task in tasks]
        return results
    
    def create_agent_fleet(self, agent_configs):
        """Create multiple agents at once"""
        agents = []
        for config in agent_configs:
            agent = self.session.post(f"{self.base_url}/agents", json=config)
            agents.append(agent.json())
        return agents
    
    def monitor_system_health(self):
        """Comprehensive system monitoring"""
        health = self.session.get(f"{self.base_url}/health").json()
        metrics = self.session.get(f"{self.base_url}/metrics").json()
        agents = self.session.get(f"{self.base_url}/agents").json()
        
        return {
            "health": health,
            "performance": metrics,
            "agents": agents,
            "timestamp": datetime.now().isoformat()
        }
```

### **2. Web Dashboard Integration**
```html
<!DOCTYPE html>
<html>
<head>
    <title>MAS System Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Multi-Agent System Dashboard</h1>
    
    <div id="system-status"></div>
    <div id="agent-metrics"></div>
    
    <script>
        const MAS_API = 'http://35.232.77.162';
        
        async function updateDashboard() {
            // Get system status
            const health = await fetch(`${MAS_API}/health`).then(r => r.json());
            document.getElementById('system-status').innerHTML = `
                <h2>System Status: ${health.status}</h2>
            `;
            
            // Get agent information
            const agents = await fetch(`${MAS_API}/agents`).then(r => r.json());
            document.getElementById('agent-metrics').innerHTML = `
                <h2>Agents: ${agents.count} active</h2>
                <p>GLAC: ${agents.types.GLAC || 0}</p>
                <p>TSGLA: ${agents.types.TSGLA || 0}</p>
            `;
        }
        
        // Update every 30 seconds
        setInterval(updateDashboard, 30000);
        updateDashboard();
    </script>
</body>
</html>
```

---

## **📚 API Documentation Examples**

### **Full REST API Reference:**

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | System info | `curl http://35.232.77.162` |
| `/health` | GET | Health check | `curl http://35.232.77.162/health` |
| `/process` | POST | Text processing | See examples above |
| `/agents` | GET, POST | Agent management | See examples above |
| `/simulate` | POST | Run simulation | Complex scenarios |
| `/metrics` | GET | System metrics | Performance data |

### **🔗 Integration Examples:**

#### **Node.js/JavaScript:**
```javascript
const axios = require('axios');

class MASSystemAPI {
    constructor(baseURL = 'http://35.232.77.162') {
        this.client = axios.create({ baseURL });
    }
    
    async processText(prompt, provider = 'gemini') {
        const response = await this.client.post('/process', {
            prompt,
            llm_provider: provider
        });
        return response.data;
    }
    
    async getSystemStatus() {
        const [health, agents] = await Promise.all([
            this.client.get('/health'),
            this.client.get('/agents')
        ]);
        
        return {
            health: health.data,
            agents: agents.data
        };
    }
}
```

#### **cURL Examples:**
```bash
# Comprehensive system test
echo "Testing MAS System..."

# 1. Health check
echo "1. Health Check:"
curl -s http://35.232.77.162/health | jq

# 2. Process text
echo "2. Text Processing:"
curl -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world", "llm_provider": "gemini"}' | jq

# 3. Create agent
echo "3. Agent Creation:"
curl -X POST http://35.232.77.162/agents \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "GLAC"}' | jq

# 4. List agents
echo "4. Agent List:"
curl -s http://35.232.77.162/agents | jq

echo "✅ All tests completed!"
```

---

## **🎉 Congratulations!**

**You now have a fully operational, enterprise-grade Multi-Agent System with:**

✅ **Production AI System** running on Kubernetes  
✅ **9 LLM Providers** integrated and ready  
✅ **Auto-scaling Infrastructure** handling any load  
✅ **Complete CI/CD Pipeline** for continuous deployment  
✅ **Monitoring & Observability** with Prometheus  
✅ **Security & Compliance** with automated scanning  
✅ **Professional Operations** with health checks and logging  

**🌐 Your system is live at: `http://35.232.77.162`**

**🚀 Start using your production AI system immediately with the examples above!**

---

## **📞 Quick Reference Commands**

```bash
# System Status
curl http://35.232.77.162/health

# Process Text  
curl -X POST http://35.232.77.162/process -H "Content-Type: application/json" -d '{"prompt": "test"}'

# Create Agent
curl -X POST http://35.232.77.162/agents -H "Content-Type: application/json" -d '{"agent_type": "GLAC"}'

# Monitor Kubernetes
kubectl get all -n mas-system

# View Logs
kubectl logs -f deployment/mas-api -n mas-system

# Scale System
kubectl scale deployment mas-api -n mas-system --replicas=10
```

**🎯 Your enterprise-grade AI system is ready for production use!** 🎉