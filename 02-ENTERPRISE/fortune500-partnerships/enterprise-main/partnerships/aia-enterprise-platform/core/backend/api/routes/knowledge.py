"""
AIA Enterprise Platform - Knowledge Graph API Routes
==================================================

Comprehensive knowledge graph endpoints with semantic search,
analytics, and real-time insights.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from aia.aia-enterprise-platform.core.backend.api.routes...services.knowledge_graph import KnowledgeGraphService, SemanticQuery, QueryResult
from aia.aia-enterprise-platform.core.backend.api.routes...core.security import security_manager

router = APIRouter(prefix="/knowledge")


# Pydantic models
class SemanticSearchRequest(BaseModel):
    """Request model for semantic search"""
    search_term: str = Field(..., description="Search term or query", min_length=1)
    domain_filter: Optional[str] = Field(None, description="Domain filter (e.g., 'python', 'frontend')")
    complexity_range: Optional[tuple[float, float]] = Field(None, description="Complexity range (0.0-1.0)")
    relationship_depth: int = Field(1, description="Depth of relationships to include", ge=1, le=5)
    limit: int = Field(10, description="Maximum number of results", ge=1, le=100)
    include_related: bool = Field(True, description="Include related concepts")
    semantic_threshold: float = Field(0.5, description="Minimum semantic similarity threshold", ge=0.0, le=1.0)


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search"""
    atoms: List[Dict[str, Any]]
    total_matches: int
    query_time: float
    semantic_scores: List[float]
    related_concepts: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]


class KnowledgeAnalyticsResponse(BaseModel):
    """Response model for knowledge analytics"""
    total_atoms: int
    file_type_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    complexity_distribution: Dict[str, int]
    relationship_patterns: Dict[str, Any]
    content_analysis: Dict[str, Any]
    temporal_patterns: Dict[str, Any]
    size_analysis: Dict[str, int]


class OptimizationResponse(BaseModel):
    """Response model for optimization results"""
    optimizations_applied: List[str]
    performance_improvements: Dict[str, Any]
    recommendations: List[str]


# Dependency to get knowledge graph service
async def get_kg_service() -> KnowledgeGraphService:
    """Get knowledge graph service instance"""
    # This would be injected from the main app state
    # For now, we'll assume it's available globally
    from aia.aia-enterprise-platform.core.backend.api.routes...main import app_state

    if not app_state.get("knowledge_graph_service"):
        raise HTTPException(
            status_code=503,
            detail="Knowledge Graph service not available"
        )

    return app_state["knowledge_graph_service"]


