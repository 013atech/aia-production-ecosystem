# Phase 1: AAM Architecture Implementation Guide

## Overview
This guide provides detailed implementation instructions for transforming the MAS system into an Agent-as-a-Microservice (AAM) architecture during weeks 1-4.

## Week 1-2: AAM Base Framework

### 1. Create AAM Base Structure

```python
# File: aia_system/aam/__init__.py
"""
Agent-as-a-Microservice Architecture
"""

from .base_service import AgentMicroservice
from .service_registry import ServiceRegistry
from .communication_layer import CommunicationLayer
from .circuit_breaker import CircuitBreaker

__all__ = [
    'AgentMicroservice',
    'ServiceRegistry', 
    'CommunicationLayer',
    'CircuitBreaker'
]
```

### 2. Implement Base Agent Microservice

```python
# File: aia_system/aam/base_service.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import uvicorn
import asyncio
import httpx
from datetime import datetime
import os

class AgentMicroservice:
    """
    Base class for agent microservices
    """
    
    def __init__(
        self,
        agent_type: str,
        service_name: str,
        port: int,
        version: str = "1.0.0"
    ):
        self.agent_type = agent_type
        self.service_name = service_name
        self.port = port
        self.version = version
        
        # Create FastAPI app for this microservice
        self.app = FastAPI(
            title=f"{service_name} Agent Service",
            version=version,
            description=f"Microservice for {agent_type} agent operations"
        )
        
        # Setup middleware
        self.setup_middleware()
        
        # Setup routes
        self.setup_routes()
        
        # Service discovery
        self.service_registry_url = os.getenv(
            "SERVICE_REGISTRY_URL", 
            "http://localhost:8500"
        )
        
        # Health check data
        self.startup_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
    def setup_middleware(self):
        """Configure middleware for the service"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    def setup_routes(self):
        """Setup base routes for the service"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": self.service_name,
                "version": self.version,
                "uptime": str(datetime.now() - self.startup_time),
                "requests_processed": self.request_count,
                "errors": self.error_count
            }
        
        @self.app.get("/info")
        async def service_info():
            """Service information endpoint"""
            return {
                "agent_type": self.agent_type,
                "service_name": self.service_name,
                "version": self.version,
                "capabilities": self.get_capabilities(),
                "port": self.port
            }
        
        @self.app.post("/process")
        async def process_task(task: Dict[str, Any]):
            """Main processing endpoint"""
            self.request_count += 1
            try:
                result = await self.process_agent_task(task)
                return {
                    "status": "success",
                    "result": result,
                    "agent": self.agent_type,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.error_count += 1
                raise HTTPException(status_code=500, detail=str(e))
    
    async def process_agent_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task - to be overridden by specific agent implementations
        """
        raise NotImplementedError("Subclasses must implement process_agent_task")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities - to be overridden
        """
        return {
            "base_capabilities": ["processing", "analysis"]
        }
    
    async def register_service(self):
        """Register service with service registry"""
        async with httpx.AsyncClient() as client:
            registration = {
                "name": self.service_name,
                "port": self.port,
                "agent_type": self.agent_type,
                "health_check": f"http://localhost:{self.port}/health",
                "tags": [self.agent_type, "aam", "agent-service"]
            }
            
            try:
                response = await client.post(
                    f"{self.service_registry_url}/register",
                    json=registration
                )
                print(f"✅ Service {self.service_name} registered successfully")
            except Exception as e:
                print(f"⚠️ Failed to register service: {e}")
    
    def run(self):
        """Run the microservice"""
        # Register service on startup
        asyncio.create_task(self.register_service())
        
        # Start the service
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
```

### 3. Implement GLAC Agent as Microservice

