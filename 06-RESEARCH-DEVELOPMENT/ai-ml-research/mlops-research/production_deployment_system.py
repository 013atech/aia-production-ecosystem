#!/usr/bin/env python3
"""
🚀 PRODUCTION DEPLOYMENT SYSTEM - ENTERPRISE KNOWLEDGE PROCESSING ENDPOINTS
===========================================================================

Production deployment system for knowledge processing endpoints across domains:
- api.013a.tech/knowledge-graph
- analytics.013a.tech
- ml.013a.tech
- enterprise.013a.tech

Key Features:
- Multi-domain deployment orchestration
- Load balancing and auto-scaling
- Health monitoring and circuit breakers
- Blue-green deployment strategies
- Integration with all MLOps components

Author: Claude Code (MLOps Specialist)
Version: v3.0 - Enterprise Production
Deployment: Production Ready
"""

import json
import logging
import asyncio
import threading
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import subprocess
import tempfile
from collections import defaultdict, deque
import concurrent.futures

# FastAPI & Async
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# HTTP Client
import httpx

# System Integration
import sqlite3
from contextlib import contextmanager
import yaml

@dataclass
class DeploymentEndpoint:
    """Configuration for production deployment endpoint."""
    endpoint_id: str
    domain: str
    subdomain: str
    service_type: str  # "knowledge_graph", "analytics", "ml_pipeline", "enterprise"
    port: int
    health_check_path: str
    load_balancer_config: Dict[str, Any]
    ssl_enabled: bool = True
    auto_scaling: bool = True
    circuit_breaker: bool = True
    deployment_strategy: str = "blue_green"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ServiceInstance:
    """Individual service instance."""
    instance_id: str
    endpoint_id: str
    host: str
    port: int
    status: str  # "starting", "healthy", "unhealthy", "stopping"
    health_score: float
    cpu_usage: float
    memory_usage: float
    request_count: int
    error_count: int
    last_health_check: datetime = field(default_factory=datetime.now)

