# AIA System - Developer Guide

## Quick Start

```bash
# Clone repository
git clone https://github.com/aia-system/platform.git
cd platform

# Set up environment
export GEMINI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GCP_PROJECT="your-project"

# Deploy to GCP
./deploy-complete-aia.sh

# Test deployment
curl http://YOUR_IP:8000/health
```

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Architecture Overview](#architecture-overview)
3. [Core Concepts](#core-concepts)
4. [Integration Examples](#integration-examples)
5. [Common Use Cases](#common-use-cases)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)

## Development Environment Setup

### Prerequisites

```yaml
requirements:
  python: ">=3.11"
  docker: ">=20.10"
  kubernetes: ">=1.27"
  gcloud: "latest"
  tools:
    - kubectl
    - helm
    - docker-compose
    - git
```

### Local Development

#### 1. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r aia_system/requirements.txt
pip install -r aia_system/requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### 2. Run Local Services

```bash
# Start local dependencies
docker-compose -f docker-compose.local.yml up -d

# Services started:
# - Neo4j: localhost:7474 (Browser), localhost:7687 (Bolt)
# - Kafka: localhost:9092
# - Redis: localhost:6379
```

#### 3. Configure Environment

```bash
# Create .env file
cat > .env << EOF
# API Keys
GEMINI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
XAI_API_KEY=your-key

# Local Services
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
KAFKA_BROKERS=localhost:9092
REDIS_HOST=localhost
REDIS_PORT=6379

# Development
DEBUG=true
LOG_LEVEL=DEBUG
EOF
```

#### 4. Run Application

```bash
# Run with hot reload
cd aia_system
uvicorn api.full_api:app --reload --host 0.0.0.0 --port 8000

# Or use the development script
python run-aia-system.py --dev
```

### Docker Development

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install development tools
RUN apt-get update && apt-get install -y \
    git vim curl htop \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Development utilities
RUN pip install ipython ipdb pytest-watch

# Mount source code as volume
VOLUME ["/app"]

# Development command
CMD ["uvicorn", "api.full_api:app", "--reload", "--host", "0.0.0.0"]
```

Build and run:
```bash
docker build -f Dockerfile.dev -t aia-dev .
docker run -v $(pwd)/aia_system:/app -p 8000:8000 aia-dev
```

## Architecture Overview

### System Components

```python
# Core system architecture
class AIASystem:
    """
    Main system orchestrator that manages all components.
    """
    
    def __init__(self):
        # Core Services
        self.agent_manager = AgentManager()
        self.task_orchestrator = TaskOrchestrator()
        self.venture_builder = VentureBuilder()
        self.economic_governor = EconomicGovernor()
        
        # Infrastructure
        self.knowledge_graph = KnowledgeGraph()
        self.event_bus = EventBus()
        self.cache = CacheManager()
        
        # AI Integration
        self.llm_manager = LLMManager()
        self.capability_matcher = CapabilityMatcher()
```

### Service Communication

```python
# Event-driven architecture
from dataclasses import dataclass
from typing import Any
import asyncio

@dataclass
class Event:
    type: str
    payload: Any
    timestamp: float
    source: str

class EventBus:
    def __init__(self):
        self.subscribers = {}
    
    async def publish(self, event: Event):
        """Publish event to all subscribers"""
        if event.type in self.subscribers:
            tasks = [
                subscriber(event) 
                for subscriber in self.subscribers[event.type]
            ]
            await asyncio.gather(*tasks)
    
    def subscribe(self, event_type: str, handler):
        """Subscribe to specific event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

# Usage example
event_bus = EventBus()

async def on_agent_registered(event: Event):
    print(f"New agent: {event.payload['agent_id']}")

event_bus.subscribe("agent.registered", on_agent_registered)
```

### Database Models

```python
# SQLAlchemy models
from sqlalchemy import Column, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    capabilities = Column(JSON, nullable=False)
    status = Column(String, default='idle')
    created_at = Column(DateTime, server_default=func.now())
    
    def match_score(self, requirements: dict) -> float:
        """Calculate capability match score"""
        score = 0.0
        for skill, required_level in requirements.items():
            agent_level = self.capabilities.get(skill, 0.0)
            if agent_level >= required_level:
                score += agent_level * required_level
        return score / len(requirements) if requirements else 0.0

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    requirements = Column(JSON, nullable=False)
    status = Column(String, default='pending')
    assigned_to = Column(String, ForeignKey('agents.id'))
    created_at = Column(DateTime, server_default=func.now())
```

## Core Concepts

### 1. Agent Capabilities

Agents have capabilities rated from 0.0 to 1.0:

```python
class AgentCapability:
    """
    Represents an agent's skill proficiency.
    
    Rating Scale:
    0.0-0.3: Beginner
    0.3-0.6: Intermediate
    0.6-0.8: Advanced
    0.8-1.0: Expert
    """
    
    def __init__(self, skill: str, rating: float):
        if not 0.0 <= rating <= 1.0:
            raise ValueError("Rating must be between 0.0 and 1.0")
        self.skill = skill
        self.rating = rating
    
    def meets_requirement(self, required: float) -> bool:
        """Check if capability meets requirement"""
        return self.rating >= required
    
    def improvement_potential(self) -> float:
        """Calculate room for improvement"""
        return 1.0 - self.rating

# Example usage
capabilities = {
    "python": AgentCapability("python", 0.95),
    "machine_learning": AgentCapability("machine_learning", 0.85),
    "frontend": AgentCapability("frontend", 0.60)
}
```

### 2. Task Assignment Algorithm

```python
class TaskAssignmentEngine:
    """
    Intelligent task assignment based on capabilities.
    """
    
    def assign_task(self, task: Task, agents: List[Agent]) -> Optional[Agent]:
        """
        Assign task to best matching available agent.
        
        Algorithm:
        1. Filter agents by availability
        2. Calculate match scores
        3. Apply preference weights
        4. Select highest scoring agent
        """
        available = [a for a in agents if a.status == 'idle']
        
        if not available:
            return None
        
        scores = []
        for agent in available:
            score = self.calculate_match_score(
                agent.capabilities,
                task.requirements
            )
            scores.append((agent, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        if scores and scores[0][1] > 0.7:  # Minimum threshold
            best_agent = scores[0][0]
            best_agent.status = 'busy'
            task.assigned_to = best_agent.id
            task.status = 'assigned'
            return best_agent
        
        return None
    
    def calculate_match_score(
        self, 
        capabilities: Dict[str, float],
        requirements: Dict[str, float]
    ) -> float:
        """
        Calculate weighted match score.
        
        Formula:
        score = Σ(min(capability, requirement) * weight) / Σ(weights)
        """
        if not requirements:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for skill, required_level in requirements.items():
            agent_level = capabilities.get(skill, 0.0)
            
            # Weighted by requirement importance
            weight = required_level
            
            # Score is minimum of capability and requirement
            skill_score = min(agent_level, required_level)
            
            total_score += skill_score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
```

### 3. Venture Lifecycle Management

```python
class VentureLifecycle:
    """
    Manages venture progression through phases.
    """
    
    PHASES = [
        "ideation",
        "validation", 
        "design",
        "development",
        "launch",
        "scale"
    ]
    
    def __init__(self, venture_id: str, budget: float, timeline_days: int):
        self.venture_id = venture_id
        self.budget = budget
        self.timeline_days = timeline_days
        self.current_phase = 0
        self.phase_tasks = {}
        self.phase_budgets = self.allocate_budget()
    
    def allocate_budget(self) -> Dict[str, float]:
        """
        Allocate budget across phases.
        
        Default allocation:
        - Ideation: 10%
        - Validation: 15%
        - Design: 20%
        - Development: 40%
        - Launch: 15%
        """
        allocations = {
            "ideation": 0.10,
            "validation": 0.15,
            "design": 0.20,
            "development": 0.40,
            "launch": 0.15
        }
        
        return {
            phase: self.budget * percentage
            for phase, percentage in allocations.items()
        }
    
    def create_phase_tasks(self, phase: str) -> List[Task]:
        """
        Generate tasks for a specific phase.
        """
        phase_templates = {
            "ideation": [
                ("Market research", {"research": 0.8, "analysis": 0.7}),
                ("Competitor analysis", {"research": 0.7, "strategy": 0.8}),
                ("Concept development", {"creativity": 0.9, "strategy": 0.7})
            ],
            "validation": [
                ("Customer interviews", {"communication": 0.8, "research": 0.7}),
                ("MVP planning", {"product_management": 0.9, "design": 0.6}),
                ("Technical feasibility", {"architecture": 0.8, "analysis": 0.7})
            ],
            "design": [
                ("System architecture", {"architecture": 0.95, "documentation": 0.7}),
                ("UI/UX design", {"ui_design": 0.9, "ux": 0.85}),
                ("Database design", {"database": 0.85, "architecture": 0.7})
            ],
            "development": [
                ("Backend development", {"backend": 0.9, "coding": 0.85}),
                ("Frontend development", {"frontend": 0.9, "coding": 0.85}),
                ("Integration testing", {"testing": 0.85, "debugging": 0.8}),
                ("Performance optimization", {"optimization": 0.8, "analysis": 0.7})
            ],
            "launch": [
                ("Deployment setup", {"devops": 0.9, "infrastructure": 0.85}),
                ("Marketing campaign", {"marketing": 0.85, "content": 0.7}),
                ("User onboarding", {"documentation": 0.7, "support": 0.8})
            ]
        }
        
        tasks = []
        for description, requirements in phase_templates.get(phase, []):
            task = Task(
                id=f"{self.venture_id}_{phase}_{len(tasks)}",
                description=description,
                requirements=requirements,
                phase=phase,
                venture_id=self.venture_id
            )
            tasks.append(task)
        
        return tasks
    
    def advance_phase(self) -> bool:
        """
        Move to next phase if current is complete.
        """
        if self.is_phase_complete():
            self.current_phase += 1
            if self.current_phase < len(self.PHASES):
                new_phase = self.PHASES[self.current_phase]
                self.phase_tasks[new_phase] = self.create_phase_tasks(new_phase)
                return True
        return False
    
    def is_phase_complete(self) -> bool:
        """
        Check if all tasks in current phase are complete.
        """
        current = self.PHASES[self.current_phase]
        tasks = self.phase_tasks.get(current, [])
        return all(task.status == 'completed' for task in tasks)
```

### 4. Economic Token System

```python
class TokenEconomy:
    """
    Manages dual-token economic system.
    """
    
    def __init__(self):
        self.balances = {}  # agent_id -> {aia: float, aia_gov: float}
        self.total_supply = {
            "aia": 1000000,
            "aia_gov": 100000
        }
        self.distribution_rate = 0.1  # 10% per cycle
    
    def initialize_agent(self, agent_id: str):
        """
        Set initial token balance for new agent.
        """
        self.balances[agent_id] = {
            "aia": 1000,  # Starting wage tokens
            "aia_gov": 100  # Starting governance tokens
        }
    
    def calculate_reward(
        self,
        agent_id: str,
        performance_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate token rewards based on performance.
        
        Metrics considered:
        - task_completion_rate
        - quality_score
        - collaboration_score
        - innovation_score
        """
        base_reward = 100
        
        # Performance multiplier
        perf_score = sum(performance_metrics.values()) / len(performance_metrics)
        multiplier = 1.0 + (perf_score - 0.5) * 2  # Range: 0-2x
        
        # Calculate rewards
        aia_reward = base_reward * multiplier
        aia_gov_reward = aia_reward * 0.1  # 10% governance tokens
        
        return {
            "aia": aia_reward,
            "aia_gov": aia_gov_reward
        }
    
    def distribute_rewards(self, distributions: List[Dict]):
        """
        Execute reward distribution.
        """
        for dist in distributions:
            agent_id = dist["agent_id"]
            rewards = dist["rewards"]
            
            if agent_id not in self.balances:
                self.initialize_agent(agent_id)
            
            self.balances[agent_id]["aia"] += rewards["aia"]
            self.balances[agent_id]["aia_gov"] += rewards["aia_gov"]
    
    def stake_tokens(
        self,
        agent_id: str,
        amount: float,
        duration_days: int
    ) -> Dict:
        """
        Stake tokens for governance participation.
        """
        if self.balances[agent_id]["aia_gov"] < amount:
            raise ValueError("Insufficient balance")
        
        # Lock tokens
        self.balances[agent_id]["aia_gov"] -= amount
        
        # Calculate APY based on duration
        apy = 0.05 + (duration_days / 365) * 0.07  # 5-12% APY
        
        return {
            "staked": amount,
            "apy": apy,
            "duration": duration_days,
            "estimated_reward": amount * apy * (duration_days / 365)
        }
```

## Integration Examples

### 1. Building a Custom Agent

```python
from aia_sdk import AIAClient, Agent, Capability

class CustomAgent:
    """
    Example of creating a specialized agent.
    """
    
    def __init__(self, client: AIAClient):
        self.client = client
        self.agent_id = None
    
    async def create(self):
        """
        Register custom agent with specific capabilities.
        """
        # Define capabilities
        capabilities = {
            "python": 0.95,
            "async_programming": 0.90,
            "api_design": 0.85,
            "database_optimization": 0.80,
            "microservices": 0.85,
            "docker": 0.80,
            "kubernetes": 0.75
        }
        
        # Register agent
        response = await self.client.agents.register(
            id="custom_backend_specialist",
            name="Backend Engineering Specialist",
            capabilities=capabilities,
            metadata={
                "specialization": "High-performance APIs",
                "preferred_stack": ["FastAPI", "PostgreSQL", "Redis"],
                "certifications": ["AWS Solutions Architect", "CKA"]
            }
        )
        
        self.agent_id = response["agent_id"]
        return self.agent_id
    
    async def accept_task(self, task_id: str):
        """
        Accept and start working on a task.
        """
        # Update task status
        await self.client.tasks.update(
            task_id=task_id,
            status="in_progress",
            assigned_to=self.agent_id
        )
        
        # Simulate work
        for progress in [0.25, 0.5, 0.75, 1.0]:
            await asyncio.sleep(1)  # Simulate work time
            
            await self.client.tasks.update_progress(
                task_id=task_id,
                progress=progress,
                notes=f"Completed {progress*100}% of implementation"
            )
        
        # Complete task
        await self.client.tasks.complete(
            task_id=task_id,
            result={
                "success": True,
                "deliverables": ["api_endpoints", "documentation"],
                "quality_score": 0.95
            }
        )

# Usage
async def main():
    client = AIAClient(api_key="your-key")
    agent = CustomAgent(client)
    
    # Create and register agent
    agent_id = await agent.create()
    print(f"Agent registered: {agent_id}")
    
    # Accept a task
    await agent.accept_task("task_001")
```

### 2. Automated Venture Creation

```python
class VentureAutomation:
    """
    Automate venture creation and management.
    """
    
    def __init__(self, client: AIAClient):
        self.client = client
    
    async def create_saas_venture(
        self,
        name: str,
        description: str,
        target_market: str,
        budget: float
    ):
        """
        Create a complete SaaS venture with all phases.
        """
        # Create venture
        venture = await self.client.ventures.create(
            name=name,
            description=description,
            budget=budget,
            timeline_days=90,
            objectives=[
                "Market research and validation",
                "MVP development",
                "User acquisition",
                "Revenue generation"
            ],
            target_market=target_market,
            success_metrics={
                "users": 1000,
                "mrr": 10000,
                "churn": 0.05
            }
        )
        
        venture_id = venture["venture_id"]
        
        # Monitor phase progression
        async def monitor_progress():
            while True:
                status = await self.client.ventures.get(venture_id)
                
                print(f"Phase: {status['current_phase']}")
                print(f"Progress: {status['progress']*100:.1f}%")
                print(f"Budget remaining: ${status['budget']['remaining']}")
                
                if status['status'] == 'completed':
                    break
                
                await asyncio.sleep(60)  # Check every minute
        
        # Start monitoring
        asyncio.create_task(monitor_progress())
        
        return venture_id
    
    async def optimize_team(self, venture_id: str):
        """
        Optimize team composition for venture.
        """
        # Get venture details
        venture = await self.client.ventures.get(venture_id)
        current_phase = venture["current_phase"]
        
        # Get required skills for phase
        phase_requirements = {
            "ideation": ["research", "strategy", "analysis"],
            "validation": ["user_research", "product_management"],
            "design": ["ui_design", "ux", "architecture"],
            "development": ["coding", "testing", "devops"],
            "launch": ["marketing", "support", "analytics"]
        }
        
        required_skills = phase_requirements.get(current_phase, [])
        
        # Find best agents
        agents = await self.client.agents.list(
            status="idle",
            skills=required_skills,
            min_capability=0.8
        )
        
        # Assign agents to venture
        for agent in agents["agents"][:5]:  # Max 5 agents
            await self.client.ventures.assign_agent(
                venture_id=venture_id,
                agent_id=agent["id"],
                role=f"{current_phase}_specialist"
            )
        
        return len(agents["agents"])
```

### 3. Knowledge Graph Queries

```python
class KnowledgeGraphAnalytics:
    """
    Advanced knowledge graph operations.
    """
    
    def __init__(self, client: AIAClient):
        self.client = client
    
    async def find_expert_network(self, skill: str, min_level: float = 0.8):
        """
        Find network of experts for a specific skill.
        """
        query = f"""
        MATCH (a:Agent)-[r:HAS_CAPABILITY]->(s:Skill {{name: '{skill}'}})
        WHERE r.level >= {min_level}
        OPTIONAL MATCH (a)-[c:COLLABORATED_WITH]-(other:Agent)
        RETURN a.id as expert,
               a.name as name,
               r.level as expertise,
               collect(DISTINCT other.id) as collaborators
        ORDER BY r.level DESC
        """
        
        result = await self.client.dkg.query(query)
        return result["results"]
    
    async def skill_gap_analysis(self, venture_id: str):
        """
        Identify skill gaps in venture team.
        """
        query = f"""
        MATCH (v:Venture {{id: '{venture_id}'}})-[:HAS_TASK]->(t:Task)
        MATCH (t)-[r:REQUIRES]->(s:Skill)
        OPTIONAL MATCH (a:Agent)-[:ASSIGNED_TO]->(t)
        OPTIONAL MATCH (a)-[h:HAS_CAPABILITY]->(s)
        RETURN s.name as skill,
               avg(r.level) as required_level,
               avg(h.level) as actual_level,
               count(DISTINCT t) as tasks_requiring,
               count(DISTINCT a) as agents_with_skill
        """
        
        results = await self.client.dkg.query(query)
        
        gaps = []
        for row in results["results"]:
            if row["actual_level"] < row["required_level"]:
                gaps.append({
                    "skill": row["skill"],
                    "gap": row["required_level"] - row["actual_level"],
                    "tasks_affected": row["tasks_requiring"]
                })
        
        return sorted(gaps, key=lambda x: x["gap"], reverse=True)
    
    async def collaboration_recommendations(self, agent_id: str):
        """
        Recommend agents for collaboration.
        """
        query = f"""
        MATCH (a:Agent {{id: '{agent_id}'}})-[:HAS_CAPABILITY]->(s:Skill)
        MATCH (other:Agent)-[:HAS_CAPABILITY]->(s)
        WHERE other.id <> '{agent_id}'
        AND NOT (a)-[:COLLABORATED_WITH]-(other)
        WITH other, count(s) as shared_skills
        WHERE shared_skills > 2
        RETURN other.id as agent_id,
               other.name as name,
               shared_skills,
               collect(s.name) as common_skills
        ORDER BY shared_skills DESC
        LIMIT 5
        """
        
        return await self.client.dkg.query(query)
```

### 4. Real-time Event Handling

```python
class EventStreamHandler:
    """
    Handle real-time system events.
    """
    
    def __init__(self, client: AIAClient):
        self.client = client
        self.handlers = {}
    
    def on(self, event_type: str):
        """
        Decorator for event handlers.
        """
        def decorator(func):
            self.handlers[event_type] = func
            return func
        return decorator
    
    async def start(self):
        """
        Start listening to event stream.
        """
        async for event in self.client.events.stream():
            if event["type"] in self.handlers:
                await self.handlers[event["type"]](event["data"])

# Usage
handler = EventStreamHandler(client)

@handler.on("task.completed")
async def on_task_completed(data):
    print(f"Task {data['task_id']} completed by {data['agent_id']}")
    print(f"Quality score: {data['quality_score']}")
    
    # Trigger follow-up actions
    if data["quality_score"] > 0.9:
        # Bonus reward for high quality
        await client.economic.bonus(
            agent_id=data["agent_id"],
            amount=50,
            reason="High quality delivery"
        )

@handler.on("venture.phase_completed")
async def on_phase_completed(data):
    print(f"Venture {data['venture_id']} completed phase: {data['phase']}")
    
    # Advance to next phase
    await client.ventures.advance_phase(data["venture_id"])

# Start listening
await handler.start()
```

## Common Use Cases

### 1. Automated Software Development

```python
async def automated_development_pipeline(
    project_name: str,
    requirements: List[str],
    tech_stack: List[str]
):
    """
    Fully automated software development pipeline.
    """
    client = AIAClient()
    
    # Create venture
    venture = await client.ventures.create(
        name=project_name,
        description=" ".join(requirements),
        budget=50000,
        timeline_days=60
    )
    
    # Phase 1: Requirements Analysis
    analysis_task = await client.tasks.submit(
        description="Analyze requirements and create specifications",
        requirements={"analysis": 0.9, "documentation": 0.8}
    )
    
    # Wait for completion
    await wait_for_task(analysis_task["task_id"])
    
    # Phase 2: Architecture Design
    design_task = await client.tasks.submit(
        description="Design system architecture",
        requirements={"architecture": 0.95, "system_design": 0.9}
    )
    
    # Phase 3: Implementation
    dev_tasks = []
    for component in ["backend", "frontend", "database"]:
        task = await client.tasks.submit(
            description=f"Implement {component}",
            requirements={component: 0.9, "coding": 0.85}
        )
        dev_tasks.append(task)
    
    # Parallel execution
    await asyncio.gather(*[
        wait_for_task(task["task_id"]) 
        for task in dev_tasks
    ])
    
    # Phase 4: Testing
    test_task = await client.tasks.submit(
        description="Comprehensive testing",
        requirements={"testing": 0.9, "qa": 0.85}
    )
    
    # Phase 5: Deployment
    deploy_task = await client.tasks.submit(
        description="Deploy to production",
        requirements={"devops": 0.9, "infrastructure": 0.85}
    )
    
    return venture["venture_id"]
```

### 2. Dynamic Team Scaling

```python
class DynamicTeamManager:
    """
    Automatically scale team based on workload.
    """
    
    def __init__(self, client: AIAClient):
        self.client = client
        self.scaling_threshold = 0.8  # 80% utilization
    
    async def monitor_and_scale(self):
        """
        Monitor system and scale team as needed.
        """
        while True:
            metrics = await self.client.metrics()
            
            utilization = metrics["agents"]["busy"] / metrics["agents"]["total"]
            pending_tasks = metrics["tasks"]["pending"]
            
            if utilization > self.scaling_threshold and pending_tasks > 10:
                # Need more agents
                await self.scale_up(pending_tasks)
            elif utilization < 0.3 and pending_tasks < 5:
                # Too many idle agents
                await self.scale_down()
            
            await asyncio.sleep(60)  # Check every minute
    
    async def scale_up(self, pending_tasks: int):
        """
        Add more agents to handle load.
        """
        # Analyze pending tasks
        tasks = await self.client.tasks.list(status="pending")
        
        # Determine required skills
        skill_demand = {}
        for task in tasks["tasks"]:
            for skill, level in task["requirements"].items():
                if skill not in skill_demand:
                    skill_demand[skill] = []
                skill_demand[skill].append(level)
        
        # Create specialized agents
        for skill, levels in skill_demand.items():
            avg_level = sum(levels) / len(levels)
            
            agent = await self.client.agents.register(
                id=f"auto_agent_{skill}_{int(time.time())}",
                name=f"Auto-scaled {skill} Specialist",
                capabilities={skill: min(avg_level + 0.1, 1.0)}
            )
            
            print(f"Created agent: {agent['agent_id']}")
    
    async def scale_down(self):
        """
        Deactivate idle agents.
        """
        agents = await self.client.agents.list(status="idle")
        
        # Deactivate agents idle for >1 hour
        for agent in agents["agents"]:
            if agent["idle_time"] > 3600:
                await self.client.agents.deactivate(agent["id"])
                print(f"Deactivated idle agent: {agent['id']}")
```

### 3. Quality Assurance Pipeline

```python
class QualityAssurance:
    """
    Automated quality assurance system.
    """
    
    def __init__(self, client: AIAClient):
        self.client = client
        self.quality_threshold = 0.85
    
    async def review_task(self, task_id: str):
        """
        Perform quality review of completed task.
        """
        task = await self.client.tasks.get(task_id)
        
        # Create review tasks
        reviews = []
        
        # Code review
        if "coding" in task["requirements"]:
            review = await self.client.tasks.submit(
                description=f"Code review for {task_id}",
                requirements={"code_review": 0.9, "testing": 0.8},
                metadata={"original_task": task_id}
            )
            reviews.append(review)
        
        # Security review
        if "security" in task["requirements"] or "backend" in task["requirements"]:
            review = await self.client.tasks.submit(
                description=f"Security audit for {task_id}",
                requirements={"security": 0.95, "penetration_testing": 0.8},
                metadata={"original_task": task_id}
            )
            reviews.append(review)
        
        # Performance review
        review = await self.client.tasks.submit(
            description=f"Performance testing for {task_id}",
            requirements={"performance_testing": 0.85, "optimization": 0.8},
            metadata={"original_task": task_id}
        )
        reviews.append(review)
        
        # Wait for all reviews
        review_results = await asyncio.gather(*[
            self.wait_for_review(r["task_id"]) 
            for r in reviews
        ])
        
        # Calculate overall quality
        quality_score = sum(r["score"] for r in review_results) / len(review_results)
        
        return {
            "task_id": task_id,
            "quality_score": quality_score,
            "passed": quality_score >= self.quality_threshold,
            "reviews": review_results
        }
    
    async def wait_for_review(self, review_task_id: str):
        """
        Wait for review completion and get results.
        """
        while True:
            task = await self.client.tasks.get(review_task_id)
            if task["status"] == "completed":
                return task["result"]
            await asyncio.sleep(10)
```

## Best Practices

### 1. Error Handling

```python
from typing import Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class RobustClient:
    """
    Client with robust error handling.
    """
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = aiohttp.ClientSession()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None
    ):
        """
        Make API request with retry logic.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with self.session.request(
                method, url, json=data, headers=headers
            ) as response:
                if response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited. Retrying after {retry_after}s")
                    await asyncio.sleep(retry_after)
                    raise Exception("Rate limited")
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def close(self):
        """Clean up resources."""
        await self.session.close()
```

### 2. Testing

```python
import pytest
from unittest.mock import Mock, patch
import asyncio

class TestAgentSystem:
    """
    Test suite for agent system.
    """
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        client = AIAClient(api_key="test-key")
        yield client
        await client.close()
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, client):
        """Test agent registration flow."""
        # Mock response
        with patch.object(client, 'make_request') as mock_request:
            mock_request.return_value = {
                "status": "registered",
                "agent_id": "test_agent_001"
            }
            
            result = await client.agents.register(
                id="test_agent_001",
                name="Test Agent",
                capabilities={"testing": 0.9}
            )
            
            assert result["status"] == "registered"
            assert result["agent_id"] == "test_agent_001"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_task_assignment(self, client):
        """Test task assignment algorithm."""
        # Setup test data
        agents = [
            {"id": "a1", "capabilities": {"python": 0.9, "testing": 0.7}},
            {"id": "a2", "capabilities": {"python": 0.7, "testing": 0.9}},
            {"id": "a3", "capabilities": {"python": 0.5, "testing": 0.5}}
        ]
        
        task = {
            "requirements": {"testing": 0.8, "python": 0.6}
        }
        
        # Test assignment
        assigner = TaskAssigner()
        best_agent = assigner.find_best_match(task, agents)
        
        assert best_agent["id"] == "a2"  # Best testing score
    
    @pytest.mark.asyncio
    async def test_venture_lifecycle(self, client):
        """Test venture phase progression."""
        venture = VentureLifecycle(
            venture_id="test_venture",
            budget=10000,
            timeline_days=30
        )
        
        # Test phase progression
        assert venture.current_phase == 0
        assert venture.PHASES[venture.current_phase] == "ideation"
        
        # Create and complete tasks
        tasks = venture.create_phase_tasks("ideation")
        assert len(tasks) > 0
        
        # Mark tasks complete
        for task in tasks:
            task.status = "completed"
        
        venture.phase_tasks["ideation"] = tasks
        assert venture.is_phase_complete()
        
        # Advance phase
        advanced = venture.advance_phase()
        assert advanced
        assert venture.current_phase == 1
        assert venture.PHASES[venture.current_phase] == "validation"
```

### 3. Performance Optimization

```python
class PerformanceOptimizer:
    """
    Optimization strategies for better performance.
    """
    
    def __init__(self, client: AIAClient):
        self.client = client
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_agent_cached(self, agent_id: str):
        """
        Get agent with caching.
        """
        cache_key = f"agent:{agent_id}"
        
        # Check cache
        if cache_key in self.cache:
            cached, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached
        
        # Fetch and cache
        agent = await self.client.agents.get(agent_id)
        self.cache[cache_key] = (agent, time.time())
        return agent
    
    async def batch_operations(self, operations: List[dict]):
        """
        Execute operations in batches.
        """
        batch_size = 10
        results = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i+batch_size]
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*[
                self.execute_operation(op) for op in batch
            ])
            results.extend(batch_results)
        
        return results
    
    async def execute_operation(self, operation: dict):
        """
        Execute single operation.
        """
        op_type = operation["type"]
        
        if op_type == "register_agent":
            return await self.client.agents.register(**operation["params"])
        elif op_type == "submit_task":
            return await self.client.tasks.submit(**operation["params"])
        elif op_type == "create_venture":
            return await self.client.ventures.create(**operation["params"])
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    
    def optimize_task_requirements(self, requirements: dict) -> dict:
        """
        Optimize task requirements for better matching.
        """
        # Remove redundant requirements
        optimized = {}
        
        # Skill hierarchy (child implies parent)
        hierarchy = {
            "python": ["programming", "coding"],
            "react": ["javascript", "frontend"],
            "django": ["python", "backend"],
            "tensorflow": ["python", "machine_learning"]
        }
        
        for skill, level in requirements.items():
            # Check if covered by more specific skill
            covered = False
            for specific, general in hierarchy.items():
                if skill in general and specific in requirements:
                    covered = True
                    break
            
            if not covered:
                optimized[skill] = level
        
        return optimized
```

## Troubleshooting

### Common Issues and Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| Agent not assigned | Tasks remain pending | Check agent availability and capability match |
| Slow API responses | >500ms latency | Use caching, batch operations |
| Token distribution fails | No rewards received | Verify agent registration and performance metrics |
| Task stuck in progress | No completion after deadline | Check agent status, reassign if needed |
| Venture not advancing | Phase stuck | Ensure all phase tasks are completed |

### Debugging Tools

```python
class Debugger:
    """
    Debugging utilities for development.
    """
    
    @staticmethod
    async def trace_task_lifecycle(client: AIAClient, task_id: str):
        """
        Trace complete task lifecycle.
        """
        print(f"Tracing task: {task_id}")
        
        # Get task details
        task = await client.tasks.get(task_id)
        print(f"Status: {task['status']}")
        print(f"Requirements: {task['requirements']}")
        
        if task["assigned_to"]:
            # Get assigned agent
            agent = await client.agents.get(task["assigned_to"])
            print(f"Assigned to: {agent['name']}")
            print(f"Agent capabilities: {agent['capabilities']}")
            
            # Calculate match score
            score = calculate_match_score(
                agent["capabilities"],
                task["requirements"]
            )
            print(f"Match score: {score:.2f}")
        
        # Get task history
        events = await client.tasks.get_events(task_id)
        for event in events:
            print(f"{event['timestamp']}: {event['type']} - {event['description']}")
    
    @staticmethod
    def analyze_performance(metrics: dict):
        """
        Analyze system performance metrics.
        """
        # Agent utilization
        utilization = metrics["agents"]["busy"] / metrics["agents"]["total"]
        print(f"Agent Utilization: {utilization:.1%}")
        
        # Task throughput
        completion_rate = metrics["tasks"]["completed"] / metrics["tasks"]["total"]
        print(f"Task Completion Rate: {completion_rate:.1%}")
        
        # Identify bottlenecks
        if utilization > 0.9:
            print("⚠️ High agent utilization - consider scaling up")
        
        if metrics["tasks"]["pending"] > metrics["agents"]["total"] * 2:
            print("⚠️ Task backlog growing - add more agents")
        
        if metrics["performance"]["error_rate"] > 0.05:
            print("⚠️ High error rate - investigate failures")
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import redis
import json

class CacheManager:
    """
    Multi-layer caching system.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.local_cache = {}
    
    @lru_cache(maxsize=1000)
    def get_cached(self, key: str):
        """
        Memory cache with LRU eviction.
        """
        # Check local cache
        if key in self.local_cache:
            return self.local_cache[key]
        
        # Check Redis
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        
        return None
    
    def set_cached(self, key: str, value: any, ttl: int = 300):
        """
        Set value in both caches.
        """
        # Local cache
        self.local_cache[key] = value
        
        # Redis with TTL
        self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
    
    def invalidate(self, pattern: str):
        """
        Invalidate cache entries matching pattern.
        """
        # Clear local cache
        keys_to_delete = [
            k for k in self.local_cache.keys()
            if pattern in k
        ]
        for key in keys_to_delete:
            del self.local_cache[key]
        
        # Clear Redis
        for key in self.redis.scan_iter(f"*{pattern}*"):
            self.redis.delete(key)
```

### Connection Pooling

```python
class ConnectionPool:
    """
    Manage connection pool for better performance.
    """
    
    def __init__(self, max_connections: int = 10):
        self.pool = asyncio.Queue(maxsize=max_connections)
        self.semaphore = asyncio.Semaphore(max_connections)
    
    async def acquire(self):
        """
        Acquire connection from pool.
        """
        async with self.semaphore:
            if self.pool.empty():
                # Create new connection
                conn = await self.create_connection()
            else:
                conn = await self.pool.get()
            
            # Verify connection is alive
            if not await self.is_alive(conn):
                conn = await self.create_connection()
            
            return conn
    
    async def release(self, conn):
        """
        Return connection to pool.
        """
        if self.pool.full():
            await self.close_connection(conn)
        else:
            await self.pool.put(conn)
    
    async def create_connection(self):
        """Create new connection."""
        return aiohttp.ClientSession()
    
    async def is_alive(self, conn):
        """Check if connection is alive."""
        try:
            await conn.get("http://api.aia.system/health")
            return True
        except:
            return False
    
    async def close_connection(self, conn):
        """Close connection."""
        await conn.close()
```

---

**Documentation Version**: 1.0.0  
**Last Updated**: September 2024  
**SDK Version**: 2.0.0  
**API Version**: 2.0.0