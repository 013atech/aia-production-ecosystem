# AIA Codebase Analysis System - Comprehensive Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the AIA Automated Codebase Analysis & Knowledge Base System across different environments: development, staging, and production.

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores, 2.4 GHz
- **Memory**: 4 GB RAM
- **Storage**: 10 GB available space
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows (WSL2)
- **Python**: 3.10 or higher
- **Network**: Internet connection for dependencies

### Recommended Production Requirements
- **CPU**: 8 cores, 3.0 GHz
- **Memory**: 16 GB RAM
- **Storage**: 100 GB SSD
- **Network**: 1 Gbps connection
- **Container Runtime**: Docker 20.10+ or Kubernetes 1.24+

## Quick Start (Development)

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-org/aia-analysis.git
cd aia-analysis

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-analysis.txt
```

### 2. Run Analysis
```bash
# Make CLI executable
chmod +x aia_analysis_cli.py

# Analyze a project
python aia_analysis_cli.py analyze /path/to/your/project

# Or use the direct system
python aia_codebase_analysis_system.py /path/to/your/project --monitor
```

### 3. View Results
```bash
# Check generated notes
ls -la knowledge_notes/

# View database
sqlite3 aia_knowledge.db ".tables"
```

## Local Development with Ollama

### 1. Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull llama2
# or for better performance:
ollama pull codellama:7b
```

### 2. Configure Environment
```bash
export OLLAMA_URL="http://localhost:11434"
export AIA_LOG_LEVEL="DEBUG"
```

### 3. Run with LLM Integration
```bash
python aia_analysis_cli.py analyze /path/to/project --verbose
```

## Docker Deployment

### 1. Build Docker Image
```bash
# Build the analysis system image
docker build -f Dockerfile.analysis -t aia/codebase-analysis:latest .

# Verify build
docker images | grep aia/codebase-analysis
```

### 2. Single Container Deployment
```bash
# Create data directories
mkdir -p data knowledge_notes logs

# Run container
docker run -d \
  --name aia-analysis \
  -v $(pwd)/project:/app/project:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/knowledge_notes:/app/knowledge_notes \
  -p 8000:8000 \
  aia/codebase-analysis:latest
```

### 3. Full Stack with Docker Compose
```bash
# Set environment variables
export PROJECT_SOURCE_PATH="$(pwd)/project"
export DATA_PATH="$(pwd)/data"
export NOTES_PATH="$(pwd)/knowledge_notes"

# Start full stack
docker-compose -f docker-compose.analysis.yml up -d

# Check status
docker-compose -f docker-compose.analysis.yml ps

# View logs
docker-compose -f docker-compose.analysis.yml logs -f aia-analysis
```

### 4. Access Services
- **Analysis API**: http://localhost:8000
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Jupyter Notebooks**: http://localhost:8888
- **Ollama API**: http://localhost:11434

## Kubernetes Deployment

### 1. Prerequisites
```bash
# Ensure kubectl is configured
kubectl cluster-info

# Install cert-manager (for TLS)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

### 2. Deploy to Kubernetes
```bash
# Apply the configuration
kubectl apply -f kubernetes-analysis.yaml

# Check deployment status
kubectl get pods -n aia-analysis
kubectl get services -n aia-analysis
kubectl get ingress -n aia-analysis

# Check logs
kubectl logs -f deployment/aia-analysis-deployment -n aia-analysis
```

### 3. Configure DNS (Optional)
```bash
# Get ingress IP
kubectl get ingress aia-analysis-ingress -n aia-analysis

# Add to /etc/hosts or configure DNS
# <INGRESS_IP> analysis.aia.tech
```

### 4. Scale Deployment
```bash
# Manual scaling
kubectl scale deployment aia-analysis-deployment --replicas=5 -n aia-analysis

# Check HPA status
kubectl get hpa -n aia-analysis
```

## Production Deployment

### 1. Environment Preparation
```bash
# Create production user
sudo useradd -r -s /bin/bash -d /opt/aia aia
sudo mkdir -p /opt/aia/{data,logs,config}
sudo chown -R aia:aia /opt/aia