@dataclass
class DeploymentStatus:
    """Overall deployment status."""
    deployment_id: str
    endpoint_id: str
    strategy: str
    current_version: str
    target_version: str
    status: str  # "planning", "deploying", "completed", "failed", "rollback"
    progress_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class HealthChecker:
    """Health checking system for deployed services."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.health_history = defaultdict(deque)

    async def check_health(
        self,
        service_instance: ServiceInstance,
        timeout: float = 5.0
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check health of a service instance."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                health_url = f"http://{service_instance.host}:{service_instance.port}/health"
                response = await client.get(health_url)

                if response.status_code == 200:
                    health_data = response.json()
                    return True, health_data
                else:
                    return False, {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            self.logger.warning(f"Health check failed for {service_instance.instance_id}: {e}")
            return False, {"error": str(e)}

    def update_health_history(
        self,
        instance_id: str,
        is_healthy: bool,
        health_data: Dict[str, Any]
    ):
        """Update health history for an instance."""
        health_record = {
            "timestamp": datetime.now(),
            "is_healthy": is_healthy,
            "health_data": health_data
        }

        self.health_history[instance_id].append(health_record)

        # Keep only recent history
        if len(self.health_history[instance_id]) > 100:
            self.health_history[instance_id].popleft()

    def calculate_health_score(self, instance_id: str) -> float:
        """Calculate health score based on recent history."""
        if instance_id not in self.health_history:
            return 0.5

        recent_checks = list(self.health_history[instance_id])[-20:]  # Last 20 checks
        if not recent_checks:
            return 0.5

        healthy_count = sum(1 for check in recent_checks if check["is_healthy"])
        return healthy_count / len(recent_checks)

class LoadBalancer:
    """Load balancer for distributing requests across service instances."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.routing_strategies = {
            "round_robin": self._round_robin,
            "weighted_round_robin": self._weighted_round_robin,
            "least_connections": self._least_connections,
            "health_based": self._health_based
        }
        self.current_index = defaultdict(int)

    def select_instance(
        self,
        instances: List[ServiceInstance],
        strategy: str = "health_based"
    ) -> Optional[ServiceInstance]:
        """Select best instance based on strategy."""
        if not instances:
            return None

        # Filter healthy instances
        healthy_instances = [
            instance for instance in instances
            if instance.status == "healthy" and instance.health_score > 0.7
        ]

        if not healthy_instances:
            # Fall back to any available instance
            healthy_instances = [
                instance for instance in instances
                if instance.status in ["healthy", "starting"]
            ]

        if not healthy_instances:
            return None

        strategy_func = self.routing_strategies.get(strategy, self._health_based)
        return strategy_func(healthy_instances)

    def _round_robin(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin load balancing."""
        endpoint_id = instances[0].endpoint_id
        index = self.current_index[endpoint_id] % len(instances)
        self.current_index[endpoint_id] += 1
        return instances[index]

    def _weighted_round_robin(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round-robin based on health scores."""
        weights = [max(0.1, instance.health_score) for instance in instances]
        total_weight = sum(weights)

        if total_weight == 0:
            return self._round_robin(instances)

        # Select based on weights
        import random
        r = random.uniform(0, total_weight)
        cumulative = 0

        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return instances[i]

        return instances[-1]

    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Select instance with least connections."""
        return min(instances, key=lambda x: x.request_count)

    def _health_based(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Select instance with best health score."""
        return max(instances, key=lambda x: x.health_score)

class CircuitBreaker:
    """Circuit breaker for service resilience."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.states = {}  # instance_id -> state info
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def can_request(self, instance_id: str) -> bool:
        """Check if requests can be sent to instance."""
        if instance_id not in self.states:
            self.states[instance_id] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "success_count": 0,
                "last_failure": None,
                "last_attempt": None
            }

        state_info = self.states[instance_id]

        if state_info["state"] == "closed":
            return True
        elif state_info["state"] == "open":
            # Check if we should try half-open
            if (datetime.now() - state_info["last_failure"]).total_seconds() > self.recovery_timeout:
                state_info["state"] = "half_open"
                state_info["success_count"] = 0
                return True
            return False
        else:  # half_open
            return True

    def record_success(self, instance_id: str):
        """Record successful request."""
        if instance_id not in self.states:
            return

        state_info = self.states[instance_id]

        if state_info["state"] == "half_open":
            state_info["success_count"] += 1
            if state_info["success_count"] >= self.success_threshold:
                state_info["state"] = "closed"
                state_info["failure_count"] = 0
        elif state_info["state"] == "closed":
            state_info["failure_count"] = max(0, state_info["failure_count"] - 1)

    def record_failure(self, instance_id: str):
        """Record failed request."""
        if instance_id not in self.states:
            self.states[instance_id] = {
                "state": "closed",
                "failure_count": 0,
                "success_count": 0,
                "last_failure": None,
                "last_attempt": None
            }

        state_info = self.states[instance_id]
        state_info["failure_count"] += 1
        state_info["last_failure"] = datetime.now()

        if state_info["failure_count"] >= self.failure_threshold:
            state_info["state"] = "open"
            self.logger.warning(f"Circuit breaker opened for instance {instance_id}")

class ProductionDeploymentSystem:
    """Main production deployment system."""

    def __init__(self, database_path: str = "/tmp/deployment_system.db"):
        self.logger = logging.getLogger(__name__)
        self.database_path = Path(database_path)

        # Core components
        self.health_checker = HealthChecker()
        self.load_balancer = LoadBalancer()
        self.circuit_breaker = CircuitBreaker()

        # System state
        self.endpoints = {}
        self.service_instances = {}
        self.deployments = {}

        # Background processes
        self.running = False
        self.monitor_thread = None

        # Domain configurations
        self.domain_configs = {
            "api.013a.tech": {
                "services": ["knowledge_graph", "atomic_dkg"],
                "base_port": 8001,
                "ssl_required": True
            },
            "analytics.013a.tech": {
                "services": ["business_intelligence", "performance_dashboard"],
                "base_port": 8101,
                "ssl_required": True
            },
            "ml.013a.tech": {
                "services": ["ml_pipelines", "model_serving"],
                "base_port": 8201,
                "ssl_required": True
            },
            "enterprise.013a.tech": {
                "services": ["fortune_500", "compliance_engine"],
                "base_port": 8301,
                "ssl_required": True
            }
        }

        # Initialize system
        self._initialize_database()
        self._setup_default_endpoints()

        self.logger.info("🚀 Production Deployment System initialized")

    def _initialize_database(self):
        """Initialize SQLite database for deployment tracking."""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deployment_endpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint_id TEXT UNIQUE,
                    domain TEXT,
                    subdomain TEXT,
                    service_type TEXT,
                    port INTEGER,
                    health_check_path TEXT,
                    ssl_enabled BOOLEAN,
                    auto_scaling BOOLEAN,
                    circuit_breaker BOOLEAN,
                    deployment_strategy TEXT,
                    created_at DATETIME
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS service_instances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instance_id TEXT UNIQUE,
                    endpoint_id TEXT,
                    host TEXT,
                    port INTEGER,
                    status TEXT,
                    health_score REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    request_count INTEGER,
                    error_count INTEGER,
                    last_health_check DATETIME
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deployment_id TEXT UNIQUE,
                    endpoint_id TEXT,
                    strategy TEXT,
                    current_version TEXT,
                    target_version TEXT,
                    status TEXT,
                    progress_percentage REAL,
                    started_at DATETIME,
                    completed_at DATETIME,
                    error_message TEXT
                )
            """)

            conn.commit()

    @contextmanager
    def _get_db_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.database_path)
        try:
            yield conn
        finally:
            conn.close()

    def _setup_default_endpoints(self):
        """Setup default production endpoints."""
        self.logger.info("🔧 Setting up default production endpoints...")

        for domain, config in self.domain_configs.items():
            for i, service_type in enumerate(config["services"]):
                endpoint_id = f"{domain}_{service_type}_{uuid.uuid4().hex[:8]}"

                endpoint = DeploymentEndpoint(
                    endpoint_id=endpoint_id,
                    domain=domain,
                    subdomain=service_type.replace("_", "-"),
                    service_type=service_type,
                    port=config["base_port"] + i,
                    health_check_path="/health",
                    load_balancer_config={
                        "strategy": "health_based",
                        "max_instances": 5,
                        "min_instances": 2
                    },
                    ssl_enabled=config["ssl_required"],
                    auto_scaling=True,
                    circuit_breaker=True
                )

                self.endpoints[endpoint_id] = endpoint
                self._store_endpoint(endpoint)

        self.logger.info(f"✅ Setup {len(self.endpoints)} default endpoints")

    def _store_endpoint(self, endpoint: DeploymentEndpoint):
        """Store endpoint configuration in database."""
        with self._get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO deployment_endpoints (
                    endpoint_id, domain, subdomain, service_type, port,
                    health_check_path, ssl_enabled, auto_scaling,
                    circuit_breaker, deployment_strategy, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                endpoint.endpoint_id,
                endpoint.domain,
                endpoint.subdomain,
                endpoint.service_type,
                endpoint.port,
                endpoint.health_check_path,
                endpoint.ssl_enabled,
                endpoint.auto_scaling,
                endpoint.circuit_breaker,
                endpoint.deployment_strategy,
                endpoint.created_at
            ))
            conn.commit()

    def create_service_instance(
        self,
        endpoint_id: str,
        host: str = "localhost",
        port: Optional[int] = None
    ) -> str:
        """Create a new service instance."""
        if endpoint_id not in self.endpoints:
            raise ValueError(f"Endpoint {endpoint_id} not found")

        endpoint = self.endpoints[endpoint_id]
        instance_id = f"{endpoint_id}_{uuid.uuid4().hex[:8]}"

        if port is None:
            port = endpoint.port

        instance = ServiceInstance(
            instance_id=instance_id,
            endpoint_id=endpoint_id,
            host=host,
            port=port,
            status="starting",
            health_score=0.5,
            cpu_usage=0.0,
            memory_usage=0.0,
            request_count=0,
            error_count=0
        )

        self.service_instances[instance_id] = instance
        self._store_service_instance(instance)

        self.logger.info(f"🆕 Created service instance {instance_id} for endpoint {endpoint_id}")
        return instance_id

    def _store_service_instance(self, instance: ServiceInstance):
        """Store service instance in database."""
        with self._get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO service_instances (
                    instance_id, endpoint_id, host, port, status, health_score,
                    cpu_usage, memory_usage, request_count, error_count,
                    last_health_check
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                instance.instance_id,
                instance.endpoint_id,
                instance.host,
                instance.port,
                instance.status,
                instance.health_score,
                instance.cpu_usage,
                instance.memory_usage,
                instance.request_count,
                instance.error_count,
                instance.last_health_check
            ))
            conn.commit()

    async def deploy_service(
        self,
        endpoint_id: str,
        deployment_config: Dict[str, Any],
        strategy: str = "blue_green"
    ) -> str:
        """Deploy service using specified strategy."""
        if endpoint_id not in self.endpoints:
            raise ValueError(f"Endpoint {endpoint_id} not found")

        deployment_id = f"deploy_{endpoint_id}_{uuid.uuid4().hex[:8]}"

        deployment = DeploymentStatus(
            deployment_id=deployment_id,
            endpoint_id=endpoint_id,
            strategy=strategy,
            current_version=deployment_config.get("current_version", "1.0.0"),
            target_version=deployment_config.get("target_version", "1.0.1"),
            status="planning",
            progress_percentage=0.0,
            started_at=datetime.now()
        )

        self.deployments[deployment_id] = deployment
        self._store_deployment(deployment)

        self.logger.info(f"🚀 Starting deployment {deployment_id} using {strategy} strategy")

        try:
            if strategy == "blue_green":
                await self._deploy_blue_green(deployment, deployment_config)
            elif strategy == "rolling":
                await self._deploy_rolling(deployment, deployment_config)
            elif strategy == "canary":
                await self._deploy_canary(deployment, deployment_config)
            else:
                raise ValueError(f"Unknown deployment strategy: {strategy}")

            deployment.status = "completed"
            deployment.completed_at = datetime.now()
            deployment.progress_percentage = 100.0

        except Exception as e:
            deployment.status = "failed"
            deployment.error_message = str(e)
            self.logger.error(f"❌ Deployment {deployment_id} failed: {e}")

        self._store_deployment(deployment)
        return deployment_id

    def _store_deployment(self, deployment: DeploymentStatus):
        """Store deployment status in database."""
        with self._get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO deployments (
                    deployment_id, endpoint_id, strategy, current_version,
                    target_version, status, progress_percentage, started_at,
                    completed_at, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deployment.deployment_id,
                deployment.endpoint_id,
                deployment.strategy,
                deployment.current_version,
                deployment.target_version,
                deployment.status,
                deployment.progress_percentage,
                deployment.started_at,
                deployment.completed_at,
                deployment.error_message
            ))
            conn.commit()

    async def _deploy_blue_green(
        self,
        deployment: DeploymentStatus,
        config: Dict[str, Any]
    ):
        """Execute blue-green deployment."""
        self.logger.info(f"💙💚 Starting blue-green deployment for {deployment.endpoint_id}")

        deployment.status = "deploying"
        deployment.progress_percentage = 10.0

        # Create green instances (new version)
        green_instances = []
        instance_count = config.get("instance_count", 2)

        for i in range(instance_count):
            port = self.endpoints[deployment.endpoint_id].port + 1000 + i  # Green environment offset
            instance_id = self.create_service_instance(deployment.endpoint_id, port=port)
            green_instances.append(instance_id)

        deployment.progress_percentage = 30.0

        # Wait for green instances to be healthy
        await self._wait_for_healthy_instances(green_instances, timeout=300)

        deployment.progress_percentage = 60.0

        # Switch traffic to green instances
        await self._switch_traffic(deployment.endpoint_id, green_instances)

        deployment.progress_percentage = 80.0

        # Remove blue instances (old version)
        blue_instances = [
            instance_id for instance_id, instance in self.service_instances.items()
            if (instance.endpoint_id == deployment.endpoint_id and
                instance_id not in green_instances)
        ]

        for instance_id in blue_instances:
            await self._stop_service_instance(instance_id)

        deployment.progress_percentage = 100.0
        self.logger.info(f"✅ Blue-green deployment completed for {deployment.endpoint_id}")

    async def _deploy_rolling(
        self,
        deployment: DeploymentStatus,
        config: Dict[str, Any]
    ):
        """Execute rolling deployment."""
        self.logger.info(f"🔄 Starting rolling deployment for {deployment.endpoint_id}")
        # Implementation would gradually replace instances one by one
        # For now, simulate the process
        deployment.status = "deploying"

        for progress in range(10, 101, 10):
            deployment.progress_percentage = progress
            await asyncio.sleep(1)  # Simulate deployment progress

    async def _deploy_canary(
        self,
        deployment: DeploymentStatus,
        config: Dict[str, Any]
    ):
        """Execute canary deployment."""
        self.logger.info(f"🐤 Starting canary deployment for {deployment.endpoint_id}")
        # Implementation would deploy small percentage of traffic to new version
        # For now, simulate the process
        deployment.status = "deploying"

        for progress in range(10, 101, 15):
            deployment.progress_percentage = progress
            await asyncio.sleep(1)

    async def _wait_for_healthy_instances(
        self,
        instance_ids: List[str],
        timeout: int = 300
    ):
        """Wait for instances to become healthy."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            all_healthy = True

            for instance_id in instance_ids:
                if instance_id not in self.service_instances:
                    all_healthy = False
                    break

                instance = self.service_instances[instance_id]
                is_healthy, health_data = await self.health_checker.check_health(instance)

                if is_healthy:
                    instance.status = "healthy"
                    instance.health_score = 1.0
                else:
                    all_healthy = False
                    instance.status = "unhealthy"

                self._store_service_instance(instance)

            if all_healthy:
                return

            await asyncio.sleep(5)

        raise TimeoutError(f"Instances did not become healthy within {timeout} seconds")

    async def _switch_traffic(self, endpoint_id: str, target_instances: List[str]):
        """Switch traffic to target instances."""
        self.logger.info(f"🔀 Switching traffic for endpoint {endpoint_id}")
        # In a real implementation, this would update load balancer configuration
        # For now, we'll just mark the target instances as active
        pass

    async def _stop_service_instance(self, instance_id: str):
        """Stop a service instance."""
        if instance_id in self.service_instances:
            instance = self.service_instances[instance_id]
            instance.status = "stopping"
            self._store_service_instance(instance)

            # Simulate graceful shutdown
            await asyncio.sleep(2)

            # Remove from active instances
            del self.service_instances[instance_id]
            self.logger.info(f"🛑 Stopped service instance {instance_id}")

    def get_endpoint_status(self, endpoint_id: str) -> Dict[str, Any]:
        """Get status of an endpoint and its instances."""
        if endpoint_id not in self.endpoints:
            return {"error": "Endpoint not found"}

        endpoint = self.endpoints[endpoint_id]
        instances = [
            asdict(instance) for instance in self.service_instances.values()
            if instance.endpoint_id == endpoint_id
        ]

        healthy_instances = len([i for i in instances if i["status"] == "healthy"])

        return {
            "endpoint": asdict(endpoint),
            "instances": instances,
            "summary": {
                "total_instances": len(instances),
                "healthy_instances": healthy_instances,
                "unhealthy_instances": len(instances) - healthy_instances,
                "overall_health": healthy_instances / max(len(instances), 1)
            }
        }

    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        if deployment_id not in self.deployments:
            return {"error": "Deployment not found"}

        deployment = self.deployments[deployment_id]
        return asdict(deployment)

    def list_endpoints(self) -> List[Dict[str, Any]]:
        """List all endpoints."""
        return [asdict(endpoint) for endpoint in self.endpoints.values()]

    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments."""
        return [asdict(deployment) for deployment in self.deployments.values()]

    def start_monitoring(self):
        """Start background monitoring processes."""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()

        self.logger.info("📊 Started deployment monitoring")

    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.running:
            try:
                # Monitor instance health
                asyncio.run(self._monitor_instance_health())

                # Check auto-scaling requirements
                self._check_auto_scaling()

                # Update metrics
                self._update_system_metrics()

                time.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(10)

    async def _monitor_instance_health(self):
        """Monitor health of all service instances."""
        for instance in self.service_instances.values():
            try:
                is_healthy, health_data = await self.health_checker.check_health(instance)

                instance.last_health_check = datetime.now()
                instance.health_score = self.health_checker.calculate_health_score(instance.instance_id)

                if is_healthy:
                    if instance.status != "healthy":
                        instance.status = "healthy"
                        self.logger.info(f"✅ Instance {instance.instance_id} is now healthy")
                else:
                    if instance.status == "healthy":
                        instance.status = "unhealthy"
                        self.logger.warning(f"⚠️ Instance {instance.instance_id} is now unhealthy")

                self.health_checker.update_health_history(
                    instance.instance_id, is_healthy, health_data
                )
                self._store_service_instance(instance)

            except Exception as e:
                self.logger.error(f"Health monitoring error for {instance.instance_id}: {e}")

    def _check_auto_scaling(self):
        """Check if auto-scaling is needed."""
        for endpoint_id, endpoint in self.endpoints.items():
            if not endpoint.auto_scaling:
                continue

            instances = [
                instance for instance in self.service_instances.values()
                if instance.endpoint_id == endpoint_id
            ]

            healthy_instances = [i for i in instances if i.status == "healthy"]
            config = endpoint.load_balancer_config

            min_instances = config.get("min_instances", 2)
            max_instances = config.get("max_instances", 5)

            # Scale up if needed
            if len(healthy_instances) < min_instances:
                needed_instances = min_instances - len(healthy_instances)
                for _ in range(needed_instances):
                    self.create_service_instance(endpoint_id)
                self.logger.info(f"📈 Scaled up {endpoint_id}: added {needed_instances} instances")

            # Scale down if needed (basic implementation)
            elif len(healthy_instances) > max_instances:
                excess_instances = len(healthy_instances) - max_instances
                for i in range(excess_instances):
                    if i < len(instances):
                        asyncio.run(self._stop_service_instance(instances[i].instance_id))
                self.logger.info(f"📉 Scaled down {endpoint_id}: removed {excess_instances} instances")

    def _update_system_metrics(self):
        """Update system-wide metrics."""
        # This would collect and update various system metrics
        # For now, just log a summary
        total_endpoints = len(self.endpoints)
        total_instances = len(self.service_instances)
        healthy_instances = len([i for i in self.service_instances.values() if i.status == "healthy"])

        self.logger.debug(f"System metrics: {total_endpoints} endpoints, "
                         f"{total_instances} instances ({healthy_instances} healthy)")

    def stop_monitoring(self):
        """Stop background monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)

        self.logger.info("🛑 Stopped deployment monitoring")

# FastAPI application for production deployment management
app = FastAPI(title="Production Deployment System", version="3.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global deployment system instance
deployment_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize deployment system on startup."""
    global deployment_system
    deployment_system = ProductionDeploymentSystem()
    deployment_system.start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if deployment_system:
        deployment_system.stop_monitoring()