```python
# File: aia_system/aam/glac_service.py
import numpy as np
from typing import Dict, Any, List
from .base_service import AgentMicroservice
from ..agents.glac_agent import GLAC_Agent

class GLACMicroservice(AgentMicroservice):
    """
    GLAC Agent as a Microservice
    """
    
    def __init__(self, port: int = 8001):
        super().__init__(
            agent_type="GLAC",
            service_name="glac-agent-service",
            port=port,
            version="1.0.0"
        )
        
        # Initialize GLAC agent
        self.agent = GLAC_Agent(
            epsilon=0.1,
            beta=0.2,
            equilibrium_type='fixed_point',
            bias='unbiased'
        )
        
        # Add GLAC-specific routes
        self.setup_glac_routes()
    
    def setup_glac_routes(self):
        """Setup GLAC-specific routes"""
        
        @self.app.post("/glac/learn")
        async def genetic_learning(data: Dict[str, Any]):
            """Genetic learning endpoint"""
            population = data.get("population", [])
            fitness_scores = data.get("fitness_scores", [])
            
            result = self.agent.genetic_algorithm_learning(
                population, fitness_scores
            )
            
            return {
                "learned_strategy": result,
                "agent_type": "GLAC"
            }
        
        @self.app.post("/glac/decide")
        async def make_decision(data: Dict[str, Any]):
            """Decision making endpoint"""
            state = data.get("state", {})
            context = data.get("context", {})
            
            decision = self.agent.make_decision(state, context)
            
            return {
                "decision": decision,
                "confidence": self.agent.get_confidence(),
                "agent_type": "GLAC"
            }
    
    async def process_agent_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process GLAC-specific tasks
        """
        task_type = task.get("type", "general")
        
        if task_type == "optimization":
            return await self.process_optimization(task)
        elif task_type == "learning":
            return await self.process_learning(task)
        elif task_type == "consensus":
            return await self.process_consensus(task)
        else:
            return await self.process_general(task)
    
    async def process_optimization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process optimization tasks"""
        parameters = task.get("parameters", {})
        constraints = task.get("constraints", {})
        
        # Use genetic algorithm for optimization
        population = self.initialize_population(parameters)
        
        for generation in range(task.get("generations", 100)):
            fitness_scores = self.evaluate_fitness(population, constraints)
            population = self.agent.genetic_algorithm_learning(
                population, fitness_scores
            )
        
        best_solution = self.get_best_solution(population, constraints)
        
        return {
            "optimal_solution": best_solution,
            "fitness_score": self.evaluate_fitness([best_solution], constraints)[0],
            "generations_run": task.get("generations", 100)
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get GLAC agent capabilities"""
        return {
            "optimization": ["genetic_algorithm", "evolutionary_strategies"],
            "learning": ["reinforcement", "genetic"],
            "consensus": ["voting", "aggregation"],
            "specialization": "Global optimization and consensus building"
        }

# Run the service if executed directly
if __name__ == "__main__":
    service = GLACMicroservice(port=8001)
    service.run()
```

### 4. Implement Service Registry

```python
# File: aia_system/aam/service_registry.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import httpx

class ServiceRegistry:
    """
    Service registry for agent microservices
    """
    
    def __init__(self):
        self.services: Dict[str, Dict] = {}
        self.health_check_interval = 30  # seconds
        self.unhealthy_threshold = 3  # failed checks before marking unhealthy
        
    async def register(
        self,
        service_name: str,
        host: str,
        port: int,
        agent_type: str,
        health_check_url: str,
        tags: List[str] = None
    ) -> bool:
        """Register a new service"""
        
        service_id = f"{service_name}:{port}"
        
        self.services[service_id] = {
            "name": service_name,
            "host": host,
            "port": port,
            "agent_type": agent_type,
            "health_check_url": health_check_url,
            "tags": tags or [],
            "status": "healthy",
            "registered_at": datetime.now(),
            "last_health_check": datetime.now(),
            "failed_checks": 0
        }
        
        # Start health monitoring for this service
        asyncio.create_task(self.monitor_service_health(service_id))
        
        return True
    
    async def discover(
        self,
        agent_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """Discover services by type or tags"""
        
        results = []
        
        for service_id, service in self.services.items():
            if service["status"] != "healthy":
                continue
                
            if agent_type and service["agent_type"] != agent_type:
                continue
                
            if tags and not all(tag in service["tags"] for tag in tags):
                continue
                
            results.append(service)
        
        return results
    
    async def get_service_endpoint(
        self,
        agent_type: str
    ) -> Optional[str]:
        """Get endpoint for a specific agent type"""
        
        services = await self.discover(agent_type=agent_type)
        
        if not services:
            return None
        
        # Simple round-robin selection
        service = services[0]  # In production, implement proper load balancing
        
        return f"http://{service['host']}:{service['port']}"
    
    async def monitor_service_health(self, service_id: str):
        """Monitor health of a registered service"""
        
        while service_id in self.services:
            await asyncio.sleep(self.health_check_interval)
            
            service = self.services[service_id]
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        service["health_check_url"],
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        service["status"] = "healthy"
                        service["failed_checks"] = 0
                    else:
                        service["failed_checks"] += 1
                        
            except Exception as e:
                service["failed_checks"] += 1
                print(f"Health check failed for {service_id}: {e}")
            
            service["last_health_check"] = datetime.now()
            
            # Mark as unhealthy if threshold exceeded
            if service["failed_checks"] >= self.unhealthy_threshold:
                service["status"] = "unhealthy"
                print(f"Service {service_id} marked as unhealthy")
    
    async def deregister(self, service_id: str) -> bool:
        """Deregister a service"""
        
        if service_id in self.services:
            del self.services[service_id]
            return True
        
        return False
```

