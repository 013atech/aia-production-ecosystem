"""
AIA Enterprise Platform - Unified Core Backend
==============================================

This consolidated backend merges all scattered API implementations into a single,
production-ready FastAPI application with enterprise-grade security and performance.

Architecture:
- Unified FastAPI application with modular routing
- Production-grade security with JWT authentication
- Knowledge graph integration with ML processing
- Circuit breaker pattern for resilience
- Comprehensive monitoring and observability
- Enterprise service integrations
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Internal imports
from aia.aia-enterprise-platform.core.backend.config.settings import Settings
from aia.aia-enterprise-platform.core.backend.core.security import SecurityManager
from aia.aia-enterprise-platform.core.backend.core.circuit_breaker import CircuitBreakerManager
from aia.aia-enterprise-platform.core.backend.models.schemas import *
from aia.aia-enterprise-platform.core.backend.services.knowledge_graph import KnowledgeGraphService
from aia.aia-enterprise-platform.core.backend.services.ai_engine import AIEngineService
from aia.aia-enterprise-platform.core.backend.services.analytics import AnalyticsService
from aia.aia-enterprise-platform.core.backend.services.enterprise import EnterpriseService
from aia.aia-enterprise-platform.core.backend.api.routes import (
    health_router,
    auth_router,
    knowledge_router,
    ai_router,
    analytics_router,
    enterprise_router,
    payment_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global settings and state
settings = Settings()
security_manager = SecurityManager()
circuit_breaker_manager = CircuitBreakerManager()
executor = ThreadPoolExecutor(max_workers=20)

# Application state
app_state = {
    "initialized": False,
    "redis_client": None,
    "knowledge_graph_service": None,
    "ai_engine_service": None,
    "analytics_service": None,
    "enterprise_service": None,
    "circuit_breakers": {},
    "health_status": "starting",
    "performance_metrics": {
        "total_requests": 0,
        "average_response_time": 0.0,
        "error_rate": 0.0
    }
}

# Performance monitoring middleware
@asynccontextmanager
async def performance_monitor():
    """Context manager for request performance monitoring"""
    start_time = asyncio.get_event_loop().time()
    try:
        yield
        end_time = asyncio.get_event_loop().time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Update performance metrics
        app_state["performance_metrics"]["total_requests"] += 1
        current_avg = app_state["performance_metrics"]["average_response_time"]
        total_requests = app_state["performance_metrics"]["total_requests"]

        # Calculate rolling average
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        app_state["performance_metrics"]["average_response_time"] = new_avg

        # Log slow requests (>100ms target)
        if response_time > 100:
            logger.warning(f"Slow request detected: {response_time:.2f}ms")

    except Exception as e:
        app_state["performance_metrics"]["error_rate"] += 1
        logger.error(f"Request processing error: {e}")
        raise

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown with comprehensive initialization"""
    logger.info("🚀 Starting AIA Enterprise Platform Core Backend...")

    try:
        # Initialize security components
        await security_manager.initialize()
        logger.info("🛡️ Security manager initialized")

        # Initialize Redis connection
        redis_url = settings.redis_url
        app_state["redis_client"] = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20
        )
        await app_state["redis_client"].ping()
        logger.info("📊 Redis connection established")

        # Initialize circuit breakers
        app_state["circuit_breakers"] = circuit_breaker_manager.initialize_breakers([
            "knowledge_graph", "ai_engine", "analytics", "enterprise", "auth"
        ])
        logger.info("🔧 Circuit breakers initialized")

        # Initialize core services
        app_state["knowledge_graph_service"] = KnowledgeGraphService(
            app_state["redis_client"],
            circuit_breaker=app_state["circuit_breakers"]["knowledge_graph"]
        )
        await app_state["knowledge_graph_service"].initialize()
        logger.info("🧠 Knowledge Graph service initialized")

        app_state["ai_engine_service"] = AIEngineService(
            circuit_breaker=app_state["circuit_breakers"]["ai_engine"]
        )
        await app_state["ai_engine_service"].initialize()
        logger.info("🤖 AI Engine service initialized")

        app_state["analytics_service"] = AnalyticsService(
            app_state["redis_client"],
            circuit_breaker=app_state["circuit_breakers"]["analytics"]
        )
        await app_state["analytics_service"].initialize()
        logger.info("📈 Analytics service initialized")

        app_state["enterprise_service"] = EnterpriseService(
            circuit_breaker=app_state["circuit_breakers"]["enterprise"]
        )
        await app_state["enterprise_service"].initialize()
        logger.info("🏢 Enterprise service initialized")

        # Load knowledge graph
        knowledge_graph_path = settings.knowledge_graph_path
        if knowledge_graph_path and os.path.exists(knowledge_graph_path):
            await app_state["knowledge_graph_service"].load_knowledge_graph(knowledge_graph_path)
            logger.info(f"📚 Knowledge graph loaded from {knowledge_graph_path}")

        app_state["initialized"] = True
        app_state["health_status"] = "healthy"
        logger.info("✅ AIA Enterprise Platform Core Backend ready!")

    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        app_state["health_status"] = "unhealthy"
        app_state["initialized"] = False

    yield

    # Cleanup
    logger.info("🛑 Shutting down AIA Enterprise Platform Core Backend...")
    if app_state["redis_client"]:
        await app_state["redis_client"].close()
    executor.shutdown(wait=True)
    logger.info("✅ Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="AIA Enterprise Platform - Core Backend",
    version="4.0.0",
    description="Unified, production-ready backend for the AIA Enterprise Platform",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,  # Disable in production
    redoc_url="/redoc" if settings.debug else None
)

