"""
AIA Enterprise Platform - API Routes Module
==========================================

Consolidated API routing system that merges all scattered endpoints
into a unified, well-organized structure.
"""

from aia.aia-enterprise-platform.core.backend.api.routes.health import router as health_router
from aia.aia-enterprise-platform.core.backend.api.routes.auth import router as auth_router
from aia.aia-enterprise-platform.core.backend.api.routes.knowledge import router as knowledge_router
from aia.aia-enterprise-platform.core.backend.api.routes.ai_engine import router as ai_router
from aia.aia-enterprise-platform.core.backend.api.routes.analytics import router as analytics_router
from aia.aia-enterprise-platform.core.backend.api.routes.enterprise import router as enterprise_router
from aia.aia-enterprise-platform.core.backend.api.routes.payments import router as payment_router

__all__ = [
    "health_router",
    "auth_router",
    "knowledge_router",
    "ai_router",
    "analytics_router",
    "enterprise_router",
    "payment_router"
]