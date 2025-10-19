# Multi-Agent System Integration Guide

## Overview

This document describes the complete Multi-Agent System (MAS) integration for the AIA platform, providing advanced agent orchestration, economic integration, real-time communication, and workflow management capabilities.

## Architecture Components

### 1. Agent Orchestration Engine (`aia/agents/multi_agent_system.py`)

**Core Features:**
- Agent lifecycle management (register, unregister, monitor)
- Dynamic task assignment with performance-based scoring
- Real-time agent status tracking with heartbeat monitoring
- Load balancing and capacity management
- Performance metrics collection and analysis

**Key Classes:**
- `AgentOrchestrationEngine` - Main orchestration system
- `AgentInstance` - Represents active agent instances
- `TaskSpecification` - Defines task requirements and constraints
- `WorkflowState` - Tracks workflow execution state

### 2. Economic Integration (`aia/agents/economic_integration.py`)

**Core Features:**
- AIA/AIA_GOV token integration with automated reward distribution
- Multi-tier staking system (Bronze → Diamond) with performance multipliers
- Governance participation with voting power based on stake
- Performance-based incentive programs
- Economic transaction processing and tracking

**Key Classes:**
- `AgentEconomicIntegrator` - Manages economic interactions
- `AgentEconomicProfile` - Tracks agent economic status
- `EconomicMASIntegration` - Bridges MAS and economic systems
- `PerformanceIncentive` - Defines reward structures

### 3. Communication Framework (`aia/agents/communication_framework.py`)

**Core Features:**
- Real-time WebSocket communication with connection management
- Priority-based message routing (Critical → Low → Maintenance)
- Event-driven architecture with custom event handlers
- Message persistence and retry logic with exponential backoff
- Multi-protocol support (WebSocket, HTTP, Redis Pub/Sub)

**Key Classes:**
- `EventDrivenCommunicationFramework` - Main communication system
- `MessageRouter` - Intelligent message routing with load balancing
- `MessageQueue` - Priority-based message queuing with persistence
- `WebSocketManager` - WebSocket connection management

### 4. Workflow Management (`aia/agents/workflow_management.py`)

**Core Features:**
- Sprint-based development coordination
- Task dependency management with cycle detection
- Quality assurance workflows with automated validation
- Workflow templates and reusable components
- Real-time progress tracking and monitoring

**Key Classes:**
- `WorkflowEngine` - Main workflow execution engine
- `SprintManager` - Sprint organization and coordination
- `DependencyResolver` - Task dependency analysis and ordering
- `QualityAssuranceEngine` - Automated quality gate validation

### 5. Integration APIs (`aia/agents/integration_apis.py`)

**Core Features:**
- FastAPI routers for all MAS operations
- WebSocket endpoints for real-time frontend updates
- Streaming API for workflow execution progress
- Comprehensive health checks and system monitoring
- Event broadcasting to connected clients

**API Endpoints:**
- `/mas/api/v1/agents/*` - Agent management operations
- `/mas/api/v1/economic/*` - Economic system operations
- `/mas/api/v1/communication/*` - Communication operations
- `/mas/api/v1/workflows/*` - Workflow management

## Integration with AIA Platform

The MAS system is fully integrated into the existing AIA platform through:

### 1. FastAPI Integration
```python
# In aia/api/full_api.py
if MAS_INTEGRATION_AVAILABLE and mas_router:
    app.include_router(mas_router, prefix="/mas")
```

### 2. System Initialization
```python
# During startup in initialize_core_systems()
if NewMultiAgentSystem:
    system_state["new_mas_system"] = NewMultiAgentSystem()
    await system_state["new_mas_system"].start()
```

### 3. Graceful Shutdown
```python
# During shutdown in graceful_shutdown()
if system_state.get("new_mas_system"):
    await system_state["new_mas_system"].stop()
```

## Usage Examples

### 1. Register an Agent

```python
from aia.agents.multi_agent_system import MultiAgentSystem, AgentCapabilities
from decimal import Decimal

mas = MultiAgentSystem()
await mas.start()

capabilities = AgentCapabilities(
    agent_id="data_analyst_001",
    specializations=["data_analysis", "statistics"],
    skills={"python": 0.9, "sql": 0.8, "statistics": 0.85},
    max_concurrent_tasks=3,
    cost_per_task=Decimal("15.0")
)

success = await mas.register_agent("data_analyst_001", capabilities)
```

### 2. Submit a Task

```python
from aia.agents.multi_agent_system import TaskSpecification

task = TaskSpecification(
    task_type="data_analysis",
    description="Analyze Q3 sales data",
    requirements={
        "skills": ["statistics", "python"],
        "data_sources": ["sales_db"]
    },
    max_cost=Decimal("50.0")
)

agent_id = await mas.orchestration_engine.assign_task(task)
```

### 3. Create and Execute Workflow

```python
from aia.agents.workflow_management import WorkflowEngine

workflow_engine = WorkflowEngine()

workflow_id = await workflow_engine.create_workflow_from_template(
    template_id="data_analysis_template",
    name="Q3 Sales Analysis",
    parameters={"quarter": "Q3", "year": 2024}
)

await workflow_engine.execute_workflow(workflow_id)
```

### 4. Economic Operations

```python
from aia.agents.economic_integration import AgentEconomicIntegrator

economic_integrator = AgentEconomicIntegrator()

# Register agent economically
await economic_integrator.register_agent_economically("agent_001", Decimal("500.0"))

# Stake tokens
await economic_integrator.stake_tokens("agent_001", Decimal("300.0"))

# Participate in governance
await economic_integrator.participate_in_governance("agent_001", "proposal_123", "yes")
```

### 5. Real-time Communication

