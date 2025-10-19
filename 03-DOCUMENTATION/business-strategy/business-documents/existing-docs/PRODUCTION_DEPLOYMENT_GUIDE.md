# AIA System Production Deployment Guide

## Overview

The AIA (Artificial Intelligence Agent) System is now production-ready with comprehensive monitoring, security, and scalability features. This guide covers deployment, configuration, and management procedures.

## System Architecture

### Core Components
- **AIA Multi-Agent System**: Advanced orchestration with GLAC, TSGLA, and TASA-NS-Alg agents
- **Structured Report Generation**: JSON-LD compliant reports with slide decks and dashboards  
- **Dynamic Knowledge Graph (DKG)**: Enhanced skill, tool, strategy, and education registries
- **Economic Governor**: Dual-token system (AIA utility, AIA_GOV governance) with conviction voting
- **Atomic Agentic Microservices**: Containerized services with event-driven communication

### Infrastructure Stack
- **API**: FastAPI with Pydantic v2, full OpenAPI documentation
- **Database**: PostgreSQL 15 with connection pooling
- **Cache**: Redis 7 with persistence
- **Load Balancer**: Nginx with SSL termination and rate limiting
- **Monitoring**: Prometheus + Grafana + Jaeger tracing
- **Container Orchestration**: Docker Compose (production) / Kubernetes (enterprise)

## Pre-deployment Checklist

### Required Environment Variables
```bash
# Core Security
export SECRET_KEY="your-ultra-secure-secret-key-here"
export JWT_SECRET="your-jwt-signing-secret-here"

# Database
export DB_PASSWORD="your-database-password"
export DB_NAME="aia_system"
export DB_USER="aia"

# AI Provider Keys
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key" # Optional
export ANTHROPIC_API_KEY="your-anthropic-key" # Optional

# Optional Overrides
export ENVIRONMENT="production"
export API_PORT="8000"
export REDIS_PASSWORD="auto-generated-if-not-set"
```

### System Requirements
- **CPU**: 4+ cores recommended (8+ for high load)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ SSD for databases and logs
- **Network**: Stable internet for AI API calls

## Deployment Options

### Option 1: Quick Production Deploy (Recommended)
```bash
# 1. Set required environment variables
source .env.production

# 2. Run deployment script
./deploy-production.sh
```

### Option 2: Manual Docker Compose
```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up -d --build

# Monitor logs
docker-compose -f docker-compose.production.yml logs -f
```

### Option 3: Kubernetes (Enterprise)
```bash
# Deploy to existing K8s cluster
kubectl apply -f aia/k8s/
```

## Service URLs (Default Configuration)

| Service | URL | Description |
|---------|-----|-------------|
| AIA API | https://localhost:8000 | Main API endpoints |
| API Docs | https://localhost:8000/docs | Interactive API documentation |
| Grafana | http://localhost:3000 | Metrics dashboards (admin/admin) |
| Prometheus | http://localhost:9090 | Metrics collection |
| Jaeger | http://localhost:16686 | Distributed tracing |

## Configuration Management

### Feature Flags
Control system capabilities via environment variables:

```bash
# Core Features
export STRUCTURED_REPORTS_ENABLED="true"
export DKG_ENHANCED_ENABLED="true" 
export GOVERNANCE_ENABLED="true"
export WEBSOCKET_ENABLED="true"

# Advanced Features
export ADVANCED_ANALYTICS_ENABLED="false"  # Enable for enterprise
```

### Performance Tuning
```bash
# API Configuration
export API_WORKERS="4"                    # CPU cores
export MAX_REQUEST_SIZE="16777216"        # 16MB max
export RATE_LIMIT_REQUESTS="1000"        # Per hour
export RATE_LIMIT_WINDOW="3600"          # Seconds

# Database Optimization  
export DB_POOL_SIZE="10"
export DB_MAX_OVERFLOW="20"

# Redis Configuration
export REDIS_MAX_CONNECTIONS="100"

# LLM Settings
export LLM_MAX_TOKENS="4000"
export LLM_TEMPERATURE="0.7" 
export LLM_TIMEOUT_SECONDS="30"
export LLM_RETRY_ATTEMPTS="3"
```

## Monitoring and Observability

### Health Monitoring
```bash
# Check system health
curl https://localhost:8000/health

# Check metrics
curl https://localhost:8000/metrics
```

### Key Metrics to Monitor
- API response times (< 500ms P95)
- Database connection pool usage
- Redis memory utilization  
- Agent task completion rates
- Token transaction volumes
- Error rates (< 1%)

### Alerting Setup (Grafana)
1. Import dashboard: `monitoring/grafana-dashboards/aia-overview.json`
2. Configure notification channels
3. Set up alert rules for:
   - High error rates
   - Database connection failures
   - Memory/CPU usage thresholds
   - API availability

## Security Considerations

### SSL/TLS Configuration
- Self-signed certificates generated automatically
- For production: Replace with valid SSL certificates
- Configure certificate renewal (Let's Encrypt recommended)

### Network Security
- Rate limiting enabled (configurable)
- CORS policies configured
- Security headers enforced
- Database access restricted to application network

### Secrets Management
- Environment variables for sensitive data
- Consider using HashiCorp Vault for enterprise
- Rotate secrets regularly
- Never commit secrets to version control

## Backup and Recovery

### Database Backups
```bash
# Create backup
docker-compose -f docker-compose.production.yml exec postgres \
    pg_dump -U aia aia_system > backup_$(date +%Y%m%d).sql

# Restore backup  
docker-compose -f docker-compose.production.yml exec -T postgres \
    psql -U aia aia_system < backup_20240911.sql
```

### Redis Persistence
- Redis configured with RDB + AOF persistence
- Backup `/data/redis` volume regularly

## Scaling and High Availability

### Horizontal Scaling
```bash
# Scale API instances
docker-compose -f docker-compose.production.yml up -d --scale aia-api=3

# Load balancer automatically distributes traffic
```

### Database Scaling
- Consider read replicas for high read loads
- Implement connection pooling (already configured)
- Monitor query performance and add indexes as needed

### Cache Scaling
- Redis Cluster for horizontal scaling
- Monitor memory usage and eviction policies

## Troubleshooting

### Common Issues

**API not starting**
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs aia-api

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Port conflicts
```

**Database connection errors**
```bash
# Verify database is running
docker-compose -f docker-compose.production.yml ps postgres

# Check database logs
docker-compose -f docker-compose.production.yml logs postgres
```

**High memory usage**
```bash
# Monitor container resource usage
docker stats

# Check for memory leaks in application logs
docker-compose -f docker-compose.production.yml logs aia-api | grep -i memory
```

### Performance Issues
1. Check Grafana dashboards for bottlenecks
2. Monitor database slow query logs
3. Verify AI API response times
4. Check Redis hit rates
5. Review application logs for errors

## Maintenance

### Regular Tasks
- Monitor disk usage and clean old logs
- Update dependencies (security patches)
- Rotate SSL certificates
- Backup databases
- Review metrics and alerts

### Updates and Upgrades
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d --build
```

## Support and Documentation

### Additional Resources
- **API Documentation**: Available at `/docs` endpoint
- **System Architecture**: See `SYSTEM_DOCUMENTATION.md`
- **Development Guide**: See `CONTRIBUTING.md`

### Getting Help
1. Check application logs first
2. Review this deployment guide
3. Check GitHub issues
4. Contact system administrator

---

**Status**: ✅ Production Ready
**Last Updated**: September 11, 2025
**Version**: 3.0.0

The AIA System is now fully deployed and ready for production workloads with comprehensive monitoring, security, and scalability features.