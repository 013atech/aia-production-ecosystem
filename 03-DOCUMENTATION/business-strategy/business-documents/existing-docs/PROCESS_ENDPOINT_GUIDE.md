# 🚀 **Complete Guide: Using the `/process` Endpoint**

## **🎯 How the `/process` Endpoint Works**

Your MAS system uses **asynchronous processing** for complex AI analysis. Here's the complete workflow:

## **📋 Step-by-Step Process:**

### **1. Submit Processing Request**
```bash
curl -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Your text to analyze",
    "llm_provider": "gemini"
  }'
```

**Response:**
```json
{
  "simulation_id": "sim_abc123_20250911114425",
  "status": "processing",
  "message": "Full complexity simulation started",
  "endpoints": {
    "status": "/simulations/sim_abc123_20250911114425",
    "results": "/simulations/sim_abc123_20250911114425/results",
    "stream": "/simulations/sim_abc123_20250911114425/stream"
  }
}
```

### **2. Check Processing Status**
```bash
# Use the simulation_id from step 1
curl http://35.232.77.162/simulations/sim_abc123_20250911114425
```

**Response:**
```json
{
  "status": "completed|processing|pending",
  "progress": 90,
  "started_at": "2025-09-11T11:44:25.840734",
  "config": {
    "num_agents": 20,
    "agent_distribution": {"GLAC": 7, "TSGLA": 7, "TASA-NS-Alg": 6},
    "iterations": 100
  }
}
```

### **3. Get Final Results**
```bash
# Once status is "completed"
curl http://35.232.77.162/simulations/sim_abc123_20250911114425/results
```

**Response:**
```json
{
  "analysis_type": "general_analysis",
  "summary": "Processed using 20 agents",
  "key_findings": [
    "Convergence achieved after 100 iterations",
    "Consensus confidence: 0.82",
    "Processing time: 13.6 seconds"
  ],
  "metrics": {
    "convergence_rate": 0.949,
    "consensus_score": 0.932,
    "confidence_interval": [0.82, 0.93]
  }
}
```

---

## **💻 Practical Usage Examples**

### **🐍 Python Implementation**
```python
import requests
import time
import json

class MASProcessor:
    def __init__(self, base_url="http://35.232.77.162"):
        self.base_url = base_url
    
    def process_text(self, prompt, provider="gemini", wait_for_completion=True):
        """Process text and optionally wait for results"""
        
        # 1. Submit processing request
        response = requests.post(f"{self.base_url}/process", json={
            "prompt": prompt,
            "llm_provider": provider
        })
        
        if response.status_code != 200:
            raise Exception(f"Failed to submit: {response.text}")
        
        data = response.json()
        sim_id = data["simulation_id"]
        
        if not wait_for_completion:
            return {"simulation_id": sim_id, "status": "submitted"}
        
        # 2. Wait for completion
        while True:
            status_response = requests.get(f"{self.base_url}/simulations/{sim_id}")
            status_data = status_response.json()
            
            if status_data["status"] == "completed":
                break
            elif status_data["status"] == "failed":
                raise Exception("Processing failed")
            
            print(f"Progress: {status_data.get('progress', 0)}%")
            time.sleep(2)
        
        # 3. Get final results
        results_response = requests.get(f"{self.base_url}/simulations/{sim_id}/results")
        return results_response.json()

# Usage examples
mas = MASProcessor()

# Simple processing
result = mas.process_text("Explain AI ethics", provider="anthropic")
print("Analysis:", result["summary"])
print("Findings:", result["key_findings"])

# Complex analysis without waiting
job = mas.process_text("Complex market analysis...", wait_for_completion=False)
print(f"Job submitted: {job['simulation_id']}")
```

### **🟡 JavaScript/Node.js Implementation**
```javascript
class MASProcessor {
    constructor(baseUrl = 'http://35.232.77.162') {
        this.baseUrl = baseUrl;
    }
    
    async processText(prompt, provider = 'gemini') {
        // 1. Submit request
        const response = await fetch(`${this.baseUrl}/process`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                prompt,
                llm_provider: provider
            })
        });
        
        const data = await response.json();
        const simId = data.simulation_id;
        
        // 2. Poll for completion
        while (true) {
            const statusResponse = await fetch(`${this.baseUrl}/simulations/${simId}`);
            const statusData = await statusResponse.json();
            
            if (statusData.status === 'completed') {
                break;
            }
            
            console.log(`Progress: ${statusData.progress || 0}%`);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        // 3. Get results
        const resultsResponse = await fetch(`${this.baseUrl}/simulations/${simId}/results`);
        return await resultsResponse.json();
    }
}

// Usage
const mas = new MASProcessor();
const result = await mas.processText("Analyze blockchain technology");
console.log(result);
```