```python
from aia.agents.communication_framework import EventDrivenCommunicationFramework, CommunicationMessage

comm_framework = EventDrivenCommunicationFramework()
await comm_framework.start()

message = CommunicationMessage(
    from_agent="system",
    to_agent="agent_001",
    message_type="task_request",
    payload={"task_id": "123", "description": "Process data"}
)

await comm_framework.send_message(message)
```

## API Usage

### 1. Register Agent via API

```bash
curl -X POST "http://localhost:8000/mas/api/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "data_analyst_001",
    "specializations": ["data_analysis", "statistics"],
    "skills": {"python": 0.9, "statistics": 0.8},
    "max_concurrent_tasks": 3,
    "cost_per_task": 15.0,
    "initial_stake": 500.0
  }'
```

### 2. Submit Task via API

```bash
curl -X POST "http://localhost:8000/mas/api/v1/agents/tasks/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "data_analysis",
    "description": "Analyze sales data",
    "requirements": {"skills": ["statistics"]},
    "max_cost": 50.0
  }'
```

### 3. Create Workflow via API

```bash
curl -X POST "http://localhost:8000/mas/api/v1/workflows/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Analysis Workflow",
    "workflow_type": "data_analysis",
    "template_id": "data_analysis_template",
    "parameters": {"quarter": "Q3"},
    "max_cost": 200.0
  }'
```

### 4. WebSocket Connection for Real-time Updates

```javascript
const ws = new WebSocket('ws://localhost:8000/mas/api/v1/agents/ws/frontend/client_001');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'metrics_update') {
        console.log('System metrics:', data.data);
    }
};
```

## Configuration

### Environment Variables

```bash
# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# WebSocket Configuration
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=8765

# Economic System Configuration
AIA_TREASURY_ADDRESS=your_treasury_address
AIA_GOV_TOKEN_ADDRESS=your_gov_token_address

# Performance Tuning
MAS_MAX_CONCURRENT_TASKS=100
MAS_HEARTBEAT_INTERVAL=30
MAS_MESSAGE_QUEUE_SIZE=10000
```

### System Configuration

```python
# In your application startup
MAS_CONFIG = {
    "orchestration": {
        "max_agents": 1000,
        "task_timeout": 300,
        "heartbeat_interval": 30
    },
    "economic": {
        "base_task_reward": "10.0",
        "staking_tiers": {
            "bronze": {"min_stake": "100.0", "multiplier": 1.0},
            "silver": {"min_stake": "500.0", "multiplier": 1.2},
            # ... more tiers
        }
    },
    "communication": {
        "websocket_host": "localhost",
        "websocket_port": 8765,
        "message_retention": 10000
    },
    "workflow": {
        "max_workflow_duration": 3600,
        "quality_gate_timeout": 60,
        "retry_attempts": 3
    }
}
```

## Monitoring and Metrics

### System Metrics Endpoint
```bash
curl "http://localhost:8000/mas/api/v1/agents/metrics/system"
```

### Economic Summary
```bash
curl "http://localhost:8000/mas/api/v1/economic/summary"
```

### Communication Metrics
```bash
curl "http://localhost:8000/mas/api/v1/communication/metrics"
```

### Workflow Metrics
```bash
curl "http://localhost:8000/mas/api/v1/workflows/metrics"
```

## Testing

Run the comprehensive test suite:

```bash
python test_mas_integration.py
```

Expected output:
```
🚀 Starting MAS Integration Tests...
✅ All MAS components imported successfully
✅ Multi-Agent System started
✅ Test agent registered successfully
✅ Economic integration successful
✅ Communication framework test successful
✅ Workflow created successfully
🎉 All MAS integration tests completed successfully!
```

## Error Handling and Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **WebSocket Connection Issues**: Check firewall and port availability
3. **Economic Transaction Failures**: Verify wallet addresses and balances
4. **Agent Registration Failures**: Check agent capabilities and requirements

### Logging

The system uses structured logging with different levels:

```python
import logging
logger = logging.getLogger(__name__)

# Set log level for debugging
logging.getLogger('aia.agents').setLevel(logging.DEBUG)
```

### Health Checks

The system provides comprehensive health checks:

```bash
curl "http://localhost:8000/mas/health"
```

## Performance Considerations

### Scaling Guidelines

1. **Agent Limit**: Tested up to 1000 concurrent agents
2. **Task Throughput**: ~100 tasks/second per orchestration engine
3. **WebSocket Connections**: ~10,000 concurrent connections
4. **Message Processing**: ~1000 messages/second priority queue

### Optimization Tips

1. Use Redis for distributed caching and message persistence
2. Configure appropriate WebSocket timeouts
3. Implement agent connection pooling for high-frequency operations
4. Use workflow templates to reduce overhead
5. Monitor memory usage with large agent populations

## Security Considerations

1. **Authentication**: All API endpoints support JWT authentication
2. **Authorization**: Role-based access control for economic operations
3. **Message Security**: Optional encryption for sensitive communications
4. **Rate Limiting**: Configurable rate limits per agent/client
5. **Input Validation**: Comprehensive request validation

## Future Enhancements

1. **Machine Learning Integration**: Agent performance prediction
2. **Advanced Scheduling**: Resource-aware task scheduling
3. **Cross-Platform Support**: Integration with other blockchain networks
4. **Enhanced Analytics**: Advanced performance analytics and reporting
5. **Mobile SDK**: Native mobile client support

## Support and Contributing

For issues, feature requests, or contributions:

1. Check the comprehensive test suite: `python test_mas_integration.py`
2. Review logs for detailed error information
3. Consult the API documentation at `/docs` endpoint
4. Monitor system health via metrics endpoints

The Multi-Agent System integration provides a robust, scalable foundation for advanced agent coordination, economic incentives, and workflow management within the AIA platform.