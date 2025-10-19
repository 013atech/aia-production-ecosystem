# AIA System API Documentation

## Base URL
```
Production: https://013a.tech/api
Staging: https://staging.013a.tech/api
Local: http://localhost:8000/api
```

## Authentication

The API uses JWT Bearer tokens for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-token>
```

### Obtaining a Token

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=your-username&password=your-password&grant_type=password
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### API Key Authentication
For programmatic access, use your API key:

```http
X-API-Key: aia_your-api-key
```

## Core Endpoints

### 1. Process Endpoint

#### Process URL/Document
```http
POST /v1/process
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://example.com/article",
  "processing_type": "extract",
  "output_format": "structured",
  "options": {
    "include_metadata": true,
    "extract_entities": true,
    "generate_summary": true
  }
}
```

**Response:**
```json
{
  "process_id": "proc_abc123",
  "status": "completed",
  "data": {
    "title": "Article Title",
    "content": "Extracted content...",
    "summary": "AI-generated summary...",
    "entities": [
      {"type": "PERSON", "value": "John Doe"},
      {"type": "ORG", "value": "Company Inc"}
    ],
    "metadata": {
      "word_count": 1500,
      "language": "en",
      "published_date": "2024-01-15"
    }
  },
  "credits_used": 10
}
```

#### Upload Document
```http
POST /v1/process/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
processing_type=extract
```

### 2. Agent System

#### List Agents
```http
GET /v1/agents
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "agent_id": "agent_123",
    "agent_name": "Research Agent",
    "agent_type": "research",
    "llm_provider": "openai",
    "llm_model": "gpt-4",
    "is_active": true,
    "capabilities": ["web_search", "document_analysis", "summarization"]
  }
]
```

#### Create Agent
```http
POST /v1/agents
Authorization: Bearer <token>
Content-Type: application/json

{
  "agent_name": "Custom Agent",
  "agent_type": "analysis",
  "llm_provider": "anthropic",
  "llm_model": "claude-3-opus",
  "system_prompt": "You are an expert analyst...",
  "temperature": 0.7,
  "tools": ["calculator", "web_search"]
}
```

#### Execute Agent
```http
POST /v1/agents/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "agent_id": "agent_123",
  "input": "Analyze the latest AI trends",
  "parameters": {
    "max_results": 10,
    "search_depth": 2
  },
  "stream": false
}
```

**Response:**
```json
{
  "execution_id": "exec_xyz789",
  "status": "completed",
  "output": "Based on my analysis...",
  "tokens_used": 1500,
  "cost": 0.03,
  "duration_ms": 2500,
  "tools_used": ["web_search", "summarization"]
}
```

### 3. Knowledge Graph

#### Query Knowledge Graph
```http
POST /v1/dkg/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "Show connections between quantum computing and cryptography",
  "depth": 3,
  "limit": 50,
  "filters": {
    "node_types": ["technology", "concept"],
    "min_confidence": 0.7
  }
}
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "node_1",
      "label": "Quantum Computing",
      "type": "technology",
      "properties": {
        "description": "Computing using quantum phenomena",
        "year_introduced": 1980
      }
    }
  ],
  "edges": [
    {
      "source": "node_1",
      "target": "node_2",
      "relationship": "enables",
      "weight": 0.95
    }
  ],
  "metadata": {
    "total_nodes": 25,
    "total_edges": 48,
    "query_time_ms": 150
  }
}
```

#### Add Node to Knowledge Graph
```http
POST /v1/dkg/nodes
Authorization: Bearer <token>
Content-Type: application/json

{
  "label": "New Technology",
  "type": "technology",
  "properties": {
    "description": "Description of the technology",
    "category": "AI"
  },
  "embedding": null
}
```

#### Semantic Search
```http
POST /v1/dkg/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "artificial intelligence applications in healthcare",
  "top_k": 10,
  "threshold": 0.7
}
```

### 4. Economic Dashboard

#### Get Economic Metrics
```http
GET /v1/economic/metrics?timeframe=30d&category=macro
Authorization: Bearer <token>
```

**Response:**
```json
{
  "metrics": [
    {
      "name": "GDP Growth",
      "value": 2.5,
      "unit": "percent",
      "change": 0.3,
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "name": "Inflation Rate",
      "value": 3.2,
      "unit": "percent",
      "change": -0.1,
      "timestamp": "2024-01-15T10:00:00Z"
    }
  ],
  "summary": {
    "trend": "stable",
    "outlook": "positive"
  }
}
```

#### Generate Economic Report
```http
POST /v1/economic/generate-report
Authorization: Bearer <token>
Content-Type: application/json

