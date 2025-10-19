# AIA Terminal Integration Guide
## Complete Guide to Using AIA as a Coding AI from Terminal

🚀 **Status**: Production Ready
📍 **Version**: 1.0.0
🎯 **Target**: Developers & System Administrators

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Advanced Workflows](#advanced-workflows)
- [Troubleshooting](#troubleshooting)

---

## 🌟 Overview

The AIA Terminal Integration provides multiple ways to interact with the AIA multi-agent system directly from your terminal:

### 🎯 **System Architecture**
- **Port 8000**: Main AIA Backend (Multi-Agent System)
- **Port 8001**: DKG v3 Intelligence Service
- **Processing Modes**: Backend, DKG v3, Hybrid, Full AIA Workflow

### 🛠️ **Available Tools**
1. **Shell Functions** (`aia_terminal_integration.sh`) - Quick terminal commands
2. **CLI Tool** (`aia_cli.py`) - Comprehensive command-line interface
3. **Processing Client** (`claude_processing_client.py`) - Python API integration
4. **Backend Client** (`aia_backend_client.py`) - Direct backend access

---

## 🚀 Quick Start

### Step 1: System Health Check
```bash
# Check if AIA services are running
curl -s http://localhost:8000/health | jq
curl -s http://localhost:8001/health | jq
```

### Step 2: Load Shell Integration
```bash
# Source the shell functions
source aia_terminal_integration.sh

# Quick health check
aia-health

# System status
aia-status
```

### Step 3: First AIA Processing
```bash
# Basic processing
aia "analyze current project structure" technical

# Multi-agent approach
aia-agents "implement user authentication system"

# Business insights
aia-fortune500
```

---

## 🛠️ Available Tools

### 🔧 Shell Functions (`aia_terminal_integration.sh`)

**Core Commands:**
```bash
aia "task description" [type] [sprints]     # Main AIA processing
aia-agents "task" [type] [sprints]          # Multi-agent approach
aia-hybrid "task" [type]                    # Hybrid AIA+DKG processing
```

**System Management:**
```bash
aia-health                                  # Quick health check
aia-status                                  # Detailed system status
aia-start                                   # Start AIA services
aia-stop                                    # Stop AIA services
```

**Analytics & Data:**
```bash
aia-fortune500                              # Fortune 500 opportunities
aia-3d                                      # 3D visualization data
aia-api endpoint [method] [data]            # Direct API calls
```

### 🖥️ CLI Tool (`aia_cli.py`)

**Installation:**
```bash
pip install click rich pyyaml
chmod +x aia_cli.py
```

**Commands:**
```bash
# Processing
python3 aia_cli.py process "analyze code complexity" --type technical --sprints 5

# System status
python3 aia_cli.py status --detailed
python3 aia_cli.py health

# Multi-agent coordination
python3 aia_cli.py agents "optimize database queries"

# Business insights
python3 aia_cli.py insights --fortune500 --3d

# Interactive mode
python3 aia_cli.py interactive
```

### 🐍 Python Integration

**Direct Processing:**
```python
import asyncio
from claude_processing_client import process_with_aia_workflow

async def process_task():
    result = await process_with_aia_workflow(
        context="implement secure authentication system",
        task_type="technical",
        sprints=5,
        team_approach=True
    )
    print(f"Success: {result.success}")
    print(f"Business Value: ${result.data.get('dkg_intelligence', {}).get('insights', [{}])[0].get('business_value', 0):,.0f}")

asyncio.run(process_task())
```

---

## 💡 Usage Examples

### 🔨 Development Workflow Integration

**1. Code Analysis:**
```bash
# Analyze current codebase
aia "analyze the current project structure and suggest improvements" technical 3

# Code review assistance
aia "review the authentication implementation for security issues" security 2

# Performance optimization
aia-hybrid "optimize database queries for better performance" technical
```

**2. Feature Implementation:**
```bash
# Multi-agent feature development
aia-agents "implement real-time chat system with WebSocket" technical 8

# API development
aia "create RESTful API endpoints for user management" technical 5
```

**3. DevOps & Deployment:**
```bash
# Infrastructure analysis
aia "analyze current deployment strategy and suggest CI/CD improvements" devops 4

# Security audit
aia "perform security audit of the current system architecture" security 3
```

### 📊 Business Intelligence

**Fortune 500 Opportunities:**
```bash
# Get business opportunities
aia-fortune500

# Custom business analysis
aia "analyze market opportunities for our AI platform in enterprise segment" business 6
```

**System Analytics:**
```bash
# Performance monitoring
aia-api health
aia-api metrics

# 3D visualization data
aia-3d
```

### 🎯 Interactive Development

**Interactive Session:**
```bash
python3 aia_cli.py interactive

# Inside interactive mode:
AIA> process "implement JWT authentication"
AIA> status
AIA> config
AIA> exit
```

**Configuration Management:**
```bash
# View current config
python3 aia_cli.py config --show

# Set configuration
python3 aia_cli.py config --key default_sprints --value 8
python3 aia_cli.py config --key output_format --value json
```

---

## 🚀 Advanced Workflows

### 🎬 Complete Development Lifecycle

**1. Project Initialization:**
```bash
# Project structure analysis
aia "analyze the optimal project structure for a React + Node.js application with AI integration" technical 5

# Architecture planning
aia-agents "design system architecture for scalable AI-powered analytics platform" technical 10
```

**2. Implementation Phase:**
```bash
# Backend development
aia "implement secure user authentication with JWT and role-based access control" technical 8

# Frontend development
aia "create responsive dashboard components with real-time data visualization" technical 6

# Integration
aia-hybrid "integrate frontend and backend with proper error handling and loading states" technical 4
```

**3. Testing & Optimization:**
```bash
# Testing strategy
aia "create comprehensive testing strategy including unit, integration, and e2e tests" testing 4

# Performance optimization
aia "analyze and optimize application performance, focusing on database queries and API response times" performance 6
```

**4. Deployment & Monitoring:**
```bash
# Deployment strategy
aia "design and implement CI/CD pipeline with automated testing and deployment" devops 8

# Monitoring setup
aia "implement comprehensive monitoring, logging, and alerting system" devops 5
```

### 🧠 Multi-Agent Team Coordination

**Complex System Design:**
```bash
# Lead with cryptography agent (as per .claude/agents/aia.md)
aia-agents "design end-to-end encryption system for enterprise chat application" security 12

# Full team collaboration
aia "coordinate multi-agent team to implement microservices architecture with API gateway, service discovery, and load balancing" technical 15
```

**Sprint-Based Development:**
```bash
# Short sprint for quick features
aia "implement user profile management with avatar upload" technical 3

# Long sprint for complex features
aia "implement advanced analytics dashboard with real-time charts, filtering, and export capabilities" technical 12
```

### 📈 Business Intelligence Integration

**Market Analysis:**
```bash
# Fortune 500 integration opportunities
aia-fortune500

# Custom business intelligence
aia "analyze competitive landscape and identify market positioning opportunities for our AI platform" business 8

# Revenue optimization
aia "analyze current revenue streams and suggest optimization strategies" business 6
```

---

## 🔧 Configuration & Customization

### 🎯 Shell Function Configuration

**Environment Variables:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export AIA_BACKEND_URL="http://localhost:8000"
export AIA_DKG_URL="http://localhost:8001"
export AIA_PROJECT_ROOT="/Users/wXy/dev/Projects/aia"

# Load integration on shell startup
source /path/to/aia_terminal_integration.sh
```

### 🖥️ CLI Tool Configuration

**Config File Location:**
- `~/.aia/config.yaml`

**Default Configuration:**
```yaml
backend_url: "http://localhost:8000"
dkg_url: "http://localhost:8001"
default_sprints: 10
default_task_type: "technical"
output_format: "rich"  # rich, json, table, yaml
auto_confirm: false
show_progress: true
save_history: true
```

**Custom Configuration:**
```bash
# Set preferences
python3 aia_cli.py config --key default_sprints --value 8
python3 aia_cli.py config --key output_format --value json
python3 aia_cli.py config --key default_task_type --value business

# View current config
python3 aia_cli.py config --show
```

### 🐍 Python Client Configuration

**Environment Setup:**
```python
import os
from claude_processing_client import ClaudeProcessingClient

# Custom configuration
client = ClaudeProcessingClient()
client.backend_url = os.getenv('AIA_BACKEND_URL', 'http://localhost:8000')
client.dkg_url = os.getenv('AIA_DKG_URL', 'http://localhost:8001')
client.timeout = 120  # Extended timeout for complex processing
```

---

## 🧪 Testing & Validation

### ✅ System Health Validation

**Quick Health Check:**
```bash
# Shell function
aia-health

# CLI tool
python3 aia_cli.py health

# Direct API
curl -s http://localhost:8000/health | jq '.status'
```

**Comprehensive Status:**
```bash
# Detailed system status
aia-status

# CLI tool with details
python3 aia_cli.py status --detailed

# Performance monitoring
python3 aia_cli.py status --watch  # Continuous monitoring
```

### 🎯 Processing Validation

**Test Processing Pipeline:**
```bash
# Simple test
aia "test system integration" technical 2

# Complex test with validation
aia-agents "analyze system performance and suggest optimizations" technical 5

# Business intelligence test
aia-fortune500
```

**Performance Benchmarking:**
```bash
# Test processing times
time aia "quick processing test" general 1

# Monitor system resources during processing
top -p $(pgrep -f "uvicorn aia.main")
```

---

## 🚨 Troubleshooting

### 🔍 Common Issues

**1. Services Not Running:**
```bash
# Check if services are up
lsof -i :8000 -i :8001

# Start services if needed
./start_aia_with_dkg.sh

# Or manually start backend
python3 -m uvicorn aia.main:app --host 0.0.0.0 --port 8000
```

**2. Import Errors:**
```bash
# Check Python path
echo $PYTHONPATH

# Add project to path
export PYTHONPATH="/Users/wXy/dev/Projects/aia:$PYTHONPATH"
```

**3. Permission Issues:**
```bash
# Make scripts executable
chmod +x aia_terminal_integration.sh
chmod +x aia_cli.py

# Check file permissions
ls -la aia_*.py aia_*.sh
```

**4. Missing Dependencies:**
```bash
# Install required packages
pip install click rich pyyaml aiohttp

# Check installation
python3 -c "import click, rich, yaml; print('All dependencies installed')"
```

### 🔧 Debug Mode

**Enable Verbose Output:**
```bash
# Shell functions with debug
export AIA_DEBUG=1
aia-status

# CLI tool with verbose mode
python3 aia_cli.py --verbose process "test task"

# Direct Python debugging
python3 -c "
import asyncio
from claude_processing_client import get_system_status
async def debug():
    status = await get_system_status()
    print('System Status:', status)
asyncio.run(debug())
"
```

**Log Analysis:**
```bash
# Check AIA backend logs
tail -f logs/aia_backend.log

# Check DKG service logs
tail -f logs/dkg_v3_service.log

# System resource monitoring
htop  # or top on older systems
```

---

## 📊 Performance Optimization

### ⚡ Best Practices

**1. Efficient Processing:**
- Use appropriate sprint counts (3-8 for most tasks)
- Choose correct task types (technical, business, security, etc.)
- Enable team approach for complex tasks

**2. System Resources:**
- Monitor memory usage during large processing tasks
- Use hybrid mode for balanced performance
- Consider background processing for long tasks

**3. Network Optimization:**
- Ensure stable connection to localhost services
- Use timeouts for long-running requests
- Implement retry logic for transient failures

### 📈 Monitoring & Metrics

**Real-time Monitoring:**
```bash
# Continuous system monitoring
python3 aia_cli.py status --watch

# API performance monitoring
watch -n 5 'curl -s http://localhost:8000/health | jq ".circuit_breakers"'

# Resource monitoring
watch -n 2 'ps aux | grep -E "(uvicorn|python.*aia)"'
```

**Performance Analytics:**
```bash
# Processing time analysis
time aia "benchmark processing task" technical 3

# System load analysis
aia-api metrics | jq '.performance'

# Memory usage tracking
aia-api health | jq '.components'
```

---

## 🎯 Integration Examples

### 🔗 IDE Integration

**VS Code Integration:**
```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "AIA: Analyze Code",
            "type": "shell",
            "command": "aia",
            "args": ["analyze current code for improvements", "technical", "3"],
            "group": "build"
        },
        {
            "label": "AIA: Review Security",
            "type": "shell",
            "command": "aia-agents",
            "args": ["review code for security vulnerabilities", "security", "2"],
            "group": "test"
        }
    ]
}
```

### 🤖 Git Hooks Integration

**Pre-commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🧠 Running AIA code analysis..."
source aia_terminal_integration.sh

# Analyze staged changes
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(js|ts|py)$")

if [ ! -z "$STAGED_FILES" ]; then
    aia "review staged files for code quality and potential issues: $STAGED_FILES" technical 2
fi
```

