## 🚀 COMPREHENSIVE AIA DEEP INTEGRATION - PROJECT LEVEL

### 🔄 Automatic Session Protocol
For EVERY interaction in this project, Claude must:

1. **Initialize AIA Systems**:
   - Check AIA backend status (`localhost:8000/health`)
   - Auto-start if needed: `python3 -m uvicorn aia.main:app --host 0.0.0.0 --port 8000`
   - Load knowledge graph from `/Users/wXy/dev/Projects/aia/aia_knowledge_graph_v2_1759313796.json`
   - Activate multi-agent orchestration with cryptography agent as team leader

2. **Route ALL Prompts Through AIA**:
   - Technical tasks → `aia "technical: [PROMPT]" technical 2`
   - Business queries → `aia business: "analyze: [PROMPT]"`
   - Implementation → `aia-coding "[PROMPT]"` (with sprint planning)
   - Infrastructure → `aia deploy: "[PROMPT]"`

3. **Engage Full Agent Team** per @.claude/agents/aia.md workflow:
   - Cryptography Agent (Lead)
   - Main Orchestrator Agent
   - Software Development Agent
   - Code Reviewer
   - Production Readiness Assessor
   - GCP Deployment Orchestrator
   - ML Ops Specialist
   - Three.js UI Optimizer
   - All specialized agents as required

4. **Knowledge Graph Integration**:
   - Query DKG v3 (2,472+ atoms) for context
   - Apply historical project intelligence
   - Reference patterns and best practices

### ⚡ Enhanced Processing Rules
- **NEVER** process prompts without AIA integration first
- **ALWAYS** mention which agents were consulted
- **INCLUDE** confidence levels from AIA responses
- **SHOW** sprint plans for complex implementations
- **REFERENCE** knowledge graph insights in all responses

### 🛡️ Fallback Strategy
If AIA backend unavailable:
1. Display clear warning about reduced capabilities
2. Use local AIA CLI tools (`aia-coding`, `aia-code`)
3. Reference knowledge graph file directly
4. Recommend restarting AIA backend

### 📋 Legacy Compatibility
- use aia backend for all prompts-tasks, additionally use knowledge-graph
- query or process each prompt from me using aia backend
- use aia for all tasks processing. use @.claude/agents/aia.md as workflow.
- use aia backend for processing.  use @.claude/agents/aia.md as workflow.
- use aia to process my requests, tasks, etc.