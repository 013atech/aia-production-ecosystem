#!/usr/bin/env python3
"""
AIA Atomic DKG API Endpoints
============================
Enhanced API endpoints for atomic DKG integration with AIA backend
Designed for seamless hot-swap integration without service interruption

New Endpoints:
- /api/atomic-dkg/search/{query} - Semantic search across atoms
- /api/atomic-dkg/navigate/{atom_id} - Navigate relationships
- /api/atomic-dkg/context/{topic} - Get comprehensive context
- /api/atomic-dkg/evolution/{topic} - Track thought evolution
- /api/atomic-dkg/stats - Integration statistics
- /api/atomic-dkg/priority/{level} - Priority-filtered queries
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
import asyncio
from pydantic import BaseModel

from aia_atomic_dkg_integration_service import AtomicDKGIntegrationServer

# Configure logging
logger = logging.getLogger(__name__)

# Global integration server instance
integration_server: Optional[AtomicDKGIntegrationServer] = None

class QueryRequest(BaseModel):
    query: str
    agent_type: Optional[str] = "technical"
    priority_filter: Optional[float] = None
    limit: Optional[int] = 50

class NavigationRequest(BaseModel):
    atom_id: str
    depth: Optional[int] = 2
    include_relationships: Optional[bool] = True

class EnhancedQueryResponse(BaseModel):
    status: str
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    processing_time: float

async def initialize_atomic_dkg_endpoints():
    """Initialize atomic DKG endpoints for AIA backend"""
    global integration_server

    try:
        logger.info("🧬 Initializing atomic DKG API endpoints")

        # Create integration server
        integration_server = AtomicDKGIntegrationServer()

        # Start integration
        success = await integration_server.start_integration()

        if success:
            logger.info("✅ Atomic DKG API endpoints ready")
            return True
        else:
            logger.error("❌ Atomic DKG initialization failed")
            return False

    except Exception as e:
        logger.error(f"❌ Endpoint initialization failed: {e}")
        return False

# FastAPI route definitions for AIA backend integration
async def atomic_dkg_search(
    query: str = Path(..., description="Search query for atomic DKG"),
    agent_type: str = Query("technical", description="Agent type for priority filtering"),
    priority_filter: Optional[float] = Query(None, description="Minimum priority weight filter"),
    limit: int = Query(50, description="Maximum results to return")
) -> JSONResponse:
    """Semantic search across atomic DKG knowledge atoms"""
    if not integration_server or not integration_server.query_engine.loaded:
        raise HTTPException(status_code=503, detail="Atomic DKG not initialized")

    try:
        start_time = time.time()

        # Enhanced semantic search
        atoms = await integration_server.query_engine.query_semantic_search(
            query, limit=limit, priority_filter=priority_filter
        )

        # Format results for AIA backend
        results = []
        for atom in atoms:
            results.append({
                "atom_id": atom.id,
                "file_path": atom.file_path,
                "content_excerpt": atom.content_excerpt,
                "semantic_summary": atom.semantic_summary,
                "hierarchical_level": atom.hierarchical_level,
                "priority_weight": atom.priority_weight,
                "quality_score": atom.quality_score,
                "relationships_count": atom.relationships_count
            })

        processing_time = time.time() - start_time

        return JSONResponse({
            "status": "success",
            "query": query,
            "results": results,
            "metadata": {
                "total_results": len(results),
                "processing_time_ms": round(processing_time * 1000, 2),
                "agent_type": agent_type,
                "priority_filter": priority_filter,
                "gpu_accelerated": bool(integration_server.query_engine.embedding_model)
            }
        })

    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def atomic_dkg_navigate(
    atom_id: str = Path(..., description="Atom ID to navigate from"),
    depth: int = Query(2, description="Relationship traversal depth"),
    include_relationships: bool = Query(True, description="Include relationship metadata")
) -> JSONResponse:
    """Navigate atomic DKG relationships from a specific atom"""
    if not integration_server or not integration_server.query_engine.loaded:
        raise HTTPException(status_code=503, detail="Atomic DKG not initialized")

    try:
        start_time = time.time()

        # Get comprehensive context
        context = await integration_server.query_engine.get_atom_context(atom_id, depth)

        if not context:
            raise HTTPException(status_code=404, detail=f"Atom {atom_id} not found")

        # Format navigation response
        response = {
            "status": "success",
            "atom_id": atom_id,
            "primary_atom": {
                "id": context["primary_atom"].id,
                "file_path": context["primary_atom"].file_path,
                "content_excerpt": context["primary_atom"].content_excerpt,
                "hierarchical_level": context["primary_atom"].hierarchical_level,
                "priority_weight": context["primary_atom"].priority_weight,
                "quality_score": context["primary_atom"].quality_score
            },
            "navigation_context": {
                "related_atoms": len(context.get("related_atoms", [])),
                "context_quality": context.get("context_quality", 0),
                "priority_level": context.get("priority_level", 0),
                "total_relationships": context.get("total_relationships", 0)
            },
            "metadata": {
                "traversal_depth": depth,
                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                "include_relationships": include_relationships
            }
        }

        if include_relationships:
            response["related_atoms"] = [
                {
                    "atom_id": rel["atom"].id,
                    "relationship_type": rel["relationship"].get("type", "unknown"),
                    "relationship_strength": rel["relationship"].get("strength", 0),
                    "content_excerpt": rel["atom"].content_excerpt[:200]
                }
                for rel in context.get("related_atoms", [])[:10]
            ]

        return JSONResponse(response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Navigation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def atomic_dkg_context(
    topic: str = Path(..., description="Topic for comprehensive context"),
    agent_type: str = Query("technical", description="Agent type for context filtering")
) -> JSONResponse:
    """Get comprehensive context for a topic across atomic DKG"""
    if not integration_server or not integration_server.query_engine.loaded:
        raise HTTPException(status_code=503, detail="Atomic DKG not initialized")

    try:
        start_time = time.time()

        # Enhanced context assembly
        enhanced_context = await integration_server.query_engine.enhance_aia_query(topic, agent_type)

        return JSONResponse({
            "status": "success",
            "topic": topic,
            "enhanced_context": enhanced_context,
            "metadata": {
                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                "agent_type": agent_type,
                "context_source": "atomic_dkg_enhanced"
            }
        })

    except Exception as e:
        logger.error(f"❌ Context assembly failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def atomic_dkg_evolution(
    topic: str = Path(..., description="Topic for evolution tracking")
) -> JSONResponse:
    """Track thought evolution across thoughts_lately versions"""
    if not integration_server or not integration_server.query_engine.loaded:
        raise HTTPException(status_code=503, detail="Atomic DKG not initialized")

    try:
        start_time = time.time()

        # Track evolution
        evolution = await integration_server.query_engine.query_thoughts_evolution(topic)

        return JSONResponse({
            "status": "success",
            "topic": topic,
            "evolution_timeline": evolution,
            "metadata": {
                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                "evolution_tracking": "thoughts_lately_versions"
            }
        })

    except Exception as e:
        logger.error(f"❌ Evolution tracking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def atomic_dkg_stats() -> JSONResponse:
    """Get atomic DKG integration statistics"""
    if not integration_server:
        raise HTTPException(status_code=503, detail="Integration server not initialized")

    try:
        stats = await integration_server.query_engine.get_stats()
        return JSONResponse(stats)

    except Exception as e:
        logger.error(f"❌ Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def atomic_dkg_priority(
    level: float = Path(..., description="Minimum priority level"),
    limit: int = Query(100, description="Maximum results to return")
) -> JSONResponse:
    """Get atoms filtered by priority level"""
    if not integration_server or not integration_server.query_engine.loaded:
        raise HTTPException(status_code=503, detail="Atomic DKG not initialized")

    try:
        start_time = time.time()

        # Get priority-filtered atoms
        priority_atoms = []
        for weight, atom_ids in integration_server.query_engine.priority_index.items():
            if weight >= level:
                for atom_id in atom_ids[:limit]:
                    if atom_id in integration_server.query_engine.atoms:
                        atom = integration_server.query_engine.atoms[atom_id]
                        priority_atoms.append({
                            "atom_id": atom.id,
                            "file_path": atom.file_path,
                            "content_excerpt": atom.content_excerpt[:200],
                            "priority_weight": atom.priority_weight,
                            "quality_score": atom.quality_score,
                            "hierarchical_level": atom.hierarchical_level
                        })

        # Sort by priority weight
        priority_atoms.sort(key=lambda x: x["priority_weight"], reverse=True)

        return JSONResponse({
            "status": "success",
            "priority_level": level,
            "results": priority_atoms[:limit],
            "metadata": {
                "total_results": len(priority_atoms),
                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                "priority_filtering": "active"
            }
        })

    except Exception as e:
        logger.error(f"❌ Priority filtering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Route registration function for AIA backend
def register_atomic_dkg_routes(app: FastAPI):
    """Register atomic DKG routes with existing AIA FastAPI app"""

    app.add_api_route(
        "/api/atomic-dkg/search/{query}",
        atomic_dkg_search,
        methods=["GET"],
        response_model=None
    )

    app.add_api_route(
        "/api/atomic-dkg/navigate/{atom_id}",
        atomic_dkg_navigate,
        methods=["GET"],
        response_model=None
    )

    app.add_api_route(
        "/api/atomic-dkg/context/{topic}",
        atomic_dkg_context,
        methods=["GET"],
        response_model=None
    )

    app.add_api_route(
        "/api/atomic-dkg/evolution/{topic}",
        atomic_dkg_evolution,
        methods=["GET"],
        response_model=None
    )

    app.add_api_route(
        "/api/atomic-dkg/stats",
        atomic_dkg_stats,
        methods=["GET"],
        response_model=None
    )

    app.add_api_route(
        "/api/atomic-dkg/priority/{level}",
        atomic_dkg_priority,
        methods=["GET"],
        response_model=None
    )

# Startup function for integration
async def startup_atomic_dkg_integration():
    """Startup function for atomic DKG integration"""
    success = await initialize_atomic_dkg_endpoints()

    if success:
        logger.info("🚀 Atomic DKG API endpoints registered successfully")
    else:
        logger.error("❌ Atomic DKG endpoint registration failed")

if __name__ == "__main__":
    # Standalone testing
    asyncio.run(initialize_atomic_dkg_endpoints())