# Setup directories
sudo mkdir -p /var/log/aia
sudo chown aia:aia /var/log/aia
```

### 2. Database Setup (PostgreSQL)
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE aia_knowledge;
CREATE USER aia_user WITH PASSWORD 'secure_password_2024';
GRANT ALL PRIVILEGES ON DATABASE aia_knowledge TO aia_user;
\q

# Configure connection
export DATABASE_URL="postgresql://aia_user:secure_password_2024@localhost/aia_knowledge"
```

### 3. Systemd Service
```bash
# Create service file
sudo tee /etc/systemd/system/aia-analysis.service << EOF
[Unit]
Description=AIA Codebase Analysis System
After=network.target postgresql.service

[Service]
Type=simple
User=aia
Group=aia
WorkingDirectory=/opt/aia
Environment=AIA_LOG_LEVEL=INFO
Environment=DATABASE_URL=postgresql://aia_user:secure_password_2024@localhost/aia_knowledge
Environment=OLLAMA_URL=http://localhost:11434
ExecStart=/opt/aia/venv/bin/python /opt/aia/aia_codebase_analysis_system.py /opt/aia/projects --monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable aia-analysis
sudo systemctl start aia-analysis
sudo systemctl status aia-analysis
```

### 4. Reverse Proxy (NGINX)
```bash
# Install NGINX
sudo apt install nginx

# Create configuration
sudo tee /etc/nginx/sites-available/aia-analysis << EOF
server {
    listen 80;
    server_name analysis.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name analysis.yourdomain.com;

    ssl_certificate /etc/ssl/certs/aia-analysis.crt;
    ssl_certificate_key /etc/ssl/private/aia-analysis.key;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files (notes)
    location /notes/ {
        alias /opt/aia/knowledge_notes/;
        autoindex on;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/aia-analysis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring and Observability

### 1. Log Management
```bash
# Configure logrotate
sudo tee /etc/logrotate.d/aia-analysis << EOF
/var/log/aia/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 aia aia
    postrotate
        systemctl reload aia-analysis
    endscript
}
EOF
```

### 2. Prometheus Metrics
```bash
# Add to prometheus.yml
cat >> /etc/prometheus/prometheus.yml << EOF
  - job_name: 'aia-analysis'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF

# Restart Prometheus
sudo systemctl restart prometheus
```

### 3. Grafana Dashboard
```bash
# Import dashboard JSON
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @grafana-dashboard.json
```

## Performance Optimization

### 1. Database Optimization
```sql
-- PostgreSQL optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_code_atoms_file_path ON code_atoms USING HASH (file_path);
CREATE INDEX CONCURRENTLY idx_code_atoms_updated_at ON code_atoms (updated_at DESC);
CREATE INDEX CONCURRENTLY idx_relationships_composite ON relationships (source_id, target_id, relationship_type);

-- Restart PostgreSQL
sudo systemctl restart postgresql
```

### 2. Application Tuning
```bash
# Environment variables for optimization
export PYTHONOPTIMIZE=1
export PYTHONUNBUFFERED=1
export AIA_WORKER_THREADS=8
export AIA_BATCH_SIZE=100
export AIA_CACHE_SIZE=1000
```

### 3. System-level Optimizations
```bash
# Increase file limits
echo "aia soft nofile 65536" >> /etc/security/limits.conf
echo "aia hard nofile 65536" >> /etc/security/limits.conf

# Kernel parameters
echo "vm.swappiness=10" >> /etc/sysctl.conf
echo "net.core.somaxconn=65536" >> /etc/sysctl.conf
sysctl -p
```

## Security Configuration

### 1. Firewall Setup
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from localhost to any port 8000
sudo ufw deny 8000
```

### 2. SSL/TLS Configuration
```bash
# Generate self-signed certificate (development)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/aia-analysis.key \
  -out /etc/ssl/certs/aia-analysis.crt

# Or use Let's Encrypt (production)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d analysis.yourdomain.com
```

### 3. User and Permission Management
```bash
# Restrict access to configuration files
sudo chmod 600 /opt/aia/config/*
sudo chown aia:aia /opt/aia/config/*

# Setup sudoers for service management
echo "aia ALL=(ALL) NOPASSWD: /bin/systemctl start aia-analysis, /bin/systemctl stop aia-analysis, /bin/systemctl restart aia-analysis" >> /etc/sudoers.d/aia
```