### 📝 Documentation Generation

**Automated Documentation:**
```bash
# Generate API documentation
aia "analyze the API endpoints and generate comprehensive documentation" technical 4

# Create README updates
aia "update README with latest features and usage examples" technical 2

# Generate deployment guide
aia "create deployment guide for production environment" devops 3
```

---

## 🎓 Advanced Tips & Tricks

### 🏆 Expert Workflows

**1. Continuous Integration:**
```bash
# Add to CI pipeline
- name: AIA Code Analysis
  run: |
    source aia_terminal_integration.sh
    aia "analyze pull request changes for code quality" technical 3
```

**2. Automated Testing:**
```bash
# Test AIA integration in scripts
test_aia_integration() {
    local result=$(aia "test integration" technical 1)
    if echo "$result" | grep -q "Success: True"; then
        echo "✅ AIA integration test passed"
        return 0
    else
        echo "❌ AIA integration test failed"
        return 1
    fi
}
```

**3. Custom Aliases:**
```bash
# Add to ~/.bashrc
alias aia-review='aia "review current code changes for quality and security" technical 3'
alias aia-optimize='aia "analyze performance and suggest optimizations" technical 4'
alias aia-deploy='aia "create deployment checklist and strategy" devops 2'
alias aia-debug='aia "analyze error logs and suggest debugging steps" technical 2'
```

