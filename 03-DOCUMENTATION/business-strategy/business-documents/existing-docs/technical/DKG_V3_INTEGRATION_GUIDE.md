# DKG v3 Integration Guide

## Overview

This guide covers the integration between the DKG v3 Intelligence Service (port 8001) and the main AIA backend (port 8000). The DKG v3 system provides advanced knowledge graph intelligence capabilities that enhance the AIA backend's processing power.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   AIA Backend   │    │  DKG v3 Service │
│   (Port 8000)   │◄──►│   (Port 8001)   │
│                 │    │                 │
├─────────────────┤    ├─────────────────┤
│ • FastAPI App   │    │ • FastAPI App   │
│ • Multi-Agent   │    │ • U-DKG v3.0    │
│   System        │    │ • Intelligence  │
│ • Business      │    │   Engine        │
│   Logic         │    │ • Knowledge     │
│ • API Endpoints │    │   Graph         │
│ • DKG Client    │    │ • 3D Viz        │
└─────────────────┘    └─────────────────┘
```

## Components

### 1. DKG v3 Service (`aia/services/dkg_v3_service.py`)
- **Port**: 8001
- **Purpose**: Standalone FastAPI service providing knowledge graph intelligence
- **Core Engine**: `udkg_v3_intelligence_system.py`
- **Features**:
  - Intelligence insights generation
  - Fortune 500 opportunity analysis
  - 3D visualization data
  - Real-time knowledge processing

### 2. DKG Client (`aia/clients/dkg_v3_client.py`)
- **Purpose**: HTTP client for communication between backend and DKG service
- **Features**:
  - Async HTTP communication
  - Retry logic with exponential backoff
  - Health monitoring
  - Connection pooling

### 3. Backend Integration (`aia/main.py`)
- **Purpose**: Integrated DKG v3 endpoints in main AIA backend
- **New Endpoints**:
  - `/dkg-v3/health` - DKG service health check
  - `/dkg-v3/intelligence/query` - Intelligence analysis
  - `/dkg-v3/fortune500/opportunities` - Business opportunities
  - `/dkg-v3/3d-visualization` - 3D visualization data
  - `/process-with-dkg` - Hybrid AIA + DKG processing

### 4. Service Orchestrator (`aia/orchestrator/service_orchestrator.py`)
- **Purpose**: Python-based orchestrator for managing both services
- **Features**:
  - Sequential startup (DKG first, then backend)
  - Health monitoring
  - Graceful shutdown
  - Integration testing

## Quick Start

### Method 1: Using Python Orchestrator (Recommended)

```bash
cd /Users/wXy/dev/Projects/aia
python3 aia/orchestrator/service_orchestrator.py
```

### Method 2: Using Shell Script

```bash
cd /Users/wXy/dev/Projects/aia
./start_aia_with_dkg.sh
```

### Method 3: Manual Startup

Terminal 1 (DKG v3 Service):
```bash
cd /Users/wXy/dev/Projects/aia/aia
python3 -m services.dkg_v3_service
```

Terminal 2 (AIA Backend):
```bash
cd /Users/wXy/dev/Projects/aia
python3 -m uvicorn aia.main:app --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

```bash
# DKG v3 Service
export DKG_PORT=8001
export DKG_HOST=0.0.0.0
export DKG_WORKERS=1
export KNOWLEDGE_GRAPH_PATH="/Users/wXy/dev/Projects/aia/aia_knowledge_graph_v2_1759313796.json"

# AIA Backend
export PORT=8000
export PYTHONPATH="/Users/wXy/dev/Projects/aia:$PYTHONPATH"
```

### Service Configuration

DKG v3 Service supports:
- Knowledge graph path configuration
- GPU/CPU processing selection
- Port configuration
- CORS settings for backend communication

## API Endpoints

### DKG v3 Direct Endpoints (Port 8001)

#### Health Check
```bash
GET http://localhost:8001/health
```

#### Intelligence Query
```bash
POST http://localhost:8001/intelligence/query
Content-Type: application/json

{
    "context": "Analyze current AI market trends",
    "analysis_type": "business",
    "include_3d": false
}
```

#### Fortune 500 Opportunities
```bash
GET http://localhost:8001/intelligence/fortune500
```

#### System Status
```bash
GET http://localhost:8001/system/status
```

### Backend Integrated Endpoints (Port 8000)

#### DKG Health through Backend
```bash
GET http://localhost:8000/dkg-v3/health
```