## Backup and Recovery

### 1. Database Backup
```bash
# Create backup script
sudo tee /opt/aia/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/aia/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Database backup
pg_dump aia_knowledge > "$BACKUP_DIR/aia_knowledge_$DATE.sql"

# Knowledge notes backup
tar -czf "$BACKUP_DIR/knowledge_notes_$DATE.tar.gz" /opt/aia/knowledge_notes/

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/aia/backup.sh

# Setup cron job
echo "0 2 * * * /opt/aia/backup.sh >> /var/log/aia/backup.log 2>&1" | crontab -u aia -
```

### 2. Recovery Procedure
```bash
# Database recovery
sudo -u postgres createdb aia_knowledge_restored
sudo -u postgres psql aia_knowledge_restored < /opt/aia/backups/aia_knowledge_YYYYMMDD_HHMMSS.sql

# Knowledge notes recovery
tar -xzf /opt/aia/backups/knowledge_notes_YYYYMMDD_HHMMSS.tar.gz -C /opt/aia/
```

## Troubleshooting

### 1. Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status aia-analysis

# Check logs
sudo journalctl -u aia-analysis -f

# Common fixes
sudo systemctl restart aia-analysis
sudo systemctl daemon-reload
```

#### High Memory Usage
```bash
# Check memory usage
ps aux | grep python
htop

# Reduce batch size
export AIA_BATCH_SIZE=50
export AIA_CACHE_SIZE=500
```

#### Database Connection Issues
```bash
# Test database connection
psql -h localhost -U aia_user -d aia_knowledge

# Check PostgreSQL status
sudo systemctl status postgresql

# Reset database
sudo systemctl restart postgresql
```

### 2. Performance Issues

#### Slow Analysis
```bash
# Check system resources
iostat -x 1
vmstat 1

# Enable performance profiling
export AIA_PROFILING=true
export AIA_LOG_LEVEL=DEBUG
```

#### Large File Processing
```bash
# Increase file size limits
export AIA_MAX_FILE_SIZE=10485760  # 10MB

# Enable streaming processing
export AIA_STREAMING_MODE=true
```

## Maintenance

### 1. Regular Maintenance Tasks
```bash
# Daily tasks (automated via cron)
# - Database vacuum and analyze
# - Log rotation
# - Backup creation
# - Health checks

# Weekly tasks
# - Update dependencies
# - Security patches
# - Performance analysis

# Monthly tasks
# - Full system backup
# - Capacity planning review
# - Security audit
```

### 2. Updates and Upgrades
```bash
# Update application
cd /opt/aia
sudo -u aia git pull origin main
sudo -u aia /opt/aia/venv/bin/pip install -r requirements-analysis.txt
sudo systemctl restart aia-analysis

# Database migrations (if needed)
sudo -u aia python manage.py migrate

# Verify deployment
curl -f http://localhost:8000/health
```

## Scaling Considerations

### 1. Horizontal Scaling
- Load balancing across multiple analysis instances
- Database read replicas for heavy read workloads
- Redis cluster for distributed caching
- Message queue for async processing

### 2. Vertical Scaling
- Increase CPU cores for parallel processing
- Add more RAM for larger knowledge graphs
- SSD storage for faster I/O operations
- GPU acceleration for ML workloads

### 3. Architecture Evolution
- Microservices decomposition
- Event-driven architecture
- Container orchestration
- Cloud-native deployment

## Cost Optimization

### 1. Resource Optimization
- Right-size compute resources
- Use spot instances for batch processing
- Implement auto-scaling policies
- Optimize storage classes

### 2. Monitoring Costs
- Set up billing alerts
- Track resource usage metrics
- Regular cost reviews
- Reserved instance planning

## Conclusion

This deployment guide provides comprehensive instructions for deploying the AIA Codebase Analysis System across different environments. Regular monitoring, maintenance, and optimization are key to ensuring optimal performance and reliability.

For additional support or questions, please refer to the system documentation or contact the development team.