# Security middleware
security = HTTPBearer(auto_error=False)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token for protected endpoints"""
    if not credentials:
        return None

    try:
        payload = security_manager.verify_token(credentials.credentials)
        return payload
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None

# CORS configuration with security considerations
allowed_origins = [
    "https://013a.tech",
    "https://www.013a.tech",
]

if settings.debug:
    allowed_origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Accept", "Accept-Language", "Content-Language", "Content-Type", "Authorization", "X-Requested-With", "X-API-Key"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining", "X-Response-Time"]
)

# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Monitor request performance and add response headers"""
    async with performance_monitor():
        start_time = asyncio.get_event_loop().time()

        response = await call_next(request)

        end_time = asyncio.get_event_loop().time()
        response_time = (end_time - start_time) * 1000

        # Add performance headers
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        response.headers["X-Request-ID"] = f"req_{int(start_time * 1000)}"

        return response

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response

# Include API routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(knowledge_router, prefix="/api/v1", tags=["Knowledge Graph"])
app.include_router(ai_router, prefix="/api/v1", tags=["AI Engine"])
app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])
app.include_router(enterprise_router, prefix="/api/v1", tags=["Enterprise"])
app.include_router(payment_router, prefix="/api/v1", tags=["Payments"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AIA Enterprise Platform - Core Backend",
        "version": "4.0.0",
        "status": app_state["health_status"],
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "unified_backend": True,
            "production_security": True,
            "knowledge_graph": bool(app_state.get("knowledge_graph_service")),
            "ai_engine": bool(app_state.get("ai_engine_service")),
            "analytics": bool(app_state.get("analytics_service")),
            "enterprise_services": bool(app_state.get("enterprise_service"))
        }
    }

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with detailed error responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with logging"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

# Performance metrics endpoint
@app.get("/api/v1/metrics/performance")
async def get_performance_metrics(current_user: dict = Depends(verify_token)):
    """Get real-time performance metrics"""
    if not current_user and not settings.debug:
        raise HTTPException(status_code=401, detail="Authentication required")

    return {
        "performance_metrics": app_state["performance_metrics"],
        "circuit_breaker_status": {
            name: {
                "state": breaker.state,
                "failure_count": breaker.failure_count,
                "last_failure": breaker.last_failure_time
            } for name, breaker in app_state["circuit_breakers"].items()
        },
        "system_health": app_state["health_status"],
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.debug,
        workers=1 if settings.debug else 4,
        log_level="info"
    )