#### Intelligence Query through Backend
```bash
POST http://localhost:8000/dkg-v3/intelligence/query
Content-Type: application/json

{
    "context": "Market analysis for enterprise AI solutions",
    "analysis_type": "business"
}
```

#### Hybrid Processing (AIA + DKG)
```bash
POST http://localhost:8000/process-with-dkg
Content-Type: application/json

{
    "context": "Comprehensive business strategy analysis",
    "task_type": "business",
    "include_intelligence": true,
    "include_3d": false
}
```

## Testing

### Run Integration Tests
```bash
cd /Users/wXy/dev/Projects/aia
python3 test_dkg_integration.py
```

### Manual Testing Examples

1. **Test DKG Health**:
```bash
curl http://localhost:8001/health
```

2. **Test Backend Integration**:
```bash
curl http://localhost:8000/dkg-v3/health
```

3. **Test Intelligence Query**:
```bash
curl -X POST http://localhost:8000/dkg-v3/intelligence/query \
  -H "Content-Type: application/json" \
  -d '{"context": "AI market trends analysis", "analysis_type": "business"}'
```

## Monitoring

### Health Checks
- DKG v3 Service: `http://localhost:8001/health`
- Backend Integration: `http://localhost:8000/dkg-v3/health`
- Backend Health: `http://localhost:8000/health`

### Logs
When using the orchestrator, logs are available:
- DKG v3: Check console output for service logs
- Backend: Check console output for backend logs

### Performance Monitoring
- Monitor response times for intelligence queries
- Track knowledge graph processing performance
- Monitor memory usage for large knowledge graphs

## Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check what's using the port
lsof -i :8001
lsof -i :8000

# Kill existing processes
kill -9 <PID>
```

2. **Knowledge Graph Not Found**
```bash
# Verify knowledge graph file exists
ls -la /Users/wXy/dev/Projects/aia/aia_knowledge_graph_v2_1759313796.json

# Set correct path
export KNOWLEDGE_GRAPH_PATH="/path/to/your/knowledge_graph.json"
```

3. **Connection Refused**
```bash
# Check if services are running
curl http://localhost:8001/health
curl http://localhost:8000/health

# Check firewall settings
# Ensure localhost connections are allowed
```

4. **Import Errors**
```bash
# Set Python path
export PYTHONPATH="/Users/wXy/dev/Projects/aia:$PYTHONPATH"

# Install missing dependencies
pip install -r requirements.txt
```

### Debug Mode

Start services with debug logging:
```bash
# DKG v3 Service
PYTHONPATH="/Users/wXy/dev/Projects/aia" python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from aia.services.dkg_v3_service import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8001, log_level='debug')
"

# AIA Backend
uvicorn aia.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

## Performance Optimization

### DKG v3 Service
- Use GPU acceleration when available
- Optimize knowledge graph loading
- Implement caching for frequent queries
- Use appropriate batch sizes for processing

### Backend Integration
- Connection pooling for HTTP client
- Async processing for DKG queries
- Timeout configuration for long-running queries
- Circuit breaker patterns for resilience

## Security Considerations

### CORS Configuration
- Backend allows connections from localhost:8000
- DKG service allows connections from backend
- Production deployment should restrict origins

### Authentication
- Currently no authentication between services
- Consider JWT tokens for production
- Implement API keys for service-to-service communication

## Production Deployment

### Docker Configuration
```dockerfile
# Dockerfile for DKG v3 Service
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["python", "-m", "services.dkg_v3_service"]
```

### Kubernetes Deployment
- Deploy DKG v3 as separate service
- Use service discovery for communication
- Implement health checks and readiness probes
- Configure resource limits and requests

### Load Balancing
- Use load balancer for multiple DKG instances
- Implement sticky sessions if needed
- Configure health checks

## Development

### Adding New Intelligence Features
1. Extend `udkg_v3_intelligence_system.py`
2. Add new endpoints to `dkg_v3_service.py`
3. Update client in `dkg_v3_client.py`
4. Add integration endpoints in `main.py`
5. Update tests

### Code Structure
```
aia/
├── services/
│   └── dkg_v3_service.py          # DKG v3 FastAPI service
├── clients/
│   └── dkg_v3_client.py           # HTTP client for DKG communication
├── analytics/
│   └── udkg_v3_intelligence_system.py  # Core intelligence engine
├── orchestrator/
│   └── service_orchestrator.py    # Service management
└── main.py                        # Main backend with DKG integration
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run the integration test suite
3. Review service logs
4. Check health endpoints
5. Verify configuration settings

---

**Integration Status**: ✅ Complete
**Last Updated**: 2024-12-08
**Version**: 1.0.0