"""
AIA Enterprise Platform - Knowledge Graph Service
===============================================

Advanced knowledge graph service that integrates 2,472+ knowledge atoms
with ML processing, semantic search, and real-time analytics.
"""

import json
import logging
import asyncio
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import redis.asyncio as redis

from aia.aia-enterprise-platform.core.backend.services..core.circuit_breaker import CircuitBreaker
from aia.aia-enterprise-platform.core.backend.services..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeAtom:
    """Represents a single knowledge atom in the graph"""
    id: str
    file_path: str
    content_hash: str
    file_type: str
    size_bytes: int
    created_timestamp: float
    content_excerpt: str
    semantic_summary: str
    technical_context: Dict[str, Any] = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)
    embedding: Optional[np.ndarray] = None
    relevance_score: float = 0.0


@dataclass
class SemanticQuery:
    """Represents a semantic search query"""
    search_term: str
    domain_filter: Optional[str] = None
    complexity_range: Optional[Tuple[float, float]] = None
    relationship_depth: int = 1
    limit: int = 10
    include_related: bool = True
    semantic_threshold: float = 0.5


@dataclass
class QueryResult:
    """Represents search results with metadata"""
    atoms: List[KnowledgeAtom]
    total_matches: int
    query_time: float
    semantic_scores: List[float] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class KnowledgeGraphService:
    """
    Production-grade knowledge graph service with ML integration
    """

    def __init__(self, redis_client: redis.Redis, circuit_breaker: CircuitBreaker):
        self.redis_client = redis_client
        self.circuit_breaker = circuit_breaker
        self.knowledge_atoms: Dict[str, KnowledgeAtom] = {}
        self.embedding_model: Optional[SentenceTransformer] = None
        self.vector_index: Optional[faiss.IndexFlatIP] = None
        self.atom_embeddings: Optional[np.ndarray] = None
        self.atom_ids: List[str] = []
        self.initialized = False
        self.analytics_data = {
            "total_queries": 0,
            "average_query_time": 0.0,
            "popular_concepts": {},
            "recent_queries": []
        }

    async def initialize(self):
        """Initialize the knowledge graph service"""
        try:
            # Initialize embedding model
            await self._initialize_embedding_model()

            # Initialize vector database
            await self._initialize_vector_database()

            # Load cached analytics if available
            await self._load_analytics()

            self.initialized = True
            logger.info("🧠 Knowledge Graph service initialized successfully")

        except Exception as e:
            logger.error(f"Knowledge Graph service initialization failed: {e}")
            raise

    async def _initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        try:
            model_name = settings.knowledge_graph_embedding_model
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"📊 Embedding model '{model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            # Fallback to a simple embedding method
            self.embedding_model = None

    async def _initialize_vector_database(self):
        """Initialize FAISS vector database"""
        try:
            # We'll initialize with a placeholder dimension
            # The actual dimension will be set when we load embeddings
            embedding_dim = 384  # Default for all-MiniLM-L6-v2
            self.vector_index = faiss.IndexFlatIP(embedding_dim)
            logger.info(f"🗄️ Vector database initialized with {embedding_dim} dimensions")
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")

    async def load_knowledge_graph(self, file_path: str):
        """Load knowledge graph from JSON file"""
        try:
            start_time = asyncio.get_event_loop().time()

            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            knowledge_atoms_data = data.get('knowledge_atoms', [])
            logger.info(f"📚 Loading {len(knowledge_atoms_data)} knowledge atoms...")

            # Process atoms in batches for better performance
            batch_size = 100
            total_atoms = 0

            for i in range(0, len(knowledge_atoms_data), batch_size):
                batch = knowledge_atoms_data[i:i + batch_size]
                await self._process_atom_batch(batch)
                total_atoms += len(batch)

                if i % (batch_size * 10) == 0:  # Log progress every 1000 atoms
                    logger.info(f"📊 Processed {total_atoms}/{len(knowledge_atoms_data)} atoms...")

            # Generate embeddings for all atoms
            await self._generate_embeddings()

            # Build vector index
            await self._build_vector_index()

            # Cache the loaded graph
            await self._cache_knowledge_graph()

            load_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"✅ Knowledge graph loaded successfully in {load_time:.2f}s")
            logger.info(f"📈 Total atoms: {len(self.knowledge_atoms)}")

        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {e}")
            raise

    async def _process_atom_batch(self, atoms_batch: List[Dict[str, Any]]):
        """Process a batch of knowledge atoms"""
        for atom_data in atoms_batch:
            try:
                atom = KnowledgeAtom(
                    id=atom_data.get('id', ''),
                    file_path=atom_data.get('file_path', ''),
                    content_hash=atom_data.get('content_hash', ''),
                    file_type=atom_data.get('file_type', ''),
                    size_bytes=atom_data.get('size_bytes', 0),
                    created_timestamp=atom_data.get('created_timestamp', 0),
                    content_excerpt=atom_data.get('content_excerpt', ''),
                    semantic_summary=atom_data.get('semantic_summary', ''),
                    technical_context=atom_data.get('technical_context', {}),
                    relationships=atom_data.get('relationships', [])
                )

                self.knowledge_atoms[atom.id] = atom

            except Exception as e:
                logger.warning(f"Failed to process atom {atom_data.get('id', 'unknown')}: {e}")

    async def _generate_embeddings(self):
        """Generate embeddings for all knowledge atoms"""
        if not self.embedding_model:
            logger.warning("No embedding model available, using simple hash-based embeddings")
            await self._generate_fallback_embeddings()
            return

        try:
            logger.info("🔄 Generating embeddings for knowledge atoms...")

            # Prepare texts for embedding
            texts = []
            atom_ids = []

            for atom_id, atom in self.knowledge_atoms.items():
                # Combine semantic summary and content excerpt for better embeddings
                text = f"{atom.semantic_summary} {atom.content_excerpt}"
                texts.append(text)
                atom_ids.append(atom_id)

            # Generate embeddings in batches
            batch_size = 32
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                embeddings = self.embedding_model.encode(batch_texts, convert_to_numpy=True)
                all_embeddings.extend(embeddings)

                if i % (batch_size * 10) == 0:
                    logger.info(f"🧮 Generated embeddings for {i + len(batch_texts)}/{len(texts)} atoms")

            # Store embeddings
            self.atom_embeddings = np.array(all_embeddings)
            self.atom_ids = atom_ids

            # Update atoms with their embeddings
            for i, atom_id in enumerate(atom_ids):
                self.knowledge_atoms[atom_id].embedding = all_embeddings[i]

            logger.info(f"✅ Generated {len(all_embeddings)} embeddings successfully")

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            await self._generate_fallback_embeddings()

    async def _generate_fallback_embeddings(self):
        """Generate simple hash-based embeddings as fallback"""
        logger.info("🔄 Generating fallback embeddings...")

        embeddings = []
        atom_ids = []

        for atom_id, atom in self.knowledge_atoms.items():
            # Create a simple hash-based embedding
            text = f"{atom.semantic_summary} {atom.content_excerpt}"
            hash_value = hashlib.md5(text.encode()).hexdigest()

            # Convert hash to a simple embedding (384 dimensions to match model)
            embedding = np.array([
                int(hash_value[i:i+2], 16) / 255.0
                for i in range(0, min(len(hash_value), 64), 2)
            ])

            # Pad to 384 dimensions
            if len(embedding) < 384:
                padding = np.zeros(384 - len(embedding))
                embedding = np.concatenate([embedding, padding])

            embeddings.append(embedding[:384])  # Ensure exactly 384 dimensions
            atom_ids.append(atom_id)

        self.atom_embeddings = np.array(embeddings)
        self.atom_ids = atom_ids

    async def _build_vector_index(self):
        """Build FAISS vector index for semantic search"""
        if self.atom_embeddings is None:
            logger.warning("No embeddings available to build index")
            return

        try:
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(self.atom_embeddings)

            # Add embeddings to index
            self.vector_index.add(self.atom_embeddings)

            logger.info(f"🏗️ Vector index built with {self.vector_index.ntotal} vectors")

        except Exception as e:
            logger.error(f"Failed to build vector index: {e}")

    async def semantic_search(self, query: SemanticQuery) -> QueryResult:
        """Perform semantic search on the knowledge graph"""
        start_time = asyncio.get_event_loop().time()

        try:
            # Record query for analytics
            await self._record_query(query.search_term)

            # Generate query embedding
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query.search_term], convert_to_numpy=True)
            else:
                # Fallback hash-based embedding
                hash_value = hashlib.md5(query.search_term.encode()).hexdigest()
                query_embedding = np.array([[
                    int(hash_value[i:i+2], 16) / 255.0
                    for i in range(0, min(len(hash_value), 64), 2)
                ]])

                # Pad to 384 dimensions
                if query_embedding.shape[1] < 384:
                    padding = np.zeros((1, 384 - query_embedding.shape[1]))
                    query_embedding = np.concatenate([query_embedding, padding], axis=1)

            # Normalize query embedding
            faiss.normalize_L2(query_embedding)

            # Search vector index
            k = min(query.limit * 2, self.vector_index.ntotal)  # Get more results for filtering
            scores, indices = self.vector_index.search(query_embedding, k)

            # Filter and rank results
            results = []
            semantic_scores = []

            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score < query.semantic_threshold:
                    continue

                atom_id = self.atom_ids[idx]
                atom = self.knowledge_atoms[atom_id]

                # Apply domain filter if specified
                if query.domain_filter and query.domain_filter.lower() not in atom.semantic_summary.lower():
                    continue

                # Apply complexity filter if specified
                if query.complexity_range:
                    complexity = atom.technical_context.get('complexity_score', 0.5)
                    if not (query.complexity_range[0] <= complexity <= query.complexity_range[1]):
                        continue

                atom.relevance_score = float(score)
                results.append(atom)
                semantic_scores.append(float(score))

                if len(results) >= query.limit:
                    break

            # Generate related concepts
            related_concepts = await self._find_related_concepts(query.search_term, results)

            # Generate suggestions
            suggestions = await self._generate_suggestions(query.search_term, results)

            query_time = asyncio.get_event_loop().time() - start_time

            return QueryResult(
                atoms=results,
                total_matches=len(results),
                query_time=query_time,
                semantic_scores=semantic_scores,
                related_concepts=related_concepts,
                suggestions=suggestions
            )

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            # Return empty results on error
            query_time = asyncio.get_event_loop().time() - start_time
            return QueryResult(atoms=[], total_matches=0, query_time=query_time)

    async def _find_related_concepts(self, search_term: str, results: List[KnowledgeAtom]) -> List[str]:
        """Find related concepts based on search results"""
        concept_frequency = {}

        for atom in results[:5]:  # Use top 5 results
            # Extract concepts from semantic summary
            words = atom.semantic_summary.lower().split()
            for word in words:
                if len(word) > 3 and word not in search_term.lower():
                    concept_frequency[word] = concept_frequency.get(word, 0) + 1

        # Return top concepts
        sorted_concepts = sorted(concept_frequency.items(), key=lambda x: x[1], reverse=True)
        return [concept for concept, _ in sorted_concepts[:5]]

    async def _generate_suggestions(self, search_term: str, results: List[KnowledgeAtom]) -> List[str]:
        """Generate search suggestions based on results"""
        suggestions = []

        if len(results) == 0:
            suggestions.append(f"Try broadening your search for '{search_term}'")
            suggestions.append("Check spelling or try synonyms")
        elif len(results) < 3:
            suggestions.append("Try more general terms for more results")
        else:
            # Generate suggestions based on successful search
            file_types = set(atom.file_type for atom in results[:5])
            if len(file_types) > 1:
                suggestions.append(f"Filter by file type: {', '.join(file_types)}")

            # Suggest related searches
            for atom in results[:2]:
                tech_context = atom.technical_context
                if 'language' in tech_context:
                    suggestions.append(f"Explore more {tech_context['language']} files")

        return suggestions[:3]  # Limit to 3 suggestions

    async def analyze_knowledge_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the knowledge graph"""
        try:
            analysis = {
                "total_atoms": len(self.knowledge_atoms),
                "file_type_distribution": {},
                "language_distribution": {},
                "complexity_distribution": {},
                "relationship_patterns": {},
                "content_analysis": {},
                "temporal_patterns": {},
                "size_analysis": {}
            }

            # Analyze file types
            for atom in self.knowledge_atoms.values():
                file_type = atom.file_type
                analysis["file_type_distribution"][file_type] = \
                    analysis["file_type_distribution"].get(file_type, 0) + 1

                # Analyze programming languages
                tech_context = atom.technical_context
                if 'language' in tech_context:
                    language = tech_context['language']
                    analysis["language_distribution"][language] = \
                        analysis["language_distribution"].get(language, 0) + 1

                # Analyze complexity
                complexity = tech_context.get('complexity_score', 0)
                complexity_bucket = f"{int(complexity * 10) / 10:.1f}"
                analysis["complexity_distribution"][complexity_bucket] = \
                    analysis["complexity_distribution"].get(complexity_bucket, 0) + 1

                # Analyze file sizes
                size_mb = atom.size_bytes / (1024 * 1024)
                size_bucket = "large" if size_mb > 1 else "medium" if size_mb > 0.1 else "small"
                analysis["size_analysis"][size_bucket] = \
                    analysis["size_analysis"].get(size_bucket, 0) + 1

            # Analyze relationships
            total_relationships = sum(len(atom.relationships) for atom in self.knowledge_atoms.values())
            analysis["relationship_patterns"]["total_relationships"] = total_relationships
            analysis["relationship_patterns"]["average_per_atom"] = \
                total_relationships / len(self.knowledge_atoms) if self.knowledge_atoms else 0

            # Content analysis
            total_content_size = sum(len(atom.content_excerpt) for atom in self.knowledge_atoms.values())
            analysis["content_analysis"]["total_content_characters"] = total_content_size
            analysis["content_analysis"]["average_excerpt_length"] = \
                total_content_size / len(self.knowledge_atoms) if self.knowledge_atoms else 0

            # Temporal patterns
            if self.knowledge_atoms:
                timestamps = [atom.created_timestamp for atom in self.knowledge_atoms.values() if atom.created_timestamp]
                if timestamps:
                    analysis["temporal_patterns"]["earliest"] = min(timestamps)
                    analysis["temporal_patterns"]["latest"] = max(timestamps)
                    analysis["temporal_patterns"]["span_days"] = (max(timestamps) - min(timestamps)) / (24 * 3600)

            return analysis

        except Exception as e:
            logger.error(f"Knowledge pattern analysis failed: {e}")
            return {"error": str(e)}

    async def optimize_knowledge_graph(self) -> Dict[str, Any]:
        """Optimize the knowledge graph for better performance"""
        try:
            optimization_results = {
                "optimizations_applied": [],
                "performance_improvements": {},
                "recommendations": []
            }

            # Remove duplicate atoms based on content hash
            original_count = len(self.knowledge_atoms)
            hash_map = {}
            duplicates_removed = 0

            for atom_id, atom in list(self.knowledge_atoms.items()):
                if atom.content_hash in hash_map:
                    del self.knowledge_atoms[atom_id]
                    duplicates_removed += 1
                else:
                    hash_map[atom.content_hash] = atom_id

            if duplicates_removed > 0:
                optimization_results["optimizations_applied"].append(f"Removed {duplicates_removed} duplicate atoms")

            # Rebuild vector index if atoms were removed
            if duplicates_removed > 0:
                await self._generate_embeddings()
                await self._build_vector_index()
                optimization_results["optimizations_applied"].append("Rebuilt vector index")

            # Performance improvements
            optimization_results["performance_improvements"]["atoms_after_deduplication"] = len(self.knowledge_atoms)
            optimization_results["performance_improvements"]["space_saved_percentage"] = \
                (duplicates_removed / original_count * 100) if original_count > 0 else 0

            # Generate recommendations
            recommendations = []
            if len(self.knowledge_atoms) > 10000:
                recommendations.append("Consider implementing hierarchical clustering for large graphs")

            atom_sizes = [atom.size_bytes for atom in self.knowledge_atoms.values()]
            if atom_sizes and max(atom_sizes) > 1024 * 1024:  # 1MB
                recommendations.append("Consider splitting large files into smaller atoms")

            optimization_results["recommendations"] = recommendations

            logger.info(f"🔧 Knowledge graph optimization completed: {duplicates_removed} duplicates removed")
            return optimization_results

        except Exception as e:
            logger.error(f"Knowledge graph optimization failed: {e}")
            return {"error": str(e)}

    async def _record_query(self, search_term: str):
        """Record query for analytics"""
        try:
            self.analytics_data["total_queries"] += 1
            self.analytics_data["recent_queries"].append({
                "term": search_term,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Keep only recent queries (last 100)
            if len(self.analytics_data["recent_queries"]) > 100:
                self.analytics_data["recent_queries"] = self.analytics_data["recent_queries"][-100:]

            # Update popular concepts
            words = search_term.lower().split()
            for word in words:
                if len(word) > 2:
                    self.analytics_data["popular_concepts"][word] = \
                        self.analytics_data["popular_concepts"].get(word, 0) + 1

            # Cache analytics periodically
            if self.analytics_data["total_queries"] % 10 == 0:
                await self._cache_analytics()

        except Exception as e:
            logger.warning(f"Failed to record query analytics: {e}")

    async def _cache_knowledge_graph(self):
        """Cache knowledge graph data in Redis"""
        try:
            # Cache basic statistics
            stats = {
                "total_atoms": len(self.knowledge_atoms),
                "last_updated": datetime.utcnow().isoformat(),
                "embedding_model": settings.knowledge_graph_embedding_model
            }

            await self.redis_client.hset("kg:stats", mapping=stats)
            logger.info("📊 Knowledge graph statistics cached")

        except Exception as e:
            logger.warning(f"Failed to cache knowledge graph: {e}")

    async def _cache_analytics(self):
        """Cache analytics data in Redis"""
        try:
            await self.redis_client.hset("kg:analytics", mapping={
                "data": json.dumps(self.analytics_data)
            })
        except Exception as e:
            logger.warning(f"Failed to cache analytics: {e}")

    async def _load_analytics(self):
        """Load analytics data from Redis"""
        try:
            cached_data = await self.redis_client.hget("kg:analytics", "data")
            if cached_data:
                self.analytics_data.update(json.loads(cached_data))
                logger.info("📊 Analytics data loaded from cache")
        except Exception as e:
            logger.warning(f"Failed to load analytics: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            "total_atoms": len(self.knowledge_atoms),
            "total_relationships": sum(len(atom.relationships) for atom in self.knowledge_atoms.values()),
            "embedding_dimensions": self.atom_embeddings.shape[1] if self.atom_embeddings is not None else 0,
            "vector_index_size": self.vector_index.ntotal if self.vector_index else 0,
            "analytics": self.analytics_data,
            "initialized": self.initialized
        }