### 🎨 Output Formatting

**JSON Output for Scripting:**
```bash
# Get structured output
python3 aia_cli.py --format json process "analyze system" | jq '.data.business_value'

# Parse insights
python3 aia_cli.py --format json insights --fortune500 | jq '.opportunities[0].value'
```

**Markdown for Documentation:**
```bash
# Generate markdown reports
python3 aia_cli.py --format yaml process "system analysis" > analysis_report.md
```

---

## 🎉 Success Metrics

### 📈 Key Performance Indicators

- **Processing Speed**: < 2 seconds for simple tasks
- **System Availability**: > 99.5% uptime
- **Business Value**: $500K+ identified opportunities per month
- **Code Quality**: 95%+ insight accuracy

### 🏅 Achievement Unlocked

You've successfully integrated AIA as your terminal-based coding AI! 🚀

**Next Steps:**
1. Explore advanced multi-agent workflows
2. Integrate with your IDE and development tools
3. Set up automated processing for routine tasks
4. Share insights with your team

---

## 📞 Support & Resources

### 🔗 Quick Links
- **Health Check**: `aia-health`
- **System Status**: `aia-status`
- **Help**: `aia-help` or `python3 aia_cli.py --help`
- **Interactive Mode**: `python3 aia_cli.py interactive`

### 🆘 Getting Help
- Use `aia-help` for available commands
- Check system status with `aia-status --detailed`
- Monitor logs in the `logs/` directory
- Test individual components with simple tasks first

---

**🚀 Happy coding with AIA! 🤖✨**

*Built with ❤️ by the AIA Team | Version 1.0.0*