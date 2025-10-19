# AIA Local Development Environment Guide

## Overview

This guide provides comprehensive instructions for setting up and using the AIA (Artificial Intelligence Agent) local development environment. The setup includes all necessary services, databases, and mock APIs to enable full-stack development without external dependencies.

## 🏗️ Architecture Overview

The local development environment consists of:

- **Backend**: FastAPI application with multi-agent system
- **Frontend**: React application with 3D visualization capabilities
- **Database**: PostgreSQL with comprehensive schema
- **Cache**: Redis for session management and task queuing
- **Mock Services**: Local implementations of external APIs
- **Development Tools**: pgAdmin, RedisInsight, Jupyter Lab, TensorBoard

## 📋 Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows with WSL2
- **Docker**: Version 20.10+ with Docker Compose
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: At least 10GB free space
- **Network**: Internet connection for initial setup

### Required Software

1. **Docker Desktop**
   ```bash
   # macOS (via Homebrew)
   brew install --cask docker

   # Linux (Ubuntu)
   sudo apt-get update
   sudo apt-get install docker.io docker-compose

   # Verify installation
   docker --version
   docker-compose --version
   ```

2. **Git** (for version control)
   ```bash
   git --version
   ```

3. **curl** (for health checks)
   ```bash
   curl --version
   ```

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Navigate to the AIA project directory
cd /Users/wXy/dev/Projects/aia