### 5. Implement Communication Layer

```python
# File: aia_system/aam/communication_layer.py
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from .circuit_breaker import CircuitBreaker

class CommunicationLayer:
    """
    Inter-service communication layer with circuit breaker pattern
    """
    
    def __init__(self, service_registry_url: str):
        self.service_registry_url = service_registry_url
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.timeout = 30.0
        
    async def call_agent(
        self,
        agent_type: str,
        endpoint: str,
        data: Dict[str, Any],
        method: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """
        Call an agent microservice with circuit breaker protection
        """
        
        # Get service endpoint from registry
        service_url = await self._get_service_url(agent_type)
        
        if not service_url:
            raise Exception(f"No healthy service found for agent type: {agent_type}")
        
        # Get or create circuit breaker for this service
        if agent_type not in self.circuit_breakers:
            self.circuit_breakers[agent_type] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=httpx.HTTPError
            )
        
        circuit_breaker = self.circuit_breakers[agent_type]
        
        # Make the call with circuit breaker
        try:
            async with circuit_breaker:
                async with httpx.AsyncClient() as client:
                    if method == "POST":
                        response = await client.post(
                            f"{service_url}{endpoint}",
                            json=data,
                            timeout=self.timeout
                        )
                    else:
                        response = await client.get(
                            f"{service_url}{endpoint}",
                            params=data,
                            timeout=self.timeout
                        )
                    
                    response.raise_for_status()
                    return response.json()
                    
        except Exception as e:
            print(f"Failed to call {agent_type} service: {e}")
            return None
    
    async def broadcast_to_agents(
        self,
        agent_types: List[str],
        endpoint: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Broadcast a request to multiple agent types
        """
        
        tasks = []
        for agent_type in agent_types:
            task = self.call_agent(agent_type, endpoint, data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            agent_type: result
            for agent_type, result in zip(agent_types, results)
            if not isinstance(result, Exception)
        }
    
    async def orchestrate_consensus(
        self,
        task: Dict[str, Any],
        agent_types: List[str] = ["GLAC", "TSGLA", "TASA-NS-Alg"]
    ) -> Dict[str, Any]:
        """
        Orchestrate consensus among multiple agents
        """
        
        # Get individual agent responses
        responses = await self.broadcast_to_agents(
            agent_types,
            "/process",
            task
        )
        
        # Build consensus
        consensus_data = {
            "responses": responses,
            "consensus_type": "weighted_average"
        }
        
        # Use GLAC for final consensus building
        consensus_result = await self.call_agent(
            "GLAC",
            "/glac/consensus",
            consensus_data
        )
        
        return {
            "individual_responses": responses,
            "consensus": consensus_result,
            "participating_agents": list(responses.keys())
        }
    
    async def _get_service_url(self, agent_type: str) -> Optional[str]:
        """Get service URL from registry"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.service_registry_url}/discover",
                params={"agent_type": agent_type}
            )
            
            if response.status_code == 200:
                services = response.json()
                if services:
                    # Simple selection - in production use load balancing
                    service = services[0]
                    return f"http://{service['host']}:{service['port']}"
            
            return None
```