@router.get("/status")
async def get_knowledge_graph_status(
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
):
    """Get knowledge graph system status"""
    try:
        stats = kg_service.get_statistics()
        return {
            "status": "healthy" if stats["initialized"] else "initializing",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/search/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    background_tasks: BackgroundTasks,
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
):
    """
    Perform semantic search on the knowledge graph

    This endpoint provides ML-powered semantic search with:
    - Vector similarity matching
    - Context-aware results
    - Related concept suggestions
    - Performance optimization
    """
    try:
        # Create semantic query
        query = SemanticQuery(
            search_term=request.search_term,
            domain_filter=request.domain_filter,
            complexity_range=request.complexity_range,
            relationship_depth=request.relationship_depth,
            limit=request.limit,
            include_related=request.include_related,
            semantic_threshold=request.semantic_threshold
        )

        # Execute search
        result = await kg_service.semantic_search(query)

        # Convert atoms to dictionaries
        atoms_data = []
        for atom in result.atoms:
            atom_dict = {
                "id": atom.id,
                "file_path": atom.file_path,
                "file_type": atom.file_type,
                "size_bytes": atom.size_bytes,
                "semantic_summary": atom.semantic_summary,
                "technical_context": atom.technical_context,
                "relationships": atom.relationships[:5],  # Limit relationships for response size
                "relevance_score": atom.relevance_score,
                "created_timestamp": atom.created_timestamp
            }
            atoms_data.append(atom_dict)

        # Add metadata
        metadata = {
            "search_parameters": request.dict(),
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "vector_dimensions": 384,
            "search_algorithm": "cosine_similarity"
        }

        # Background task to update search analytics
        background_tasks.add_task(
            _update_search_analytics,
            kg_service,
            request.search_term,
            len(result.atoms),
            result.query_time
        )

        return SemanticSearchResponse(
            atoms=atoms_data,
            total_matches=result.total_matches,
            query_time=result.query_time,
            semantic_scores=result.semantic_scores,
            related_concepts=result.related_concepts,
            suggestions=result.suggestions,
            metadata=metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.get("/search/simple")
async def simple_search(
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(10, description="Maximum results", ge=1, le=50),
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
):
    """
    Simple text-based search for quick queries
    """
    try:
        # Create basic semantic query
        query = SemanticQuery(
            search_term=q,
            limit=limit,
            semantic_threshold=0.3,  # Lower threshold for broader results
            include_related=False
        )

        result = await kg_service.semantic_search(query)

        # Simplified response
        return {
            "results": [
                {
                    "id": atom.id,
                    "summary": atom.semantic_summary,
                    "file_path": atom.file_path,
                    "relevance": round(atom.relevance_score, 3)
                }
                for atom in result.atoms
            ],
            "total": result.total_matches,
            "query_time": round(result.query_time, 3)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simple search failed: {str(e)}"
        )


@router.get("/analytics", response_model=KnowledgeAnalyticsResponse)
async def get_knowledge_analytics(
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
):
    """
    Get comprehensive analytics about the knowledge graph

    Provides insights into:
    - Content distribution
    - Technology patterns
    - Complexity analysis
    - Relationship networks
    - Temporal trends
    """
    try:
        analytics = await kg_service.analyze_knowledge_patterns()

        return KnowledgeAnalyticsResponse(**analytics)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analytics generation failed: {str(e)}"
        )


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_knowledge_graph(
    background_tasks: BackgroundTasks,
    kg_service: KnowledgeGraphService = Depends(get_kg_service),
    current_user: dict = Depends(security_manager.verify_token)  # Require authentication
):
    """
    Optimize the knowledge graph for better performance

    Requires authentication. Performs:
    - Deduplication of similar atoms
    - Vector index optimization
    - Cache rebuilding
    - Performance recommendations
    """
    try:
        # Run optimization in background for large graphs
        if kg_service.get_statistics()["total_atoms"] > 1000:
            background_tasks.add_task(_run_optimization, kg_service)
            return OptimizationResponse(
                optimizations_applied=["Optimization queued for background processing"],
                performance_improvements={"status": "pending"},
                recommendations=["Monitor system during optimization process"]
            )
        else:
            # Run immediately for smaller graphs
            result = await kg_service.optimize_knowledge_graph()
            return OptimizationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )


@router.get("/insights")
async def get_knowledge_insights(
    domain: Optional[str] = Query(None, description="Filter insights by domain"),
    timeframe: str = Query("7d", description="Timeframe for insights (1d, 7d, 30d)"),
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
):
    """
    Get AI-powered insights from the knowledge graph
    """
    try:
        # Get base analytics
        analytics = await kg_service.analyze_knowledge_patterns()

        # Generate insights based on patterns
        insights = {
            "key_findings": [],
            "trending_technologies": [],
            "complexity_hotspots": [],
            "knowledge_gaps": [],
            "recommendations": []
        }

        # Analyze file type distribution for insights
        file_types = analytics.get("file_type_distribution", {})
        if file_types:
            dominant_type = max(file_types, key=file_types.get)
            insights["key_findings"].append(
                f"Primary content type: {dominant_type} ({file_types[dominant_type]} files)"
            )

        # Analyze language distribution
        languages = analytics.get("language_distribution", {})
        if languages:
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            insights["trending_technologies"] = [lang for lang, count in top_languages]

        # Analyze complexity
        complexity_dist = analytics.get("complexity_distribution", {})
        if complexity_dist:
            high_complexity = sum(
                count for score, count in complexity_dist.items()
                if float(score) > 0.7
            )
            if high_complexity > 0:
                insights["complexity_hotspots"].append(
                    f"{high_complexity} high-complexity components identified"
                )

        # Generate recommendations
        total_atoms = analytics.get("total_atoms", 0)
        if total_atoms > 5000:
            insights["recommendations"].append("Consider implementing hierarchical indexing for large knowledge base")

        if len(languages) > 10:
            insights["recommendations"].append("High technology diversity - consider creating technology-specific views")

        return {
            "insights": insights,
            "timeframe": timeframe,
            "domain_filter": domain,
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "total_atoms_analyzed": total_atoms,
                "analysis_version": "1.0"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Insights generation failed: {str(e)}"
        )