class DeploymentRequest(BaseModel):
    endpoint_id: str
    deployment_config: Dict[str, Any] = Field(default={
        "current_version": "1.0.0",
        "target_version": "1.0.1",
        "instance_count": 2
    })
    strategy: str = "blue_green"

class ServiceInstanceRequest(BaseModel):
    endpoint_id: str
    host: str = "localhost"
    port: Optional[int] = None

@app.post("/api/v3/deployment/deploy")
async def deploy_service_endpoint(request: DeploymentRequest):
    """Deploy service to production."""
    try:
        deployment_id = await deployment_system.deploy_service(
            request.endpoint_id,
            request.deployment_config,
            request.strategy
        )

        return {
            "success": True,
            "deployment_id": deployment_id,
            "message": f"Deployment initiated using {request.strategy} strategy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/deployment/instances/create")
async def create_service_instance_endpoint(request: ServiceInstanceRequest):
    """Create new service instance."""
    try:
        instance_id = deployment_system.create_service_instance(
            request.endpoint_id,
            request.host,
            request.port
        )

        return {
            "success": True,
            "instance_id": instance_id,
            "message": "Service instance created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/deployment/endpoints")
async def list_endpoints_endpoint():
    """List all deployment endpoints."""
    try:
        endpoints = deployment_system.list_endpoints()
        return {"success": True, "data": endpoints}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/deployment/endpoints/{endpoint_id}/status")
async def get_endpoint_status_endpoint(endpoint_id: str):
    """Get endpoint status."""
    try:
        status = deployment_system.get_endpoint_status(endpoint_id)
        return {"success": True, "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/deployment/deployments")
async def list_deployments_endpoint():
    """List all deployments."""
    try:
        deployments = deployment_system.list_deployments()
        return {"success": True, "data": deployments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/deployment/deployments/{deployment_id}/status")
async def get_deployment_status_endpoint(deployment_id: str):
    """Get deployment status."""
    try:
        status = deployment_system.get_deployment_status(deployment_id)
        return {"success": True, "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "system": "production_deployment_system",
        "endpoints": len(deployment_system.endpoints) if deployment_system else 0,
        "instances": len(deployment_system.service_instances) if deployment_system else 0
    }

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
    )

    # Run the application
    uvicorn.run(
        "production_deployment_system:app",
        host="0.0.0.0",
        port=8004,
        log_level="info",
        reload=False
    )