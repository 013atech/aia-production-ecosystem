"""
DKG v3 WebSocket Handler for Real-Time Knowledge Updates
======================================================
Sprint 3-4: Real-time knowledge graph updates and streaming intelligence
Zero-disruption real-time enhancement layer
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import uuid
import weakref
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

@dataclass
class WebSocketConnection:
    """WebSocket connection metadata."""
    connection_id: str
    websocket: WebSocket
    client_info: Dict[str, Any]
    subscriptions: Set[str]
    connected_at: datetime
    last_activity: datetime

class WebSocketMessage:
    """WebSocket message types for DKG v3 communication."""

    # Message types
    KNOWLEDGE_UPDATE = "knowledge_update"
    INTELLIGENCE_STREAM = "intelligence_stream"
    PERFORMANCE_METRICS = "performance_metrics"
    SYSTEM_STATUS = "system_status"
    QUERY_PROGRESS = "query_progress"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    HEARTBEAT = "heartbeat"
    ERROR = "error"

    # Subscription channels
    CHANNEL_KNOWLEDGE_UPDATES = "knowledge_updates"
    CHANNEL_PERFORMANCE = "performance"
    CHANNEL_SYSTEM_STATUS = "system_status"
    CHANNEL_QUERY_RESULTS = "query_results"
    CHANNEL_INTELLIGENCE_INSIGHTS = "intelligence_insights"

@dataclass
class KnowledgeUpdate:
    """Real-time knowledge graph update."""
    update_id: str
    timestamp: datetime
    update_type: str  # "atom_added", "atom_modified", "relationship_changed", "insight_discovered"
    affected_atoms: List[str]
    changes: Dict[str, Any]
    impact_score: float
    confidence: float

@dataclass
class IntelligenceStreamChunk:
    """Streaming intelligence query chunk."""
    chunk_id: str
    request_id: str
    chunk_type: str  # "header", "insight", "visualization", "completion", "error"
    data: Dict[str, Any]
    sequence_number: int
    is_final: bool
    processing_time_ms: float

class DKGWebSocketManager:
    """Manages WebSocket connections for real-time DKG v3 communication."""

    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # channel -> connection_ids
        self.connection_lock = threading.RLock()
        self.background_tasks: Dict[str, asyncio.Task] = {}
        self.knowledge_update_queue = asyncio.Queue()
        self.performance_metrics_queue = asyncio.Queue()
        self.heartbeat_interval = 30  # seconds

    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None) -> str:
        """Accept WebSocket connection and register client."""
        await websocket.accept()

        connection_id = str(uuid.uuid4())
        client_info = client_info or {}

        connection = WebSocketConnection(
            connection_id=connection_id,
            websocket=websocket,
            client_info=client_info,
            subscriptions=set(),
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )

        with self.connection_lock:
            self.connections[connection_id] = connection

        # Start heartbeat task
        self.background_tasks[f"heartbeat_{connection_id}"] = asyncio.create_task(
            self._heartbeat_task(connection_id)
        )

        logger.info(f"✅ WebSocket client connected: {connection_id}")

        # Send welcome message
        await self._send_message(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat(),
            "available_channels": [
                WebSocketMessage.CHANNEL_KNOWLEDGE_UPDATES,
                WebSocketMessage.CHANNEL_PERFORMANCE,
                WebSocketMessage.CHANNEL_SYSTEM_STATUS,
                WebSocketMessage.CHANNEL_QUERY_RESULTS,
                WebSocketMessage.CHANNEL_INTELLIGENCE_INSIGHTS
            ]
        })

        return connection_id

    async def disconnect(self, connection_id: str):
        """Disconnect and cleanup WebSocket connection."""
        with self.connection_lock:
            if connection_id not in self.connections:
                return

            connection = self.connections[connection_id]

            # Remove from all subscriptions
            for channel in connection.subscriptions.copy():
                await self._unsubscribe_from_channel(connection_id, channel)

            # Cancel background tasks
            for task_key in list(self.background_tasks.keys()):
                if connection_id in task_key:
                    task = self.background_tasks.pop(task_key)
                    task.cancel()

            # Remove connection
            del self.connections[connection_id]

        logger.info(f"🔌 WebSocket client disconnected: {connection_id}")

    async def handle_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket message."""
        if connection_id not in self.connections:
            return

        connection = self.connections[connection_id]
        connection.last_activity = datetime.utcnow()

        message_type = message.get("type")

        try:
            if message_type == WebSocketMessage.SUBSCRIBE:
                await self._handle_subscribe(connection_id, message)
            elif message_type == WebSocketMessage.UNSUBSCRIBE:
                await self._handle_unsubscribe(connection_id, message)
            elif message_type == WebSocketMessage.HEARTBEAT:
                await self._handle_heartbeat(connection_id, message)
            elif message_type == "query_intelligence":
                await self._handle_streaming_query(connection_id, message)
            else:
                await self._send_error(connection_id, f"Unknown message type: {message_type}")

        except Exception as e:
            logger.error(f"Error handling WebSocket message from {connection_id}: {e}")
            await self._send_error(connection_id, f"Message handling error: {str(e)}")

    async def _handle_subscribe(self, connection_id: str, message: Dict[str, Any]):
        """Handle subscription request."""
        channel = message.get("channel")
        if not channel:
            await self._send_error(connection_id, "Channel is required for subscription")
            return

        await self._subscribe_to_channel(connection_id, channel)

        await self._send_message(connection_id, {
            "type": "subscription_confirmed",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _handle_unsubscribe(self, connection_id: str, message: Dict[str, Any]):
        """Handle unsubscription request."""
        channel = message.get("channel")
        if not channel:
            await self._send_error(connection_id, "Channel is required for unsubscription")
            return

        await self._unsubscribe_from_channel(connection_id, channel)

        await self._send_message(connection_id, {
            "type": "unsubscription_confirmed",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _handle_heartbeat(self, connection_id: str, message: Dict[str, Any]):
        """Handle heartbeat message."""
        await self._send_message(connection_id, {
            "type": "heartbeat_ack",
            "timestamp": datetime.utcnow().isoformat(),
            "server_time": time.time()
        })

    async def _handle_streaming_query(self, connection_id: str, message: Dict[str, Any]):
        """Handle streaming intelligence query."""
        query_data = message.get("query", {})
        request_id = str(uuid.uuid4())

        # Start streaming query task
        task = asyncio.create_task(
            self._execute_streaming_query(connection_id, request_id, query_data)
        )
        self.background_tasks[f"streaming_query_{request_id}"] = task

        await self._send_message(connection_id, {
            "type": "query_started",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _execute_streaming_query(self, connection_id: str, request_id: str, query_data: Dict[str, Any]):
        """Execute streaming intelligence query with real-time updates."""
        try:
            # Import here to avoid circular imports
            from aia.api.dkg_v3_performance_optimizer import get_optimized_dkg_query

            # Send query progress updates
            await self._send_streaming_chunk(connection_id, IntelligenceStreamChunk(
                chunk_id=str(uuid.uuid4()),
                request_id=request_id,
                chunk_type="header",
                data={"status": "processing", "progress": 0},
                sequence_number=0,
                is_final=False,
                processing_time_ms=0
            ))

            # Simulate progressive query processing with updates
            for progress in [25, 50, 75]:
                await asyncio.sleep(0.1)  # Small delay for demonstration
                await self._send_streaming_chunk(connection_id, IntelligenceStreamChunk(
                    chunk_id=str(uuid.uuid4()),
                    request_id=request_id,
                    chunk_type="progress",
                    data={"status": "processing", "progress": progress},
                    sequence_number=progress // 25,
                    is_final=False,
                    processing_time_ms=progress * 2
                ))

            # Execute the actual query
            start_time = time.time()
            result = await get_optimized_dkg_query(
                context=query_data.get("context", ""),
                analysis_type=query_data.get("analysis_type", "general"),
                include_3d=query_data.get("include_3d", False),
                max_results=query_data.get("max_results", 100)
            )
            processing_time = (time.time() - start_time) * 1000

            # Send final result
            await self._send_streaming_chunk(connection_id, IntelligenceStreamChunk(
                chunk_id=str(uuid.uuid4()),
                request_id=request_id,
                chunk_type="completion",
                data=result,
                sequence_number=99,
                is_final=True,
                processing_time_ms=processing_time
            ))

        except Exception as e:
            logger.error(f"Streaming query error: {e}")
            await self._send_streaming_chunk(connection_id, IntelligenceStreamChunk(
                chunk_id=str(uuid.uuid4()),
                request_id=request_id,
                chunk_type="error",
                data={"error": str(e)},
                sequence_number=-1,
                is_final=True,
                processing_time_ms=0
            ))

    async def _subscribe_to_channel(self, connection_id: str, channel: str):
        """Subscribe connection to a channel."""
        with self.connection_lock:
            if connection_id in self.connections:
                self.connections[connection_id].subscriptions.add(channel)
                self.subscriptions[channel].add(connection_id)

    async def _unsubscribe_from_channel(self, connection_id: str, channel: str):
        """Unsubscribe connection from a channel."""
        with self.connection_lock:
            if connection_id in self.connections:
                self.connections[connection_id].subscriptions.discard(channel)
                self.subscriptions[channel].discard(connection_id)

    async def _send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific WebSocket connection."""
        if connection_id not in self.connections:
            return

        connection = self.connections[connection_id]
        if connection.websocket.client_state != WebSocketState.CONNECTED:
            await self.disconnect(connection_id)
            return

        try:
            await connection.websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending WebSocket message to {connection_id}: {e}")
            await self.disconnect(connection_id)

    async def _send_streaming_chunk(self, connection_id: str, chunk: IntelligenceStreamChunk):
        """Send streaming query chunk."""
        await self._send_message(connection_id, {
            "type": WebSocketMessage.INTELLIGENCE_STREAM,
            "chunk": asdict(chunk)
        })

    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message."""
        await self._send_message(connection_id, {
            "type": WebSocketMessage.ERROR,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast message to all subscribers of a channel."""
        connection_ids = self.subscriptions.get(channel, set()).copy()

        for connection_id in connection_ids:
            await self._send_message(connection_id, message)

    async def broadcast_knowledge_update(self, update: KnowledgeUpdate):
        """Broadcast knowledge graph update to subscribers."""
        message = {
            "type": WebSocketMessage.KNOWLEDGE_UPDATE,
            "update": asdict(update),
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_channel(WebSocketMessage.CHANNEL_KNOWLEDGE_UPDATES, message)

    async def broadcast_performance_metrics(self, metrics: Dict[str, Any]):
        """Broadcast performance metrics to subscribers."""
        message = {
            "type": WebSocketMessage.PERFORMANCE_METRICS,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_channel(WebSocketMessage.CHANNEL_PERFORMANCE, message)

    async def broadcast_system_status(self, status: Dict[str, Any]):
        """Broadcast system status update."""
        message = {
            "type": WebSocketMessage.SYSTEM_STATUS,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_channel(WebSocketMessage.CHANNEL_SYSTEM_STATUS, message)

    async def _heartbeat_task(self, connection_id: str):
        """Background heartbeat task for connection health."""
        while connection_id in self.connections:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                if connection_id not in self.connections:
                    break

                connection = self.connections[connection_id]

                # Check if connection is stale
                time_since_activity = datetime.utcnow() - connection.last_activity
                if time_since_activity > timedelta(seconds=self.heartbeat_interval * 3):
                    logger.warning(f"Connection {connection_id} appears stale, disconnecting")
                    await self.disconnect(connection_id)
                    break

                # Send heartbeat
                await self._send_message(connection_id, {
                    "type": WebSocketMessage.HEARTBEAT,
                    "timestamp": datetime.utcnow().isoformat()
                })

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat task error for {connection_id}: {e}")
                break

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        with self.connection_lock:
            return {
                "total_connections": len(self.connections),
                "active_subscriptions": {
                    channel: len(connections)
                    for channel, connections in self.subscriptions.items()
                },
                "connection_details": [
                    {
                        "connection_id": conn.connection_id,
                        "connected_at": conn.connected_at.isoformat(),
                        "last_activity": conn.last_activity.isoformat(),
                        "subscriptions": list(conn.subscriptions),
                        "client_info": conn.client_info
                    }
                    for conn in self.connections.values()
                ]
            }

# Global WebSocket manager instance
dkg_websocket_manager = DKGWebSocketManager()

# Background tasks for real-time updates
class DKGRealtimeUpdater:
    """Background service for generating real-time DKG updates."""

    def __init__(self, websocket_manager: DKGWebSocketManager):
        self.websocket_manager = websocket_manager
        self.update_interval = 10  # seconds
        self.performance_update_interval = 5  # seconds
        self.running = False

    async def start(self):
        """Start real-time update services."""
        if self.running:
            return

        self.running = True

        # Start background tasks
        asyncio.create_task(self._knowledge_update_task())
        asyncio.create_task(self._performance_metrics_task())
        asyncio.create_task(self._system_status_task())

        logger.info("✅ DKG Real-time updater started")

    async def stop(self):
        """Stop real-time update services."""
        self.running = False
        logger.info("🛑 DKG Real-time updater stopped")

    async def _knowledge_update_task(self):
        """Background task for knowledge graph updates."""
        while self.running:
            try:
                await asyncio.sleep(self.update_interval)

                # Simulate knowledge update (in real implementation, this would monitor actual changes)
                update = KnowledgeUpdate(
                    update_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    update_type="insight_discovered",
                    affected_atoms=[f"atom_{i}" for i in range(3)],
                    changes={"new_insights": 2, "updated_relationships": 5},
                    impact_score=0.75,
                    confidence=0.92
                )

                await self.websocket_manager.broadcast_knowledge_update(update)

            except Exception as e:
                logger.error(f"Knowledge update task error: {e}")

    async def _performance_metrics_task(self):
        """Background task for performance metrics updates."""
        while self.running:
            try:
                await asyncio.sleep(self.performance_update_interval)

                # Get performance metrics
                from aia.api.dkg_v3_performance_optimizer import get_performance_statistics

                metrics = await get_performance_statistics()
                await self.websocket_manager.broadcast_performance_metrics(metrics)

            except Exception as e:
                logger.error(f"Performance metrics task error: {e}")

    async def _system_status_task(self):
        """Background task for system status updates."""
        while self.running:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds

                # Get system status
                status = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "system_health": "healthy",
                    "active_connections": len(self.websocket_manager.connections),
                    "memory_usage_mb": 256,  # Simulated
                    "cpu_usage_percent": 15,  # Simulated
                    "cache_status": "optimal"
                }

                await self.websocket_manager.broadcast_system_status(status)

            except Exception as e:
                logger.error(f"System status task error: {e}")

# Global real-time updater
dkg_realtime_updater = DKGRealtimeUpdater(dkg_websocket_manager)

async def initialize_websocket_system():
    """Initialize the DKG WebSocket system."""
    await dkg_realtime_updater.start()
    logger.info("✅ DKG v3 WebSocket system initialized")

async def shutdown_websocket_system():
    """Shutdown the DKG WebSocket system."""
    await dkg_realtime_updater.stop()
    logger.info("🛑 DKG v3 WebSocket system shutdown")

# FastAPI WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """FastAPI WebSocket endpoint for DKG v3 real-time communication."""
    connection_id = None

    try:
        client_info = {"client_id": client_id} if client_id else {}
        connection_id = await dkg_websocket_manager.connect(websocket, client_info)

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle message
            await dkg_websocket_manager.handle_message(connection_id, message)

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {connection_id}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON received from WebSocket client: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error for client {connection_id}: {e}")
    finally:
        if connection_id:
            await dkg_websocket_manager.disconnect(connection_id)