### **🔧 cURL Complete Workflow**
```bash
#!/bin/bash
# Complete workflow script

echo "🚀 Testing MAS System Processing Workflow"

# 1. Submit processing request
echo "📤 Submitting processing request..."
RESPONSE=$(curl -s -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the future of artificial intelligence",
    "llm_provider": "gemini",
    "context": "technology_analysis"
  }')

# Extract simulation ID
SIM_ID=$(echo "$RESPONSE" | jq -r '.simulation_id')
echo "📋 Simulation ID: $SIM_ID"

# 2. Monitor progress
echo "⏳ Monitoring progress..."
while true; do
    STATUS_RESPONSE=$(curl -s "http://35.232.77.162/simulations/$SIM_ID")
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
    PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.progress // 0')
    
    echo "Status: $STATUS, Progress: $PROGRESS%"
    
    if [ "$STATUS" = "completed" ]; then
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "❌ Processing failed"
        exit 1
    fi
    
    sleep 2
done

# 3. Get final results
echo "📊 Getting results..."
curl -s "http://35.232.77.162/simulations/$SIM_ID/results" | jq .

echo "✅ Processing complete!"
```

---

## **📊 Response Structure Explained**

### **Initial Response (Step 1):**
```json
{
  "simulation_id": "sim_abc123_20250911114425",    // ← Use this for status/results
  "status": "processing",                          // ← Current status
  "message": "Full complexity simulation started", // ← Confirmation message
  "configuration": {                               // ← Processing config
    "num_agents": 20,
    "agent_distribution": {"GLAC": 7, "TSGLA": 7, "TASA-NS-Alg": 6},
    "iterations": 100
  },
  "endpoints": {                                   // ← URLs for next steps
    "status": "/simulations/sim_abc123.../",       // ← Check progress
    "results": "/simulations/sim_abc123.../results", // ← Get final results
    "stream": "/simulations/sim_abc123.../stream"  // ← Real-time updates
  }
}
```

### **Status Response (Step 2):**
```json
{
  "status": "completed",                           // ← completed|processing|pending
  "progress": 90,                                 // ← Percentage complete
  "prompt": "Original prompt text",
  "started_at": "2025-09-11T11:44:25.840734",
  "config": {                                     // ← Processing configuration
    "num_agents": 20,
    "iterations": 100,
    "task": "general_analysis"
  }
}
```

### **Final Results (Step 3):**
```json
{
  "analysis_type": "general_analysis",            // ← Type of analysis performed
  "summary": "Processed using 20 agents",        // ← High-level summary
  "key_findings": [                              // ← Main insights
    "Convergence achieved after 100 iterations",
    "Consensus confidence: 0.82",
    "Processing time: 13.6 seconds"
  ],
  "metrics": {                                   // ← Detailed analytics
    "convergence_rate": 0.949,
    "consensus_score": 0.932,
    "confidence_interval": [0.82, 0.93]
  },
  "detailed_analysis": "...",                   // ← Full AI response (if available)
  "agent_contributions": {...}                  // ← Individual agent outputs
}
```

---

## **🎮 Advanced Usage Patterns**

### **1. Batch Processing**
```python
import asyncio
import aiohttp

async def batch_process_texts(prompts):
    """Process multiple texts concurrently"""
    async with aiohttp.ClientSession() as session:
        # Submit all requests
        sim_ids = []
        for prompt in prompts:
            async with session.post('http://35.232.77.162/process', 
                json={"prompt": prompt, "llm_provider": "gemini"}) as resp:
                data = await resp.json()
                sim_ids.append(data['simulation_id'])
        
        # Wait for all to complete
        results = []
        for sim_id in sim_ids:
            while True:
                async with session.get(f'http://35.232.77.162/simulations/{sim_id}') as resp:
                    status = await resp.json()
                    if status['status'] == 'completed':
                        break
                await asyncio.sleep(2)
            
            # Get results
            async with session.get(f'http://35.232.77.162/simulations/{sim_id}/results') as resp:
                results.append(await resp.json())
        
        return results

# Usage
prompts = [
    "Analyze market trends",
    "Evaluate technology risks", 
    "Design optimization strategy"
]
results = asyncio.run(batch_process_texts(prompts))
```

