#!/usr/bin/env python3
"""
DKG v3 Standalone Service
========================
FastAPI service running on port 8001 providing access to the U-DKG v3.0 Intelligence System
Integrates with the main AIA backend on port 8000 for intelligent knowledge processing.
"""

import asyncio
import os
import logging
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import the DKG v3 intelligence system
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from analytics.udkg_v3_intelligence_system import (
    UDKG_V3_IntelligenceSystem,
    initialize_udkg_v3_system,
    get_udkg_v3_system,
    generate_intelligence_insights,
    analyze_fortune500_opportunities,
    create_immersive_3d_visualization
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class IntelligenceQuery(BaseModel):
    context: str = Field(..., description="Query context for intelligence analysis")
    analysis_type: Optional[str] = Field("general", description="Type of analysis: general, business, technical, fortune500")
    include_3d: bool = Field(False, description="Include 3D visualization data")

class DKGHealthResponse(BaseModel):
    status: str
    version: str
    knowledge_atoms_loaded: int
    system_ready: bool
    gpu_acceleration: bool

class IntelligenceResponse(BaseModel):
    insights: List[Dict[str, Any]]
    confidence: float
    processing_time: float
    visualization_data: Optional[Dict[str, Any]] = None

# Global DKG system instance
dkg_system: Optional[UDKG_V3_IntelligenceSystem] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global dkg_system

    # Startup
    logger.info("🚀 Starting DKG v3 Service on port 8001")

    # Initialize the DKG v3 system
    knowledge_graph_path = os.getenv(
        "KNOWLEDGE_GRAPH_PATH",
        "/Users/wXy/dev/Projects/aia/aia_knowledge_graph_v2_1759313796.json"
    )

    try:
        dkg_system = await initialize_udkg_v3_system(knowledge_graph_path)
        logger.info("✅ DKG v3 Intelligence System initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize DKG v3 system: {e}")
        raise

    yield

    # Shutdown
    logger.info("🔄 Shutting down DKG v3 Service")
    if dkg_system:
        # Cleanup resources if needed
        pass

# Create FastAPI app with lifespan management
app = FastAPI(
    title="AIA DKG v3 Intelligence Service",
    description="Advanced Knowledge Graph Intelligence System v3.0",
    version="3.0.0",
    lifespan=lifespan
)

# Configure CORS for backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_dkg_system():
    """Dependency to get DKG system instance"""
    if dkg_system is None:
        raise HTTPException(status_code=503, detail="DKG v3 system not initialized")
    return dkg_system

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AIA DKG v3 Intelligence Service",
        "version": "3.0.0",
        "status": "operational",
        "port": 8001
    }

@app.get("/health", response_model=DKGHealthResponse)
async def health_check(system: UDKG_V3_IntelligenceSystem = Depends(get_dkg_system)):
    """Health check endpoint"""
    try:
        # Get system statistics
        stats = await system.get_system_statistics()

        return DKGHealthResponse(
            status="healthy",
            version="3.0.0",
            knowledge_atoms_loaded=stats.get("knowledge_atoms_count", 0),
            system_ready=True,
            gpu_acceleration=stats.get("gpu_enabled", False)
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/intelligence/query", response_model=IntelligenceResponse)
async def query_intelligence(
    query: IntelligenceQuery,
    background_tasks: BackgroundTasks,
    system: UDKG_V3_IntelligenceSystem = Depends(get_dkg_system)
):
    """Query the DKG v3 intelligence system"""
    try:
        import time
        start_time = time.time()

        # Generate intelligence insights
        insights = await generate_intelligence_insights(query.context)

        # Include 3D visualization if requested
        visualization_data = None
        if query.include_3d:
            visualization_data = await create_immersive_3d_visualization()

        processing_time = time.time() - start_time

        # Calculate overall confidence
        if insights:
            avg_confidence = sum(insight.confidence for insight in insights) / len(insights)
        else:
            avg_confidence = 0.0

        return IntelligenceResponse(
            insights=[{
                "type": insight.insight_type,
                "confidence": insight.confidence,
                "business_value": insight.business_value,
                "description": insight.description,
                "actionable_steps": insight.actionable_steps,
                "fortune500_relevance": insight.fortune500_relevance
            } for insight in insights],
            confidence=avg_confidence,
            processing_time=processing_time,
            visualization_data=visualization_data
        )

    except Exception as e:
        logger.error(f"Intelligence query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Intelligence query failed: {str(e)}")

@app.get("/intelligence/fortune500")
async def analyze_fortune500(system: UDKG_V3_IntelligenceSystem = Depends(get_dkg_system)):
    """Analyze Fortune 500 business opportunities"""
    try:
        opportunities = await analyze_fortune500_opportunities()

        return {
            "opportunities": [{
                "id": opp.opportunity_id,
                "market_size": opp.market_size,
                "confidence": opp.confidence,
                "timeline": opp.timeline,
                "investment_required": opp.investment_required,
                "expected_roi": opp.expected_roi,
                "key_technologies": opp.key_technologies,
                "target_fortune500": opp.target_fortune500,
                "risk_factors": opp.risk_factors
            } for opp in opportunities],
            "total_opportunities": len(opportunities),
            "analysis_timestamp": "2024-12-08T12:00:00Z"
        }

    except Exception as e:
        logger.error(f"Fortune 500 analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Fortune 500 analysis failed: {str(e)}")

@app.get("/intelligence/3d-visualization")
async def get_3d_visualization(system: UDKG_V3_IntelligenceSystem = Depends(get_dkg_system)):
    """Get 3D visualization data"""
    try:
        visualization_data = await create_immersive_3d_visualization()
        return {
            "visualization_data": visualization_data,
            "rendering_type": "three_js",
            "timestamp": "2024-12-08T12:00:00Z"
        }

    except Exception as e:
        logger.error(f"3D visualization generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"3D visualization failed: {str(e)}")

@app.get("/system/status")
async def system_status(system: UDKG_V3_IntelligenceSystem = Depends(get_dkg_system)):
    """Get detailed system status"""
    try:
        stats = await system.get_system_statistics()

        return {
            "service_name": "DKG v3 Intelligence Service",
            "version": "3.0.0",
            "port": 8001,
            "status": "operational",
            "statistics": stats,
            "endpoints": {
                "health": "/health",
                "intelligence_query": "/intelligence/query",
                "fortune500_analysis": "/intelligence/fortune500",
                "3d_visualization": "/intelligence/3d-visualization",
                "system_status": "/system/status"
            }
        }

    except Exception as e:
        logger.error(f"System status failed: {e}")
        raise HTTPException(status_code=500, detail=f"System status failed: {str(e)}")

if __name__ == "__main__":
    # Configuration
    host = os.getenv("DKG_HOST", "0.0.0.0")
    port = int(os.getenv("DKG_PORT", 8001))
    workers = int(os.getenv("DKG_WORKERS", 1))

    logger.info(f"🚀 Starting DKG v3 Service on {host}:{port}")

    # Run the service
    uvicorn.run(
        "aia.services.dkg_v3_service:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        log_level="info"
    )