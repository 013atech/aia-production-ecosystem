# AIA Local Development Guide

This guide helps you set up a complete local development environment for the AIA (Advanced Intelligence Architecture) system while waiting for cloud quotas.

## 🚀 Quick Start

```bash
# 1. Run the setup script
./setup-local-dev.sh

# 2. Add your API keys to .env.local (optional but recommended)
nano .env.local

# 3. Start the development environment
./start-local-dev.sh
```

## 📋 Prerequisites

- **Docker & Docker Compose**: Latest version installed and running
- **Git**: For version control
- **Node.js 18+**: For frontend development (if running outside Docker)
- **Python 3.11+**: For backend development (if running outside Docker)

## 🏗️ Architecture Overview

Your local development environment includes:

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Development Stack                   │
├─────────────────────────────────────────────────────────────┤
│ Frontend (React)     │ http://localhost:3000                │
│ Backend API (FastAPI)│ http://localhost:8000                │
│ API Documentation    │ http://localhost:8000/docs           │
│ PostgreSQL Database  │ localhost:5432                       │
│ Redis Cache          │ localhost:6379                       │
└─────────────────────────────────────────────────────────────┘
```

## ⚙️ Configuration Files

### `.env.local` - Environment Variables
Contains all configuration for local development:
- Database connections
- API keys (add your own)
- Feature flags
- Security settings (development only)

### `docker-compose.override.yml` - Docker Configuration
Extends the base `docker-compose.dev.yml` with local-specific settings:
- Port mappings
- Volume mounts for hot reloading
- Development-specific environment variables

### `init.sql` - Database Setup
Creates initial database schema and test data.

## 🔧 Development Workflow

### Starting Development
```bash
./start-local-dev.sh
```

This will:
1. Start all Docker services
2. Initialize the database
3. Display service URLs and useful commands

### Stopping Development
```bash
./stop-local-dev.sh
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f aia-api
docker-compose logs -f postgres
```

### Resetting Everything
```bash
# Stop and remove all data
docker-compose down -v
./start-local-dev.sh
```

## 🌐 Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React application |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Redoc | http://localhost:8000/redoc | Alternative API docs |
| Health Check | http://localhost:8000/api/health | System status |

## 🔑 API Keys Setup

Add your API keys to `.env.local`:

```bash
# LLM Providers
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
GROQ_API_KEY=your_groq_key_here
```

**Note**: The system works with mocked responses when API keys are not provided.

## 🧪 Testing the Setup

### 1. Backend Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "components": {...}
}
```

### 2. Database Connection
```bash
# Connect to PostgreSQL
docker exec -it $(docker ps -q -f name=postgres) psql -U aia_user -d aia_dev -c "SELECT version();"
```

### 3. Frontend Access
Open http://localhost:3000 in your browser.

### 4. API Documentation
Visit http://localhost:8000/docs to explore the API.

## 🔄 Development Features

### Hot Reloading
- **Frontend**: React hot reload enabled
- **Backend**: FastAPI auto-reload with file watching
- **Code Changes**: Instantly reflected without container restart

### Database Persistence
- Data persists between restarts
- Use `docker-compose down -v` to reset

### Mock Mode
- External APIs are mocked by default (`MOCK_EXTERNAL_APIS=true`)
- No need for all API keys during development

## 📊 Monitoring & Debugging

### Service Status
```bash
# Check running containers
docker ps

# View resource usage
docker stats
```

### Database Access
```bash
# PostgreSQL CLI
docker exec -it $(docker ps -q -f name=postgres) psql -U aia_user -d aia_dev

# Redis CLI
docker exec -it $(docker ps -q -f name=redis) redis-cli
```

### Application Logs
```bash
# Backend logs
docker-compose logs -f aia-api

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f postgres
```

## 🚨 Troubleshooting

### Port Conflicts
If ports 3000, 8000, 5432, or 6379 are in use:
1. Stop conflicting services
2. Or modify ports in `docker-compose.override.yml`

### Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up postgres -d
# Wait 10 seconds
docker-compose up -d
```

### Container Build Issues
```bash
# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Permission Issues
```bash
# Fix script permissions
chmod +x *.sh
```

## 🔧 Customization

### Adding New Services
Edit `docker-compose.override.yml` to add services like:
- Elasticsearch
- Grafana
- Additional databases

### Environment Variables
Add new variables to `.env.local` and reference in Docker Compose.

### Database Schema Changes
Modify `init.sql` or create migration scripts in `migrations/`.

## 🚀 Production Differences

This local setup differs from production:

| Aspect | Local | Production |
|--------|-------|------------|
| Security | Basic (dev keys) | Enterprise (strong keys) |
| Scale | Single instance | Kubernetes cluster |
| Database | Local PostgreSQL | Cloud SQL |
| Monitoring | Basic logs | Prometheus + Grafana |
| SSL | HTTP only | HTTPS with certificates |
| Performance | Development mode | Optimized builds |

## 📝 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Add API Keys**: Edit `.env.local` with your LLM provider keys
3. **Start Coding**: Frontend in `frontend/src/`, Backend in `aia/`
4. **Run Tests**: `npm test` (frontend), `pytest` (backend)
5. **Deploy**: Use production scripts when cloud quotas are available

## 🆘 Getting Help

- **Logs**: Check `docker-compose logs -f` for errors
- **Health**: Monitor http://localhost:8000/api/health
- **Reset**: Use `docker-compose down -v` for clean slate
- **API Docs**: http://localhost:8000/docs for endpoint details

Happy coding! 🎉