{
  "report_type": "quarterly",
  "metrics": ["gdp", "inflation", "employment", "trade"],
  "format": "pdf",
  "include_predictions": true
}
```

### 5. Governance

#### Get Proposals
```http
GET /v1/governance/proposals?status=active
Authorization: Bearer <token>
```

#### Submit Vote
```http
POST /v1/governance/proposals/{proposal_id}/vote
Authorization: Bearer <token>
Content-Type: application/json

{
  "choice": "for",
  "reason": "I support this because..."
}
```

### 6. Performance Analytics

#### Get Agent Performance
```http
GET /v1/performance/agents?period=7d
Authorization: Bearer <token>
```

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "agent_123",
      "agent_name": "Research Agent",
      "total_executions": 150,
      "success_rate": 0.96,
      "avg_response_time_ms": 2300,
      "total_tokens": 45000,
      "total_cost": 1.35
    }
  ],
  "summary": {
    "total_agents": 10,
    "total_executions": 1500,
    "overall_success_rate": 0.94
  }
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('wss://013a.tech/ws?token=<your-token>');
```

### Message Types

#### Subscribe to Channel
```json
{
  "type": "subscribe",
  "data": {
    "channel": "agent_updates"
  }
}
```

#### Agent Status Updates
```json
{
  "type": "agent_status",
  "data": {
    "agent_id": "agent_123",
    "status": "executing",
    "progress": 0.45
  }
}
```

#### Streaming Response
```json
{
  "type": "stream_data",
  "data": {
    "stream_id": "stream_abc",
    "chunk": "The analysis shows that...",
    "is_final": false
  }
}
```

## Rate Limits

| Tier | Requests/Hour | Concurrent | Credits/Month |
|------|--------------|------------|---------------|
| Free | 100 | 2 | 1,000 |
| Premium | 1,000 | 10 | 10,000 |
| Enterprise | 10,000 | 100 | Unlimited |

## Error Responses

### Error Format
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Limit: 100/hour",
    "details": {
      "limit": 100,
      "reset_at": "2024-01-15T11:00:00Z"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| UNAUTHORIZED | 401 | Invalid or missing authentication |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |
| INVALID_REQUEST | 400 | Invalid request parameters |
| INSUFFICIENT_CREDITS | 402 | Not enough credits |
| INTERNAL_ERROR | 500 | Internal server error |

## SDKs

### Python
```python
from aia_system import AIAClient

client = AIAClient(api_key="your-api-key")

# Process document
result = client.process.url("https://example.com/article")

# Execute agent
response = client.agents.execute(
    agent_id="agent_123",
    input="Analyze this data"
)
```

### JavaScript/TypeScript
```javascript
import { AIAClient } from '@aia-system/sdk';

const client = new AIAClient({ apiKey: 'your-api-key' });

// Process document
const result = await client.process.url('https://example.com/article');

// Execute agent
const response = await client.agents.execute({
  agentId: 'agent_123',
  input: 'Analyze this data'
});
```

## Webhooks

Configure webhooks to receive real-time notifications:

```http
POST /v1/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["agent.completed", "process.completed"],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload
```json
{
  "event": "agent.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "execution_id": "exec_123",
    "agent_id": "agent_456",
    "status": "completed"
  },
  "signature": "sha256=..."
}
```

## Changelog

### v3.0.0 (2025-09-11)
- Multi-agent orchestration
- Enhanced knowledge graph with semantic search
- Real-time WebSocket support
- Subscription tiers with Stripe integration

### v2.0.0 (2024-06-01)
- Added governance system
- Performance analytics dashboard
- Improved rate limiting

### v1.0.0 (2024-01-01)
- Initial release
- Basic agent execution
- Document processing
- Knowledge graph queries