### 6. Implement Circuit Breaker Pattern

```python
# File: aia_system/aam/circuit_breaker.py
from datetime import datetime, timedelta
from typing import Any, Type, Optional
import asyncio

class CircuitBreakerError(Exception):
    """Circuit breaker is open"""
    pass

class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half_open
        
    async def __aenter__(self):
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise CircuitBreakerError("Circuit breaker is open")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success - reset failure count
            self.on_success()
        elif issubclass(exc_type, self.expected_exception):
            # Expected failure - increment counter
            self.on_failure()
        
        # Don't suppress the exception
        return False
    
    def on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "closed"
    
    def on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > 
            timedelta(seconds=self.recovery_timeout)
        )
    
    @property
    def is_closed(self) -> bool:
        return self.state == "closed"
    
    @property
    def is_open(self) -> bool:
        return self.state == "open"
```

## Week 3-4: Service Mesh & Deployment

### 7. Docker Configuration for Microservices

```dockerfile
# File: aia_system/aam/dockerfiles/Dockerfile.glac
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent service code
COPY aia_system/aam/glac_service.py .
COPY aia_system/aam/base_service.py .
COPY aia_system/agents/glac_agent.py ./agents/

# Environment variables
ENV PYTHONPATH=/app
ENV SERVICE_PORT=8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/health')"

# Run the service
CMD ["python", "glac_service.py"]
```

### 8. Kubernetes Deployment

```yaml
# File: aia_system/k8s/aam/glac-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: glac-agent-service
  namespace: mas-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: glac-agent
      type: aam-service
  template:
    metadata:
      labels:
        app: glac-agent
        type: aam-service
        version: v1
    spec:
      containers:
      - name: glac-agent
        image: mas-system/glac-agent:1.0.0
        ports:
        - containerPort: 8001
          name: http
        env:
        - name: SERVICE_PORT
          value: "8001"
        - name: SERVICE_REGISTRY_URL
          value: "http://service-registry:8500"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: glac-agent-service
  namespace: mas-system
spec:
  selector:
    app: glac-agent
  ports:
  - port: 8001
    targetPort: 8001
    name: http
  type: ClusterIP
```

### 9. Istio Service Mesh Configuration

```yaml
# File: aia_system/k8s/aam/istio-virtualservice.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: agent-services
  namespace: mas-system
spec:
  hosts:
  - agent-services.mas-system.svc.cluster.local
  http:
  - match:
    - headers:
        agent-type:
          exact: GLAC
    route:
    - destination:
        host: glac-agent-service
        port:
          number: 8001
      weight: 100
  - match:
    - headers:
        agent-type:
          exact: TSGLA
    route:
    - destination:
        host: tsgla-agent-service
        port:
          number: 8002
      weight: 100
  - match:
    - headers:
        agent-type:
          exact: TASA-NS-Alg
    route:
    - destination:
        host: tasa-agent-service
        port:
          number: 8003
      weight: 100
```

### 10. Integration with Main API

