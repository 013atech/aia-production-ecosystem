# GEMINI.md

This file provides guidance to Gemini when working with code in this repository.

## Project Overview

This is **013a** - an autonomous analytical partner built on the **Advanced Intelligence Architecture (AIA) System**. The platform transforms user prompts into comprehensive analyses through the **Model Control Protocol (MCP)**, delivering synchronized outputs across Report, Slides, and Dashboard formats.

### Core Components
- **Backend**: A Python-based multi-agent system using the FastAPI framework. It includes modules for economic governance, a dynamic knowledge graph, performance management, and more. The main application entry point is `aia/api/full_api.py`.
- **Frontend**: A React and TypeScript application with Material-UI for components and Three.js for 3D visualizations. The main entry point is `frontend/src/index.tsx`.
- **Database**: PostgreSQL is used for the main database, with Redis for caching.
- **Infrastructure**: The entire system is containerized using Docker. The production environment is deployed on Google Kubernetes Engine (GKE) and managed with Terraform. The project also includes configurations for local development using Docker Compose, and monitoring with Prometheus and Grafana.

## Building and Running

### Docker (Recommended)

The most reliable way to run the entire system is with Docker Compose, as it orchestrates all the services (backend, frontend, database, etc.).

**Production:**
```bash
# Build and start all services in detached mode
docker-compose -f docker-compose.production.yml up -d --build

# Stop and remove all services
docker-compose -f docker-compose.production.yml down
```

**Development:**
```bash
# Build and start all services in detached mode
docker-compose -f docker-compose.dev.yml up -d --build

# Stop and remove all services
docker-compose -f docker-compose.dev.yml down
```

### Local Development

**Backend:**

1.  **Install dependencies:**
    ```bash
    pip install -r aia/requirements.txt
    ```
2.  **Run the development server:**
    ```bash
    uvicorn aia.api.full_api:app --reload --port 8000
    ```

**Frontend:**

1.  **Install dependencies:**
    ```bash
    cd frontend
    npm install
    ```
2.  **Run the development server:**
    ```bash
    npm start
    ```
    The frontend will be available at `http://localhost:3000` and will proxy requests to the backend at `http://localhost:8000`.

## Testing

### Backend

The backend uses `pytest` for testing.

```bash
# Run all tests with coverage
pytest aia/tests/ -v --cov
```

### Frontend

The frontend uses `react-scripts test` (which likely uses Jest).

```bash
cd frontend
npm test
```

### End-to-End

The project uses Cypress for end-to-end testing, as referenced in the `package.json` file in the `frontend` directory. Please refer to the frontend testing documentation for details on how to run these tests.

## Development Conventions

*   **Commits**: The project appears to follow the Conventional Commits specification.
*   **Code Style**:
    *   **Python**: PEP 8
    *   **TypeScript/JavaScript**: Prettier
*   **API Documentation**: The FastAPI backend provides automatic API documentation at `/docs` and `/redoc` when running.
