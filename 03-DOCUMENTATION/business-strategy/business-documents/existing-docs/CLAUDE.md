# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **013a** - an autonomous analytical partner built on the **Advanced Intelligence Architecture (AIA) System**. The platform transforms user prompts into comprehensive analyses through the **Model Control Protocol (MCP)**, delivering synchronized outputs across Report, Slides, and Dashboard formats.

### Core User Journey
1. **Onboarding**: Landing → Signup Flow → Email Verification → Subscription (Stripe)
2. **Setup**: AI Model Configuration → Research API Configuration  
3. **Analysis**: Main Request → MCP Orchestration → Editor View → Final Presentation
4. **Output**: Synchronized Triptych (Report/Slides/Dashboard) with real-time editing

## Commands

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Development server (http://localhost:3000)
npm start

# Build for production
npm run build  

# Run tests
npm test

# Linting and formatting
npm run lint
npm run format
```

### Backend Development  
```bash
# Install Python dependencies
pip install -r aia/requirements.txt

# Run main AIA system
python -m aia.main

# Run API server (main entry point)
uvicorn aia.api.full_api:app --reload --port 8000

# Run specific worker processes
python -m aia.orchestration.worker

# Run tests with coverage
pytest aia/tests/ -v --cov
```

### Docker Operations
```bash
# Development environment
docker-compose up -d --build

# Production deployment  
docker-compose -f docker-compose.production.yml up -d

# Database migrations
docker-compose exec api alembic upgrade head

# View logs
docker-compose logs -f aia-api
```

### Testing & Quality
```bash
# Backend tests
pytest aia/tests/ -v --cov

# Frontend tests
cd frontend && npm test

# End-to-end system tests
python run_comprehensive_e2e_tests.py

# System integration tests
python aia-system-tests.py
```

## Architecture

### Core Components
- **MCP (Model Control Protocol)**: Central orchestration system in `aia/orchestration/`
- **Multi-Agent System**: Distributed AI agents with LLM integration (`aia/agents/`, `aia/llm/`)
- **Frontend**: React 18 + TypeScript with Material-UI, Three.js for 3D visualization
- **API Gateway**: FastAPI server (`aia/api/full_api.py`) with JWT authentication
- **Economic Engine**: Token-based systems (`aia/economic/`) with AIA/AIA_GOV tokens

### Key Directories
```
aia/
├── api/full_api.py          # Main FastAPI server entry point
├── orchestration/           # MCP and multi-agent coordination
├── llm/unified_llm.py       # LLM provider abstraction (OpenAI, Anthropic, etc.)
├── economic/                # Treasury, tokens, economic modeling
├── dkg/                     # Distributed Knowledge Graph
├── performance/             # Agent performance tracking and ranking
└── crypto/                  # Production cryptography and secret management

frontend/src/
├── contexts/                # ThemeContext, AuthContext, MCPContext, ThreeJSContext
├── pages/                   # LandingPage, SignupFlow, MainRequestPage, EditorView, etc.
└── components/              # CommandOverlay, LoadingScreen, UI components
```

### Technology Stack
**Backend**: FastAPI, PostgreSQL + TimescaleDB, Redis, Celery, SQLAlchemy + Alembic  
**Frontend**: React 18, TypeScript, Material-UI v5, Redux Toolkit + Zustand, React Three Fiber  
**Infrastructure**: Docker, Kubernetes (GKE), Prometheus + Grafana, AWS S3

## Development Patterns

### MCP Workflow
The Model Control Protocol orchestrates the core analytical workflow:
1. **Data Acquisition**: Query research APIs based on user prompt
2. **AI Processing**: Route validated data to appropriate LLM providers
3. **Output Generation**: Create synchronized Report/Slides/Dashboard content
4. **State Management**: Maintain real-time sync between Editor and Final views

### Frontend Context System
The app uses multiple React contexts for state management:
- `MCPContext`: Manages MCP requests and orchestration state
- `AuthContext`: JWT authentication and user session  
- `ThemeContext`: Dark theme with cyan-to-lemon gradient accents
- `ThreeJSContext`: 3D visualization state for immersive slides

### API Integration Points
- **Authentication**: JWT-based with `/auth/login` and role-based access
- **MCP Endpoint**: `/api/v1/mcp/process` for main request processing
- **Real-time Updates**: WebSocket connections for Editor ↔ Backend sync
- **Export Functions**: `/api/v1/export/` endpoints for final output formats

## Environment Setup

Required environment variables (see `.env.production.template`):
- **Database**: `DATABASE_URL`, `REDIS_URL`
- **Authentication**: `JWT_SECRET`, `API_KEY_SECRET`  
- **LLM Providers**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, etc.
- **Cloud Services**: AWS S3 keys, SendGrid for emails, Stripe for payments
- **Monitoring**: Prometheus, Jaeger configuration

## UI/UX Guidelines

### Design System
- **Color Scheme**: Deep charcoal (`#1E1E1E`) background, ivory (`#F5F5DC`) text
- **Accent**: Dynamic cyan-to-lemon gradient for CTAs and highlights
- **Typography**: Clean geometric sans-serif, rigorous minimalism
- **Interactions**: Pill-shaped buttons, contextual automation via MCP

### Command Overlay Access
- **Burger Menu**: Full-screen overlay for history and settings
- **Keyboard Shortcuts**: `Cmd/Ctrl + H` (History), `Cmd/Ctrl + M` (Model Settings), `Cmd/Ctrl + D` (Data Settings)

## Development Workflow

1. **Feature Development**: Create feature branches from `develop` using Gitflow
2. **Code Style**: PEP 8 for Python, Prettier for JavaScript/TypeScript  
3. **Commits**: Follow Conventional Commits specification
4. **Testing**: pytest for backend, Jest + Cypress for frontend
5. **Pull Requests**: Should be focused and linked to relevant issues