# Make scripts executable (if not already)
chmod +x dev-scripts/*.sh

# Run the setup script
./dev-scripts/setup-dev-env.sh
```

The setup script will:
- ✅ Check prerequisites
- ✅ Create environment configuration
- ✅ Build Docker images
- ✅ Start all services
- ✅ Initialize database with schema and seed data
- ✅ Perform health checks

### 2. Verify Installation

After setup completes, verify services are running:

```bash
# Check service status
docker-compose -f docker-compose.dev.yml ps

# Check service health
curl http://localhost:8000/health    # Backend API
curl http://localhost:3000           # Frontend
curl http://localhost:9000/health    # Mock services
```

## 🌐 Service Access

| Service | URL | Credentials | Description |
|---------|-----|-------------|-------------|
| **Frontend** | http://localhost:3000 | - | React application with 3D interface |
| **Backend API** | http://localhost:8000 | - | FastAPI with documentation |
| **API Docs** | http://localhost:8000/docs | - | Interactive API documentation |
| **Database Admin** | http://localhost:5050 | dev@013a.tech / pgadmin_dev_2025 | PostgreSQL administration |
| **Redis Admin** | http://localhost:8001 | - | Redis management interface |
| **Jupyter Lab** | http://localhost:8888 | Token: mlops_dev_token_2025 | ML development environment |
| **TensorBoard** | http://localhost:6006 | - | ML model visualization |
| **Mock Services** | http://localhost:9000 | - | Mock external API endpoints |

## 🗄️ Database Configuration

### Connection Details

- **Host**: localhost
- **Port**: 5432
- **Database**: aia_development
- **Username**: aia_dev
- **Password**: aia_dev_password_2025

### Database Schema

The database includes the following schemas:

- **agents**: Multi-agent system data (agents, tasks, communications)
- **knowledge_graph**: Knowledge atoms and relationships
- **payment**: Transaction records and billing
- **ml_models**: ML model metadata and predictions
- **monitoring**: Health checks and performance metrics

### Database Operations

```bash
# Create backup
./dev-scripts/db-maintenance.sh backup

# Reset database
./dev-scripts/db-maintenance.sh reset

# Clean old data
./dev-scripts/db-maintenance.sh clean

# View statistics
./dev-scripts/db-maintenance.sh stats

# Run database tests
./dev-scripts/db-maintenance.sh test
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
./dev-scripts/run-tests.sh

# Run specific test suites
./dev-scripts/run-tests.sh backend      # Backend tests only
./dev-scripts/run-tests.sh frontend     # Frontend tests only
./dev-scripts/run-tests.sh integration  # Integration tests
./dev-scripts/run-tests.sh lint         # Code linting
./dev-scripts/run-tests.sh security     # Security tests
./dev-scripts/run-tests.sh performance  # Performance tests
./dev-scripts/run-tests.sh e2e          # End-to-end tests
```

### Test Coverage

The testing suite includes:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Service-to-service communication
- **E2E Tests**: Full user workflow testing
- **Performance Tests**: Response time and resource usage
- **Security Tests**: Basic security vulnerability checks
- **Linting**: Code quality and formatting checks

## 🔧 Development Workflow

### Making Code Changes

1. **Backend Changes**:
   ```bash
   # Backend supports hot reload
   # Edit files in ./aia/ directory
   # Changes will be automatically reflected
   ```

2. **Frontend Changes**:
   ```bash
   # Frontend supports hot reload
   # Edit files in ./frontend/src/ directory
   # Browser will automatically refresh
   ```

3. **Database Changes**:
   ```bash
   # Add migration scripts to ./dev-scripts/db-init/
   # Reset database to apply changes
   ./dev-scripts/db-maintenance.sh reset
   ```

### Debugging

1. **View Logs**:
   ```bash
   # All services
   docker-compose -f docker-compose.dev.yml logs -f

   # Specific service
   docker-compose -f docker-compose.dev.yml logs -f backend
   docker-compose -f docker-compose.dev.yml logs -f frontend
   ```

2. **Access Container Shell**:
   ```bash
   # Backend container
   docker-compose -f docker-compose.dev.yml exec backend bash

   # Frontend container
   docker-compose -f docker-compose.dev.yml exec frontend sh

   # Database container
   docker-compose -f docker-compose.dev.yml exec postgres psql -U aia_dev -d aia_development
   ```

3. **Debug with VS Code**:
   - Install Docker extension
   - Attach to running backend container
   - Set breakpoints and debug Python code

### Environment Variables

Create `.env.local` from the template:

```bash
cp .env.local.template .env.local
```

Key development variables:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database
DATABASE_URL=postgresql://aia_dev:aia_dev_password_2025@localhost:5432/aia_development

# External APIs (Mocked)
OPENAI_API_KEY=mock_openai_key_development_only
ANTHROPIC_API_KEY=mock_anthropic_key_development_only

# Feature Flags
MOCK_SERVICES_ENABLED=true
HOT_RELOAD=true
```

## 🎭 Mock Services

The development environment includes mock implementations of external services:

### OpenAI API Mock

```bash
# Test OpenAI chat completion
curl -X POST http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello, world!"}]
  }'
```

### Anthropic API Mock

```bash
# Test Anthropic completion
curl -X POST http://localhost:9000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello, world!"}]
  }'
```

### Stripe API Mock

```bash
# Test Stripe payment intent
curl -X POST http://localhost:9000/v1/payment_intents \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2000,
    "currency": "usd",
    "payment_method": "pm_card_visa"
  }'
```

## 🔄 Common Operations

### Starting and Stopping

```bash
# Start environment
./dev-scripts/setup-dev-env.sh

# Stop services (keep data)
./dev-scripts/stop-dev-env.sh

# Stop and remove containers
./dev-scripts/stop-dev-env.sh --remove

# Stop and clean all data
./dev-scripts/stop-dev-env.sh --clean
```

### Complete Reset

```bash
# Reset entire environment
./dev-scripts/reset-dev-env.sh

# Reset with automatic restart
./dev-scripts/reset-dev-env.sh --force --restart
```

### Maintenance

```bash
# Update dependencies
docker-compose -f docker-compose.dev.yml build --no-cache

# Clean Docker system
docker system prune -a

# View resource usage
docker stats
```

## 🛠️ Customization

### Adding New Services

1. **Add to docker-compose.dev.yml**:
   ```yaml
   my-service:
     build:
       context: ./my-service
     ports:
       - "9001:9001"
     depends_on:
       - postgres
     networks:
       - aia-network
   ```

2. **Create service directory**:
   ```bash
   mkdir my-service
   # Add Dockerfile, requirements.txt, etc.
   ```

3. **Update environment variables**:
   ```env
   MY_SERVICE_URL=http://localhost:9001
   ```

### Modifying Database Schema

1. **Add migration script**:
   ```bash
   # Create new migration file
   touch dev-scripts/db-init/03-add-my-table.sql
   ```

2. **Reset database**:
   ```bash
   ./dev-scripts/db-maintenance.sh reset
   ```

### Custom Mock Endpoints

Edit `dev-services/mock_api_server.py` to add new endpoints:

```python
@app.post("/my-custom-endpoint")
async def my_custom_endpoint(request: Dict[str, Any]):
    return {"status": "success", "data": "custom response"}
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Find process using port
   lsof -i :8000

   # Kill process
   kill -9 <PID>
   ```

2. **Docker Out of Space**:
   ```bash
   # Clean unused resources
   docker system prune -a -f

   # Clean volumes
   docker volume prune -f
   ```

3. **Database Connection Issues**:
   ```bash
   # Check database status
   docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U aia_dev

   # Restart database
   docker-compose -f docker-compose.dev.yml restart postgres
   ```

4. **Frontend Build Errors**:
   ```bash
   # Clear node modules and reinstall
   docker-compose -f docker-compose.dev.yml exec frontend rm -rf node_modules
   docker-compose -f docker-compose.dev.yml restart frontend
   ```

5. **Mock Services Not Working**:
   ```bash
   # Check mock service logs
   docker-compose -f docker-compose.dev.yml logs mock-services

   # Restart mock services
   docker-compose -f docker-compose.dev.yml restart mock-services
   ```

### Health Checks

```bash
# System health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/metrics

# Mock services status
curl http://localhost:9000/status
```

### Performance Issues

1. **Increase Docker Resources**:
   - Docker Desktop → Settings → Resources
   - Increase CPU and Memory allocation

2. **Optimize Database**:
   ```bash
   ./dev-scripts/db-maintenance.sh optimize
   ```

3. **Clean Old Data**:
   ```bash
   ./dev-scripts/db-maintenance.sh clean
   ```

## 📚 Additional Resources

### API Documentation

- **Backend API**: http://localhost:8000/docs
- **Frontend Components**: Check `frontend/src/components/` directory
- **Database Schema**: See `dev-scripts/db-init/01-init-database.sql`

### Development Tools

- **Jupyter Lab**: Access at http://localhost:8888 for ML development
- **TensorBoard**: View ML metrics at http://localhost:6006
- **pgAdmin**: Database administration at http://localhost:5050
- **RedisInsight**: Redis management at http://localhost:8001

### Configuration Files

- **Docker Compose**: `docker-compose.dev.yml`
- **Environment**: `.env.local.template`
- **Database Init**: `dev-scripts/db-init/`
- **Mock Services**: `dev-services/`

## 🤝 Contributing

### Code Standards

1. **Backend (Python)**:
   ```bash
   # Format code
   docker-compose -f docker-compose.dev.yml exec backend black .

   # Lint code
   docker-compose -f docker-compose.dev.yml exec backend flake8 .
   ```

2. **Frontend (TypeScript/React)**:
   ```bash
   # Format code
   docker-compose -f docker-compose.dev.yml exec frontend npm run format

   # Lint code
   docker-compose -f docker-compose.dev.yml exec frontend npm run lint
   ```

3. **Database**:
   - Use descriptive table and column names
   - Add appropriate indexes
   - Include foreign key constraints

### Submitting Changes

1. **Run Tests**:
   ```bash
   ./dev-scripts/run-tests.sh
   ```

2. **Check Code Quality**:
   ```bash
   ./dev-scripts/run-tests.sh lint
   ```

3. **Update Documentation**: Update this guide if you add new features

## 📞 Support

For development environment issues:

1. **Check Logs**: `docker-compose -f docker-compose.dev.yml logs -f`
2. **Run Health Checks**: `./dev-scripts/run-tests.sh integration`
3. **Reset Environment**: `./dev-scripts/reset-dev-env.sh`
4. **Review Documentation**: Check this guide and inline code comments

## 🎯 Next Steps

After setting up the development environment:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Run the Frontend**: Open http://localhost:3000
3. **Check Database**: Access pgAdmin at http://localhost:5050
4. **Run Tests**: Execute `./dev-scripts/run-tests.sh`
5. **Start Development**: Begin making changes and see them reflected in real-time

Happy coding! 🚀