### **2. Real-time Streaming (If Available)**
```javascript
// WebSocket-style streaming (if endpoint supports it)
async function streamResults(simId) {
    const response = await fetch(`http://35.232.77.162/simulations/${simId}/stream`);
    const reader = response.body.getReader();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = new TextDecoder().decode(value);
        console.log('Stream update:', chunk);
    }
}
```

### **3. Error Handling Best Practices**
```python
def robust_process_text(prompt, max_retries=3):
    """Robust text processing with error handling"""
    
    for attempt in range(max_retries):
        try:
            # Submit request
            response = requests.post("http://35.232.77.162/process", 
                json={"prompt": prompt, "llm_provider": "gemini"},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            sim_id = data["simulation_id"]
            
            # Wait for completion with timeout
            start_time = time.time()
            timeout = 300  # 5 minutes
            
            while time.time() - start_time < timeout:
                status_response = requests.get(
                    f"http://35.232.77.162/simulations/{sim_id}",
                    timeout=10
                )
                status_data = status_response.json()
                
                if status_data["status"] == "completed":
                    # Get results
                    results_response = requests.get(
                        f"http://35.232.77.162/simulations/{sim_id}/results",
                        timeout=10
                    )
                    return results_response.json()
                    
                elif status_data["status"] == "failed":
                    raise Exception("Processing failed")
                
                time.sleep(2)
            
            raise TimeoutError("Processing timeout")
            
        except (requests.RequestException, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
            time.sleep(5)
```

---

## **🔍 Response Types & Use Cases**

### **📊 Analysis Types You'll Receive:**

| Analysis Type | Description | Use Case |
|---------------|-------------|----------|
| `general_analysis` | Standard text analysis | General prompts |
| `market_analysis` | Economic/financial focus | Business decisions |
| `technical_analysis` | Technical deep-dive | Engineering solutions |
| `strategic_planning` | Long-term planning | Business strategy |
| `risk_assessment` | Risk evaluation | Decision support |

### **📈 Metrics Explanation:**
- **`convergence_rate`**: How quickly agents reached consensus (0-1)
- **`consensus_score`**: Agreement level between agents (0-1)  
- **`confidence_interval`**: Reliability range of the analysis
- **`processing_time`**: Total computation time

---

## **🛠️ Integration Examples**

### **1. Web Application Integration**
```html
<!DOCTYPE html>
<html>
<head>
    <title>MAS System Integration</title>
</head>
<body>
    <div>
        <textarea id="prompt" placeholder="Enter your text to analyze..."></textarea>
        <select id="provider">
            <option value="gemini">Google Gemini</option>
            <option value="anthropic">Claude (Anthropic)</option>
            <option value="openai">GPT (OpenAI)</option>
        </select>
        <button onclick="processText()">Analyze</button>
    </div>
    
    <div id="status"></div>
    <div id="results"></div>

    <script>
        async function processText() {
            const prompt = document.getElementById('prompt').value;
            const provider = document.getElementById('provider').value;
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            
            try {
                // 1. Submit processing request
                statusDiv.innerHTML = '⏳ Submitting request...';
                const response = await fetch('http://35.232.77.162/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt, llm_provider: provider})
                });
                
                const data = await response.json();
                const simId = data.simulation_id;
                
                // 2. Poll for completion
                statusDiv.innerHTML = '🔄 Processing...';
                while (true) {
                    const statusResponse = await fetch(`http://35.232.77.162/simulations/${simId}`);
                    const statusData = await statusResponse.json();
                    
                    statusDiv.innerHTML = `🔄 Processing... ${statusData.progress || 0}%`;
                    
                    if (statusData.status === 'completed') {
                        break;
                    }
                    
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
                
                // 3. Get results
                const resultsResponse = await fetch(`http://35.232.77.162/simulations/${simId}/results`);
                const results = await resultsResponse.json();
                
                statusDiv.innerHTML = '✅ Complete!';
                resultsDiv.innerHTML = `
                    <h3>Analysis Results</h3>
                    <p><strong>Summary:</strong> ${results.summary}</p>
                    <p><strong>Confidence:</strong> ${results.metrics.consensus_score}</p>
                    <h4>Key Findings:</h4>
                    <ul>${results.key_findings.map(f => `<li>${f}</li>`).join('')}</ul>
                `;
                
            } catch (error) {
                statusDiv.innerHTML = `❌ Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

### **2. Command Line Tool**
```bash
#!/bin/bash
# mas-cli - Command line interface for MAS system

MAS_URL="http://35.232.77.162"

process_text() {
    local prompt="$1"
    local provider="${2:-gemini}"
    
    echo "🚀 Processing with MAS System..."
    echo "📝 Prompt: $prompt"
    echo "🤖 Provider: $provider"
    echo
    
    # Submit request
    RESPONSE=$(curl -s -X POST "$MAS_URL/process" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$prompt\", \"llm_provider\": \"$provider\"}")
    
    SIM_ID=$(echo "$RESPONSE" | jq -r '.simulation_id')
    
    if [ "$SIM_ID" = "null" ]; then
        echo "❌ Failed to submit request"
        echo "$RESPONSE" | jq .
        exit 1
    fi
    
    echo "📋 Simulation ID: $SIM_ID"
    echo "⏳ Processing..."
    
    # Wait for completion
    while true; do
        STATUS_RESPONSE=$(curl -s "$MAS_URL/simulations/$SIM_ID")
        STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
        PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.progress // 0')
        
        printf "\r🔄 Status: $STATUS, Progress: $PROGRESS%%"
        
        if [ "$STATUS" = "completed" ]; then
            echo
            break
        elif [ "$STATUS" = "failed" ]; then
            echo
            echo "❌ Processing failed"
            exit 1
        fi
        
        sleep 2
    done
    
    # Get results
    echo "📊 Results:"
    curl -s "$MAS_URL/simulations/$SIM_ID/results" | jq .
}

# Usage: ./mas-cli "Your prompt here" "gemini"
process_text "$1" "$2"
```

### **3. Production Integration Template**
```python
import os
import asyncio
from typing import Optional, Dict, Any
import aiohttp
import logging

class ProductionMASClient:
    def __init__(self, 
                 base_url: str = "http://35.232.77.162",
                 timeout: int = 300,
                 max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    async def process_text_async(self, 
                               prompt: str, 
                               provider: str = "gemini",
                               context: Optional[str] = None,
                               max_length: Optional[int] = None) -> Dict[Any, Any]:
        """
        Production-ready async text processing
        """
        async with aiohttp.ClientSession() as session:
            # Submit processing request
            payload = {
                "prompt": prompt,
                "llm_provider": provider
            }
            if context:
                payload["context"] = context
            if max_length:
                payload["max_length"] = max_length
            
            for attempt in range(self.max_retries):
                try:
                    # Submit request
                    async with session.post(f"{self.base_url}/process", 
                                          json=payload,
                                          timeout=30) as resp:
                        if resp.status != 200:
                            raise aiohttp.ClientError(f"HTTP {resp.status}")
                        
                        data = await resp.json()
                        sim_id = data["simulation_id"]
                    
                    # Poll for completion
                    start_time = asyncio.get_event_loop().time()
                    
                    while True:
                        if asyncio.get_event_loop().time() - start_time > self.timeout:
                            raise TimeoutError("Processing timeout")
                        
                        async with session.get(f"{self.base_url}/simulations/{sim_id}") as resp:
                            status_data = await resp.json()
                            
                            if status_data["status"] == "completed":
                                break
                            elif status_data["status"] == "failed":
                                raise Exception("Processing failed")
                        
                        await asyncio.sleep(2)
                    
                    # Get results
                    async with session.get(f"{self.base_url}/simulations/{sim_id}/results") as resp:
                        results = await resp.json()
                        
                    self.logger.info(f"Successfully processed prompt (sim_id: {sim_id})")
                    return results
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        self.logger.error(f"Failed after {self.max_retries} attempts: {e}")
                        raise e
                    
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    await asyncio.sleep(5)

# Usage in production
async def main():
    client = ProductionMASClient()
    
    result = await client.process_text_async(
        prompt="Analyze quarterly financial performance",
        provider="anthropic",
        context="financial_analysis"
    )
    
    print(f"Analysis: {result['summary']}")
    print(f"Confidence: {result['metrics']['consensus_score']}")

asyncio.run(main())
```

---

## **🚀 Quick Test Your Live System**

Run this command to test your system right now:

```bash
# Test basic processing
curl -X POST http://35.232.77.162/process \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello MAS System!", "llm_provider": "gemini"}' | jq .simulation_id

# Then check results (replace with your simulation_id)
curl http://35.232.77.162/simulations/[YOUR_SIM_ID]/results | jq .
```

**🎯 Your production MAS system is fully operational and ready for complex AI processing workflows!** 🎉

---

## **📞 Key Takeaways:**

1. **`/process`** returns a **simulation_id** immediately
2. **Use the simulation_id** to check status and get results  
3. **Process is asynchronous** - perfect for complex AI tasks
4. **Your system handles 20 agents** working together on each request
5. **Multiple LLM providers** available for different use cases

**🌟 Start processing with your live production system at `http://35.232.77.162`!**