```python
# File: aia_system/api/aam_integration.py
from typing import Dict, Any, List
from ..aam.communication_layer import CommunicationLayer

class AAMIntegration:
    """
    Integration layer for AAM services with main API
    """
    
    def __init__(self):
        self.comm_layer = CommunicationLayer(
            service_registry_url="http://service-registry:8500"
        )
    
    async def process_with_aam(
        self,
        prompt: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process request using AAM architecture
        """
        
        # Analyze task and determine agent allocation
        task_analysis = self.analyze_task(prompt)
        
        # Prepare task for agents
        agent_task = {
            "prompt": prompt,
            "type": task_analysis["task_type"],
            "parameters": task_analysis["parameters"],
            "config": config
        }
        
        # Orchestrate consensus among agents
        result = await self.comm_layer.orchestrate_consensus(
            task=agent_task,
            agent_types=task_analysis["recommended_agents"]
        )
        
        return {
            "result": result["consensus"],
            "individual_contributions": result["individual_responses"],
            "task_analysis": task_analysis
        }
    
    def analyze_task(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze task and determine optimal agent allocation
        """
        
        prompt_lower = prompt.lower()
        
        if "optimize" in prompt_lower or "best" in prompt_lower:
            return {
                "task_type": "optimization",
                "recommended_agents": ["GLAC", "TSGLA"],
                "parameters": {"focus": "global_optimization"}
            }
        elif "predict" in prompt_lower or "forecast" in prompt_lower:
            return {
                "task_type": "prediction",
                "recommended_agents": ["TSGLA", "TASA-NS-Alg"],
                "parameters": {"focus": "time_series_analysis"}
            }
        elif "analyze" in prompt_lower or "understand" in prompt_lower:
            return {
                "task_type": "analysis",
                "recommended_agents": ["GLAC", "TSGLA", "TASA-NS-Alg"],
                "parameters": {"focus": "comprehensive_analysis"}
            }
        else:
            return {
                "task_type": "general",
                "recommended_agents": ["GLAC", "TSGLA", "TASA-NS-Alg"],
                "parameters": {"focus": "balanced_approach"}
            }
```

## Testing & Validation

### Unit Tests

```python
# File: tests/test_aam_architecture.py
import pytest
import asyncio
from aia_system.aam.glac_service import GLACMicroservice
from aia_system.aam.service_registry import ServiceRegistry
from aia_system.aam.communication_layer import CommunicationLayer

@pytest.fixture
def glac_service():
    return GLACMicroservice(port=8001)

@pytest.fixture
def service_registry():
    return ServiceRegistry()

@pytest.mark.asyncio
async def test_glac_service_initialization(glac_service):
    """Test GLAC service initialization"""
    assert glac_service.agent_type == "GLAC"
    assert glac_service.port == 8001
    assert glac_service.agent is not None

@pytest.mark.asyncio
async def test_service_registration(service_registry):
    """Test service registration"""
    result = await service_registry.register(
        service_name="test-service",
        host="localhost",
        port=8001,
        agent_type="GLAC",
        health_check_url="http://localhost:8001/health"
    )
    assert result == True
    
    services = await service_registry.discover(agent_type="GLAC")
    assert len(services) == 1
    assert services[0]["name"] == "test-service"

@pytest.mark.asyncio
async def test_communication_layer():
    """Test inter-service communication"""
    comm_layer = CommunicationLayer("http://localhost:8500")
    
    # This would require running services
    # In unit tests, we'd mock the HTTP calls
    pass
```

## Deployment Steps

1. **Build Docker Images**:
```bash
cd aia_system/aam
docker build -f dockerfiles/Dockerfile.glac -t mas-system/glac-agent:1.0.0 .
docker build -f dockerfiles/Dockerfile.tsgla -t mas-system/tsgla-agent:1.0.0 .
docker build -f dockerfiles/Dockerfile.tasa -t mas-system/tasa-agent:1.0.0 .
```

2. **Deploy to Kubernetes**:
```bash
kubectl apply -f k8s/aam/
```

3. **Install Istio** (if not already installed):
```bash
istioctl install --set profile=demo
kubectl label namespace mas-system istio-injection=enabled
```

4. **Apply Istio Configuration**:
```bash
kubectl apply -f k8s/aam/istio-virtualservice.yaml
```

5. **Verify Deployment**:
```bash
kubectl get pods -n mas-system
kubectl get services -n mas-system
istioctl analyze -n mas-system
```

## Monitoring & Observability

### Prometheus Metrics
```yaml
# File: k8s/aam/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: agent-services
  namespace: mas-system
spec:
  selector:
    matchLabels:
      type: aam-service
  endpoints:
  - port: metrics
    interval: 30s
```

## Next Steps

After completing Phase 1:
1. Test individual agent microservices
2. Verify service discovery and registration
3. Test inter-service communication
4. Validate circuit breaker functionality
5. Load test the system
6. Move to Phase 2: Enhanced DKG implementation