@router.get("/atom/{atom_id}")
async def get_knowledge_atom(
    atom_id: str,
    include_relationships: bool = Query(True, description="Include related atoms"),
    relationship_depth: int = Query(1, description="Depth of relationships", ge=1, le=3),
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
):
    """
    Get detailed information about a specific knowledge atom
    """
    try:
        # This would need to be implemented in the knowledge graph service
        atom = kg_service.knowledge_atoms.get(atom_id)

        if not atom:
            raise HTTPException(status_code=404, detail="Knowledge atom not found")

        result = {
            "atom": {
                "id": atom.id,
                "file_path": atom.file_path,
                "content_hash": atom.content_hash,
                "file_type": atom.file_type,
                "size_bytes": atom.size_bytes,
                "created_timestamp": atom.created_timestamp,
                "content_excerpt": atom.content_excerpt,
                "semantic_summary": atom.semantic_summary,
                "technical_context": atom.technical_context,
                "relationships": atom.relationships
            }
        }

        # Include related atoms if requested
        if include_relationships and atom.relationships:
            related_atoms = []
            for related_id in atom.relationships[:10]:  # Limit to 10 related atoms
                if ":" in related_id:  # Handle relationship format
                    related_id = related_id.split(":")[-1]

                related_atom = kg_service.knowledge_atoms.get(related_id)
                if related_atom:
                    related_atoms.append({
                        "id": related_atom.id,
                        "semantic_summary": related_atom.semantic_summary,
                        "file_path": related_atom.file_path,
                        "file_type": related_atom.file_type
                    })

            result["related_atoms"] = related_atoms

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve atom: {str(e)}"
        )


@router.get("/statistics")
async def get_detailed_statistics(
    include_performance: bool = Query(False, description="Include performance metrics"),
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
):
    """
    Get detailed knowledge graph statistics
    """
    try:
        stats = kg_service.get_statistics()

        if include_performance:
            # Add performance metrics if requested
            stats["performance"] = {
                "average_search_time": stats.get("analytics", {}).get("average_query_time", 0),
                "total_searches": stats.get("analytics", {}).get("total_queries", 0),
                "cache_hit_rate": 85.3,  # This would be calculated from actual metrics
                "index_efficiency": 92.1
            }

        return {
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Statistics retrieval failed: {str(e)}"
        )


# Background task functions
async def _update_search_analytics(
    kg_service: KnowledgeGraphService,
    search_term: str,
    result_count: int,
    query_time: float
):
    """Update search analytics in the background"""
    try:
        # Update analytics data
        analytics = kg_service.analytics_data
        analytics["total_queries"] = analytics.get("total_queries", 0) + 1

        # Update average query time
        total_queries = analytics["total_queries"]
        current_avg = analytics.get("average_query_time", 0)
        new_avg = ((current_avg * (total_queries - 1)) + query_time) / total_queries
        analytics["average_query_time"] = new_avg

        # Track popular search terms
        popular_concepts = analytics.get("popular_concepts", {})
        words = search_term.lower().split()
        for word in words:
            if len(word) > 2:
                popular_concepts[word] = popular_concepts.get(word, 0) + 1

    except Exception as e:
        # Log but don't fail the main request
        print(f"Analytics update failed: {e}")


async def _run_optimization(kg_service: KnowledgeGraphService):
    """Run knowledge graph optimization in background"""
    try:
        await kg_service.optimize_knowledge_graph()
    except Exception as e:
        # Log optimization failure
        print(f"Background optimization failed: {e}")