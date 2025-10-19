# AIA SYSTEM - Developer Integration Guide
## Advanced Intelligence Architecture Platform - API Integration & SDK Documentation

**Developer Integration Manual**
**Prepared for:** Software Engineers, Integration Developers, Solution Architects, Technical Partners
**Date:** October 3, 2025
**Version:** 4.0 API Documentation

---

## 🎯 DEVELOPER OVERVIEW

This comprehensive guide provides developers with everything needed to integrate with the AIA platform, build custom applications, and leverage the full power of the Advanced Intelligence Architecture system. The platform offers robust APIs, SDKs, and development tools for creating innovative analytics solutions.

### Platform Capabilities for Developers

**Core API Features**
- **RESTful APIs**: Complete CRUD operations with OpenAPI 3.0 specification
- **GraphQL Endpoint**: Flexible data querying with real-time subscriptions
- **WebSocket APIs**: Real-time bidirectional communication
- **Webhook System**: Event-driven integrations with external systems

**SDKs and Libraries**
- **Python SDK**: Full-featured SDK with async support
- **JavaScript/TypeScript SDK**: Browser and Node.js compatibility
- **React Components**: Pre-built UI components for data visualization
- **3D Visualization Library**: WebGL-based immersive analytics tools

**Development Environment**
- **Sandbox Environment**: Full-featured testing environment
- **API Explorer**: Interactive API documentation and testing
- **Code Examples**: Comprehensive example library
- **Developer Dashboard**: API usage analytics and debugging tools

---

## 🚀 QUICK START GUIDE

### Getting Started

**1. Developer Account Setup**
```bash
# Register for developer access
curl -X POST https://api.013a.tech/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@yourcompany.com",
    "company": "Your Company Name",
    "use_case": "Custom analytics integration"
  }'

# Verify email and complete registration
# Access developer dashboard at https://developers.013a.tech
```

**2. API Key Generation**
```bash
# Generate API key via dashboard or CLI
curl -X POST https://api.013a.tech/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Integration",
    "permissions": ["read", "write", "admin"],
    "expires_in": "1y"
  }'
```

**3. First API Call**
```python
import requests

# Initialize AIA API client
API_KEY = "aia_key_your_api_key_here"
BASE_URL = "https://api.013a.tech/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test API connection
response = requests.get(f"{BASE_URL}/health", headers=headers)
print(f"API Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### SDK Installation

**Python SDK**
```bash
# Install via pip
pip install aia-python-sdk

# Or install from source
git clone https://github.com/013atech/aia-python-sdk.git
cd aia-python-sdk
pip install -e .
```

**JavaScript/TypeScript SDK**
```bash
# Install via npm
npm install @013atech/aia-sdk

# Or via yarn
yarn add @013atech/aia-sdk

# TypeScript types included
npm install --save-dev @types/node
```

**React Components**
```bash
# Install React component library
npm install @013atech/aia-react-components

# Install peer dependencies
npm install react react-dom three @react-three/fiber
```

---

## 📚 API REFERENCE

### Authentication

**JWT Authentication**
```python
import requests

# Login and get JWT token
login_response = requests.post(
    "https://api.013a.tech/v1/auth/login",
    json={
        "email": "developer@yourcompany.com",
        "password": "your_secure_password"
    }
)

token_data = login_response.json()
jwt_token = token_data["access_token"]

# Use token in subsequent requests
headers = {"Authorization": f"Bearer {jwt_token}"}
```

**API Key Authentication**
```javascript
// API key authentication (recommended for server-side)
const AIA_API_KEY = 'aia_key_your_api_key_here';

const apiClient = axios.create({
  baseURL: 'https://api.013a.tech/v1',
  headers: {
    'Authorization': `Bearer ${AIA_API_KEY}`,
    'Content-Type': 'application/json'
  }
});
```

**OAuth 2.0 Flow**
```python
from aia_sdk import AIAOAuth2Client

# Initialize OAuth client
oauth_client = AIAOAuth2Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="https://yourapp.com/oauth/callback"
)

# Get authorization URL
auth_url = oauth_client.get_authorization_url(
    scope=["read", "write"],
    state="random_state_string"
)

# Exchange authorization code for access token
access_token = oauth_client.exchange_code_for_token(
    authorization_code="received_auth_code"
)
```

### Data Management API

**Data Source Operations**
```python
from aia_sdk import AIAClient

# Initialize client
client = AIAClient(api_key="your_api_key")

# List available data sources
data_sources = client.data_sources.list()

# Create new data source
new_source = client.data_sources.create({
    "name": "Sales Database",
    "type": "postgresql",
    "connection_string": "postgresql://user:pass@host:5432/db",
    "schema": {
        "tables": ["sales", "customers", "products"]
    }
})

# Upload CSV data
csv_source = client.data_sources.upload_csv(
    file_path="data/sales_data.csv",
    name="Q3 Sales Data",
    description="Quarterly sales performance data"
)
```

**Data Query API**
```python
# Execute SQL queries
query_result = client.data.query({
    "sql": "SELECT region, SUM(revenue) FROM sales GROUP BY region",
    "data_source_id": "ds_123456789"
})

# GraphQL query
graphql_result = client.data.graphql({
    "query": """
        query GetSalesData($startDate: Date!, $endDate: Date!) {
            sales(startDate: $startDate, endDate: $endDate) {
                id
                amount
                customer {
                    name
                    region
                }
                product {
                    name
                    category
                }
            }
        }
    """,
    "variables": {
        "startDate": "2025-01-01",
        "endDate": "2025-03-31"
    }
})
```

**Data Transformation API**
```python
# Apply data transformations
transformed_data = client.data.transform({
    "data_source_id": "ds_123456789",
    "operations": [
        {
            "type": "filter",
            "condition": "revenue > 1000"
        },
        {
            "type": "aggregate",
            "group_by": ["region", "product_category"],
            "measures": {
                "total_revenue": "SUM(revenue)",
                "avg_order_value": "AVG(order_value)"
            }
        },
        {
            "type": "sort",
            "columns": [{"column": "total_revenue", "order": "desc"}]
        }
    ]
})
```

### Visualization API

**3D Visualization Creation**
```python
# Create 3D scatter plot
scatter_viz = client.visualizations.create({
    "type": "scatter3d",
    "data_source_id": "ds_123456789",
    "config": {
        "x_axis": "revenue",
        "y_axis": "profit_margin",
        "z_axis": "customer_count",
        "color": "region",
        "size": "market_share",
        "title": "Regional Performance Analysis"
    },
    "styling": {
        "color_scale": "viridis",
        "point_size_range": [5, 20],
        "lighting": "standard",
        "background": "dark"
    }
})

# Create immersive network graph
network_viz = client.visualizations.create({
    "type": "network3d",
    "data_source_id": "ds_987654321",
    "config": {
        "nodes": {
            "id_column": "customer_id",
            "label_column": "customer_name",
            "size_column": "total_purchases",
            "color_column": "segment"
        },
        "edges": {
            "source_column": "customer_id",
            "target_column": "referrer_id",
            "weight_column": "referral_value"
        },
        "layout": "force_directed",
        "physics": {
            "gravity": 0.1,
            "repulsion": 1000,
            "spring_length": 100
        }
    }
})
```

**Visualization Sharing and Embedding**
```python
# Share visualization with permissions
shared_viz = client.visualizations.share(
    visualization_id="viz_123456789",
    permissions={
        "public": True,
        "embed_allowed": True,
        "download_allowed": False,
        "expires_in": "30d"
    }
)

# Get embed code
embed_code = client.visualizations.get_embed_code(
    visualization_id="viz_123456789",
    options={
        "width": 800,
        "height": 600,
        "interactive": True,
        "show_controls": True
    }
)
```

### Multi-Agent Orchestration API

**Agent Configuration**
```python
# Configure multi-agent system
agent_config = client.agents.configure({
    "agents": [
        {
            "name": "data_analyst",
            "type": "analytical",
            "capabilities": ["statistical_analysis", "pattern_recognition"],
            "priority": 1.0
        },
        {
            "name": "business_advisor",
            "type": "strategic",
            "capabilities": ["recommendation_generation", "risk_assessment"],
            "priority": 0.8
        },
        {
            "name": "market_researcher",
            "type": "contextual",
            "capabilities": ["external_data_integration", "trend_analysis"],
            "priority": 0.6
        }
    ],
    "orchestration": {
        "collaboration_mode": "collaborative",
        "consensus_threshold": 0.7,
        "timeout_seconds": 30
    }
})

# Execute multi-agent analysis
analysis_result = client.agents.analyze({
    "query": "What factors are driving the decline in Q3 sales?",
    "data_context": {
        "primary_dataset": "ds_123456789",
        "time_range": "2025-07-01 to 2025-09-30",
        "focus_areas": ["sales", "marketing", "customer_behavior"]
    },
    "output_format": "comprehensive_report"
})
```

**Real-time Agent Communication**
```python
import asyncio
from aia_sdk import AIAWebSocketClient

async def agent_communication_example():
    # Connect to WebSocket for real-time agent updates
    ws_client = AIAWebSocketClient(api_key="your_api_key")

    await ws_client.connect()

    # Subscribe to agent analysis updates
    await ws_client.subscribe("agent_analysis", {
        "analysis_id": "analysis_123456789"
    })

    # Listen for real-time updates
    async for message in ws_client.listen():
        if message["type"] == "agent_update":
            agent_name = message["data"]["agent_name"]
            progress = message["data"]["progress"]
            insight = message["data"]["insight"]

            print(f"Agent {agent_name}: {progress}% - {insight}")

        elif message["type"] == "analysis_complete":
            final_result = message["data"]["result"]
            print(f"Analysis complete: {final_result}")
            break

    await ws_client.disconnect()

# Run async function
asyncio.run(agent_communication_example())
```

---

## 🛠️ SDK USAGE EXAMPLES

### Python SDK Advanced Examples

**Complete Data Pipeline**
```python
from aia_sdk import AIAClient
import pandas as pd

# Initialize client
client = AIAClient(api_key="your_api_key")

class SalesAnalysisPipeline:
    def __init__(self, client):
        self.client = client

    async def run_pipeline(self, csv_file_path):
        # 1. Upload data
        data_source = await self.client.data_sources.upload_csv(
            file_path=csv_file_path,
            name="Sales Analysis Dataset",
            auto_detect_schema=True
        )

        # 2. Data cleaning and transformation
        cleaned_data = await self.client.data.transform({
            "data_source_id": data_source["id"],
            "operations": [
                {"type": "remove_nulls", "columns": ["revenue", "date"]},
                {"type": "convert_types", "conversions": {
                    "date": "datetime",
                    "revenue": "float"
                }},
                {"type": "add_column", "name": "quarter",
                 "expression": "EXTRACT(QUARTER FROM date)"}
            ]
        })

        # 3. Statistical analysis
        stats = await self.client.analytics.statistical_summary({
            "data_source_id": cleaned_data["id"],
            "columns": ["revenue", "profit", "customer_count"],
            "group_by": ["region", "quarter"]
        })

        # 4. Multi-agent analysis
        insights = await self.client.agents.analyze({
            "query": "Identify key factors driving sales performance",
            "data_context": {"data_source_id": cleaned_data["id"]},
            "analysis_depth": "comprehensive"
        })

        # 5. Create visualization
        viz = await self.client.visualizations.create({
            "type": "interactive_dashboard",
            "data_source_id": cleaned_data["id"],
            "components": [
                {
                    "type": "scatter3d",
                    "title": "Sales Performance by Region",
                    "config": {
                        "x": "revenue", "y": "profit", "z": "customer_count",
                        "color": "region", "size": "market_share"
                    }
                },
                {
                    "type": "time_series",
                    "title": "Revenue Trend",
                    "config": {"x": "date", "y": "revenue", "group_by": "region"}
                }
            ]
        })

        return {
            "data_source": data_source,
            "statistics": stats,
            "insights": insights,
            "visualization": viz
        }

# Usage
pipeline = SalesAnalysisPipeline(client)
result = await pipeline.run_pipeline("data/sales_q3_2025.csv")
```

**Custom Analytics Function**
```python
from aia_sdk.decorators import analytics_function, cache_result

@analytics_function(
    name="customer_lifetime_value",
    description="Calculate Customer Lifetime Value with churn prediction",
    parameters={
        "customer_data": {"type": "dataframe", "required": True},
        "prediction_months": {"type": "int", "default": 12},
        "discount_rate": {"type": "float", "default": 0.1}
    }
)
@cache_result(expiration=3600)  # Cache for 1 hour
def calculate_clv(customer_data, prediction_months=12, discount_rate=0.1):
    """
    Advanced CLV calculation with machine learning predictions
    """
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier

    # Feature engineering
    features = [
        'avg_order_value', 'purchase_frequency', 'days_since_last_purchase',
        'total_purchases', 'customer_age_days', 'support_tickets'
    ]

    X = customer_data[features]

    # Predict churn probability
    churn_model = RandomForestClassifier(n_estimators=100, random_state=42)
    # Assuming we have historical churn data for training
    y_churn = customer_data['churned'].fillna(0)
    churn_model.fit(X, y_churn)

    churn_probability = churn_model.predict_proba(X)[:, 1]

    # Calculate CLV
    monthly_revenue = customer_data['avg_order_value'] * customer_data['purchase_frequency']
    retention_rate = 1 - churn_probability

    clv = []
    for i in range(len(customer_data)):
        customer_clv = 0
        current_retention = retention_rate[i]

        for month in range(prediction_months):
            monthly_value = monthly_revenue.iloc[i] * (current_retention ** month)
            discounted_value = monthly_value / ((1 + discount_rate) ** month)
            customer_clv += discounted_value

        clv.append(customer_clv)

    return {
        "customer_id": customer_data['customer_id'].tolist(),
        "clv": clv,
        "churn_probability": churn_probability.tolist(),
        "monthly_revenue": monthly_revenue.tolist()
    }

# Register custom function with AIA platform
client.analytics.register_function(calculate_clv)

# Use the function in analysis
clv_results = await client.analytics.execute_function(
    function_name="customer_lifetime_value",
    parameters={
        "customer_data": customer_df,
        "prediction_months": 18,
        "discount_rate": 0.08
    }
)
```

### JavaScript SDK Examples

**React Integration**
```typescript
import React, { useState, useEffect } from 'react';
import { AIAClient, Visualization3D } from '@013atech/aia-react-components';

const SalesDashboard: React.FC = () => {
  const [client] = useState(new AIAClient({ apiKey: process.env.AIA_API_KEY }));
  const [visualizations, setVisualizations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load sales data
      const salesData = await client.data.query({
        sql: `
          SELECT
            region,
            product_category,
            SUM(revenue) as total_revenue,
            COUNT(*) as transaction_count,
            AVG(customer_satisfaction) as avg_satisfaction
          FROM sales
          WHERE date >= '2025-01-01'
          GROUP BY region, product_category
        `,
        dataSourceId: 'sales-database'
      });

      // Create 3D scatter visualization
      const scatterViz = await client.visualizations.create({
        type: 'scatter3d',
        data: salesData.data,
        config: {
          x: 'total_revenue',
          y: 'transaction_count',
          z: 'avg_satisfaction',
          color: 'region',
          size: 'total_revenue',
          title: 'Sales Performance Analysis'
        }
      });

      // Create network analysis
      const networkData = await client.analytics.networkAnalysis({
        nodes: 'customers',
        edges: 'transactions',
        nodeAttributes: ['total_spent', 'loyalty_score', 'region'],
        edgeAttributes: ['transaction_amount', 'date']
      });

      const networkViz = await client.visualizations.create({
        type: 'network3d',
        data: networkData,
        config: {
          layout: 'force_directed',
          nodeSize: 'total_spent',
          nodeColor: 'loyalty_score',
          edgeWidth: 'transaction_amount'
        }
      });

      setVisualizations([scatterViz, networkViz]);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div className="sales-dashboard">
      <h1>Sales Performance Dashboard</h1>

      <div className="visualization-grid">
        {visualizations.map((viz, index) => (
          <div key={index} className="viz-container">
            <Visualization3D
              visualization={viz}
              width={600}
              height={400}
              interactive={true}
              showControls={true}
              onDataPointClick={(point) => {
                console.log('Data point clicked:', point);
                // Handle interaction
              }}
            />
          </div>
        ))}
      </div>

      <div className="dashboard-controls">
        <button onClick={loadDashboardData}>
          Refresh Data
        </button>
        <button onClick={() => client.visualizations.share(visualizations[0].id)}>
          Share Dashboard
        </button>
      </div>
    </div>
  );
};

export default SalesDashboard;
```

**Node.js Backend Integration**
```javascript
const { AIAClient } = require('@013atech/aia-sdk');
const express = require('express');

const app = express();
const aiaClient = new AIAClient({ apiKey: process.env.AIA_API_KEY });

// Webhook endpoint for real-time data updates
app.post('/webhooks/data-update', async (req, res) => {
  try {
    const { dataSourceId, updateType, data } = req.body;

    // Process incoming data
    if (updateType === 'batch_insert') {
      await aiaClient.data.batchInsert({
        dataSourceId,
        records: data,
        upsert: true
      });

      // Trigger real-time visualization updates
      await aiaClient.realtime.broadcast({
        channel: `data-source-${dataSourceId}`,
        event: 'data_updated',
        payload: {
          recordCount: data.length,
          timestamp: new Date().toISOString()
        }
      });
    }

    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Webhook processing error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Custom analytics endpoint
app.post('/api/custom-analysis', async (req, res) => {
  try {
    const { query, dataSourceId, analysisType } = req.body;

    // Use multi-agent system for analysis
    const analysisResult = await aiaClient.agents.analyze({
      query,
      dataContext: { dataSourceId },
      analysisType,
      includeVisualization: true,
      outputFormat: 'json_with_insights'
    });

    res.json(analysisResult);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('AIA integration server running on port 3000');
});
```

---

## 🔗 WEBHOOKS AND REAL-TIME INTEGRATION

### Webhook Configuration

**Setting Up Webhooks**
```python
# Register webhook endpoint
webhook = client.webhooks.create({
    "url": "https://yourapp.com/webhooks/aia-events",
    "events": [
        "data_source.created",
        "data_source.updated",
        "visualization.shared",
        "analysis.completed",
        "alert.triggered"
    ],
    "secret": "your_webhook_secret",
    "headers": {
        "X-Custom-Header": "your-custom-value"
    }
})

# Webhook payload verification
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature for security"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, f"sha256={expected_signature}")
```

**Webhook Event Handlers**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhooks/aia-events', methods=['POST'])
def handle_aia_webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get('X-AIA-Signature')

    # Verify signature
    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        return jsonify({'error': 'Invalid signature'}), 401

    event_data = request.json
    event_type = event_data['type']

    if event_type == 'analysis.completed':
        handle_analysis_completed(event_data['data'])
    elif event_type == 'alert.triggered':
        handle_alert_triggered(event_data['data'])
    elif event_type == 'data_source.updated':
        handle_data_source_updated(event_data['data'])

    return jsonify({'status': 'processed'}), 200

def handle_analysis_completed(analysis_data):
    """Handle completed analysis events"""
    analysis_id = analysis_data['analysis_id']
    results = analysis_data['results']

    # Send notification to relevant team members
    notify_team(f"Analysis {analysis_id} completed with {len(results)} insights")

    # Update internal tracking systems
    update_analysis_tracking(analysis_id, 'completed', results)

def handle_alert_triggered(alert_data):
    """Handle triggered alerts"""
    alert_type = alert_data['alert_type']
    severity = alert_data['severity']
    message = alert_data['message']

    if severity == 'critical':
        send_pagerduty_alert(alert_type, message)
    else:
        send_slack_notification(alert_type, message)
```

### Real-time Data Streaming

**WebSocket Client Implementation**
```python
import asyncio
import websockets
import json

class AIARealtimeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.connection = None
        self.subscriptions = {}

    async def connect(self):
        """Connect to AIA WebSocket server"""
        uri = f"wss://realtime.013a.tech/ws?token={self.api_key}"
        self.connection = await websockets.connect(uri)
        print("Connected to AIA real-time server")

    async def subscribe(self, channel, filters=None):
        """Subscribe to real-time data channel"""
        message = {
            "type": "subscribe",
            "channel": channel,
            "filters": filters or {}
        }
        await self.connection.send(json.dumps(message))
        self.subscriptions[channel] = filters

    async def listen(self):
        """Listen for real-time messages"""
        async for message in self.connection:
            data = json.loads(message)
            yield data

    async def send_command(self, command, parameters=None):
        """Send command to server"""
        message = {
            "type": "command",
            "command": command,
            "parameters": parameters or {}
        }
        await self.connection.send(json.dumps(message))

# Usage example
async def realtime_dashboard():
    client = AIARealtimeClient("your_api_key")
    await client.connect()

    # Subscribe to live data updates
    await client.subscribe("sales_metrics", {
        "region": "US",
        "update_frequency": "1m"
    })

    # Subscribe to analysis progress
    await client.subscribe("analysis_progress", {
        "analysis_id": "analysis_123"
    })

    # Listen for updates
    async for message in client.listen():
        if message["channel"] == "sales_metrics":
            update_dashboard_metrics(message["data"])
        elif message["channel"] == "analysis_progress":
            update_progress_bar(message["data"]["progress"])

asyncio.run(realtime_dashboard())
```

---

## 🧪 TESTING AND DEVELOPMENT

### Development Environment Setup

**Local Development Setup**
```bash
# Clone development resources
git clone https://github.com/013atech/aia-sdk-examples.git
cd aia-sdk-examples

# Set up virtual environment
python3 -m venv aia-dev-env
source aia-dev-env/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Set environment variables
export AIA_API_KEY="your_sandbox_api_key"
export AIA_ENVIRONMENT="sandbox"
export AIA_BASE_URL="https://sandbox-api.013a.tech/v1"

# Run example applications
python examples/basic_data_analysis.py
python examples/3d_visualization_demo.py
python examples/multi_agent_analysis.py
```

**Docker Development Environment**
```dockerfile
# Dockerfile for AIA development
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install AIA SDK
RUN pip install aia-python-sdk

# Copy application code
COPY . .

# Set environment variables
ENV AIA_ENVIRONMENT=development
ENV AIA_BASE_URL=https://sandbox-api.013a.tech/v1

EXPOSE 8000

CMD ["python", "app.py"]
```

**Docker Compose for Full Stack Development**
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  aia-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AIA_API_KEY=${AIA_API_KEY}
      - AIA_ENVIRONMENT=development
    volumes:
      - .:/app
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: aia_dev
      POSTGRES_USER: aia_user
      POSTGRES_PASSWORD: aia_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - aia-app

volumes:
  postgres_data:
```

### Testing Framework

**Unit Testing with Pytest**
```python
import pytest
from unittest.mock import Mock, patch
from aia_sdk import AIAClient

class TestAIAIntegration:
    @pytest.fixture
    def client(self):
        return AIAClient(api_key="test_api_key", environment="test")

    @pytest.fixture
    def mock_response(self):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "success",
            "data": {"id": "test_123", "name": "Test Dataset"}
        }
        return mock_resp

    @patch('requests.post')
    def test_create_data_source(self, mock_post, client, mock_response):
        mock_post.return_value = mock_response

        result = client.data_sources.create({
            "name": "Test Dataset",
            "type": "csv",
            "file_path": "test_data.csv"
        })

        assert result["id"] == "test_123"
        assert result["name"] == "Test Dataset"
        mock_post.assert_called_once()

    @patch('requests.get')
    def test_list_visualizations(self, mock_get, client):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": [
                {"id": "viz_1", "type": "scatter3d"},
                {"id": "viz_2", "type": "network3d"}
            ]
        }

        visualizations = client.visualizations.list()

        assert len(visualizations) == 2
        assert visualizations[0]["type"] == "scatter3d"

    @pytest.mark.asyncio
    async def test_agent_analysis(self, client):
        with patch.object(client.agents, 'analyze') as mock_analyze:
            mock_analyze.return_value = {
                "insights": ["Revenue trending upward", "Q3 performance exceeded targets"],
                "confidence": 0.85,
                "recommendations": ["Increase marketing spend", "Expand to new regions"]
            }

            result = await client.agents.analyze({
                "query": "Analyze Q3 sales performance",
                "data_source_id": "ds_123"
            })

            assert len(result["insights"]) == 2
            assert result["confidence"] > 0.8
            assert "marketing" in result["recommendations"][0].lower()

    def test_error_handling(self, client):
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = {
                "error": "Invalid data format"
            }

            with pytest.raises(Exception) as exc_info:
                client.data_sources.create({"invalid": "data"})

            assert "Invalid data format" in str(exc_info.value)
```

**Integration Testing**
```python
import pytest
import asyncio
from aia_sdk import AIAClient

class TestAIAIntegration:
    @pytest.fixture(scope="class")
    def client(self):
        return AIAClient(
            api_key=os.getenv("AIA_TEST_API_KEY"),
            environment="sandbox"
        )

    @pytest.mark.integration
    def test_full_analysis_pipeline(self, client):
        """Test complete data analysis pipeline"""

        # 1. Upload test data
        data_source = client.data_sources.upload_csv(
            file_path="test_data/sales_sample.csv",
            name="Integration Test Dataset"
        )

        # 2. Transform data
        transformed = client.data.transform({
            "data_source_id": data_source["id"],
            "operations": [
                {"type": "filter", "condition": "revenue > 0"},
                {"type": "add_column", "name": "profit_margin",
                 "expression": "(revenue - cost) / revenue"}
            ]
        })

        # 3. Create visualization
        viz = client.visualizations.create({
            "type": "scatter3d",
            "data_source_id": transformed["id"],
            "config": {
                "x": "revenue", "y": "cost", "z": "profit_margin",
                "color": "region"
            }
        })

        # 4. Run analysis
        analysis = client.agents.analyze({
            "query": "What drives profitability?",
            "data_context": {"data_source_id": transformed["id"]}
        })

        # Assertions
        assert data_source["id"] is not None
        assert viz["type"] == "scatter3d"
        assert len(analysis["insights"]) > 0

        # Cleanup
        client.data_sources.delete(data_source["id"])
        client.visualizations.delete(viz["id"])

    @pytest.mark.performance
    def test_api_response_times(self, client):
        """Test API performance requirements"""
        import time

        start_time = time.time()
        health_check = client.health_check()
        response_time = time.time() - start_time

        assert health_check["status"] == "healthy"
        assert response_time < 0.5  # Should respond within 500ms
```

---

## 📝 BEST PRACTICES

### API Usage Guidelines

**Rate Limiting and Throttling**
```python
import time
from functools import wraps

def rate_limit(calls_per_second=10):
    """Decorator to implement client-side rate limiting"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

class OptimizedAIAClient:
    def __init__(self, api_key):
        self.client = AIAClient(api_key=api_key)

    @rate_limit(calls_per_second=5)
    def create_visualization(self, config):
        """Rate-limited visualization creation"""
        return self.client.visualizations.create(config)

    def batch_create_visualizations(self, configs):
        """Create multiple visualizations efficiently"""
        # Use batch API when available
        if hasattr(self.client.visualizations, 'batch_create'):
            return self.client.visualizations.batch_create(configs)

        # Fallback to individual calls with rate limiting
        results = []
        for config in configs:
            result = self.create_visualization(config)
            results.append(result)
        return results
```

**Error Handling and Retry Logic**
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class RobustAIAClient:
    def __init__(self, api_key, max_retries=3):
        self.api_key = api_key
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def make_request(self, method, endpoint, **kwargs):
        """Make robust HTTP request with error handling"""
        url = f"https://api.013a.tech/v1{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(e.response.headers.get('Retry-After', 60))
                print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.make_request(method, endpoint, **kwargs)
            else:
                raise Exception(f"API error: {e.response.status_code} - {e.response.text}")

        except requests.exceptions.ConnectionError:
            raise Exception("Failed to connect to AIA API. Please check your network connection.")

        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again.")
```

**Caching and Performance Optimization**
```python
import hashlib
import pickle
import redis
from functools import wraps

class CachedAIAClient:
    def __init__(self, api_key, redis_url="redis://localhost:6379"):
        self.client = AIAClient(api_key=api_key)
        self.cache = redis.from_url(redis_url)
        self.cache_ttl = 3600  # 1 hour default TTL

    def _get_cache_key(self, method_name, *args, **kwargs):
        """Generate cache key from method name and parameters"""
        key_data = f"{method_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def cached_method(self, cache_ttl=None):
        """Decorator for caching method results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self._get_cache_key(func.__name__, *args, **kwargs)

                # Try to get from cache
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    return pickle.loads(cached_result)

                # Execute method and cache result
                result = func(*args, **kwargs)
                ttl = cache_ttl or self.cache_ttl
                self.cache.setex(cache_key, ttl, pickle.dumps(result))

                return result
            return wrapper
        return decorator

    @cached_method(cache_ttl=7200)  # Cache for 2 hours
    def get_data_source_schema(self, data_source_id):
        """Get data source schema with caching"""
        return self.client.data_sources.get_schema(data_source_id)

    @cached_method(cache_ttl=1800)  # Cache for 30 minutes
    def get_statistical_summary(self, data_source_id, columns):
        """Get statistical summary with caching"""
        return self.client.analytics.statistical_summary({
            "data_source_id": data_source_id,
            "columns": columns
        })
```

### Security Best Practices

**API Key Management**
```python
import os
from cryptography.fernet import Fernet

class SecureAPIKeyManager:
    def __init__(self, key_file=".aia_key"):
        self.key_file = key_file
        self._encryption_key = self._get_or_create_encryption_key()

    def _get_or_create_encryption_key(self):
        """Get or create encryption key for API key storage"""
        key_file = f"{self.key_file}.enc"

        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict file permissions
            return key

    def store_api_key(self, api_key):
        """Securely store API key"""
        fernet = Fernet(self._encryption_key)
        encrypted_key = fernet.encrypt(api_key.encode())

        with open(self.key_file, 'wb') as f:
            f.write(encrypted_key)
        os.chmod(self.key_file, 0o600)

    def load_api_key(self):
        """Load and decrypt API key"""
        if not os.path.exists(self.key_file):
            raise Exception("API key file not found. Please run setup first.")

        fernet = Fernet(self._encryption_key)

        with open(self.key_file, 'rb') as f:
            encrypted_key = f.read()

        return fernet.decrypt(encrypted_key).decode()

# Usage
key_manager = SecureAPIKeyManager()
api_key = key_manager.load_api_key()
client = AIAClient(api_key=api_key)
```

---

## 🚀 DEPLOYMENT PATTERNS

### Production Deployment Best Practices

**Environment Configuration**
```python
import os
from pydantic import BaseSettings

class AIASettings(BaseSettings):
    """Configuration settings for AIA integration"""

    # API Configuration
    api_key: str
    base_url: str = "https://api.013a.tech/v1"
    timeout: int = 30
    max_retries: int = 3

    # Caching Configuration
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Performance Configuration
    max_concurrent_requests: int = 10
    request_rate_limit: float = 10.0  # requests per second

    # Security Configuration
    verify_ssl: bool = True
    api_key_rotation_days: int = 90

    class Config:
        env_file = ".env"
        env_prefix = "AIA_"

settings = AIASettings()
```

**Production Monitoring**
```python
import logging
import time
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps

# Prometheus metrics
API_REQUESTS_TOTAL = Counter('aia_api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
API_REQUEST_DURATION = Histogram('aia_api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('aia_active_connections', 'Active AIA connections')

def monitor_api_calls(func):
    """Decorator to monitor API calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        method = func.__name__
        endpoint = kwargs.get('endpoint', 'unknown')

        ACTIVE_CONNECTIONS.inc()

        try:
            result = func(*args, **kwargs)
            status = 'success'
            return result
        except Exception as e:
            status = 'error'
            logging.error(f"API call failed: {method} - {str(e)}")
            raise
        finally:
            duration = time.time() - start_time
            API_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            API_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
            ACTIVE_CONNECTIONS.dec()

    return wrapper

class ProductionAIAClient:
    def __init__(self, settings):
        self.client = AIAClient(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=settings.timeout
        )
        self.settings = settings

    @monitor_api_calls
    def create_visualization(self, config):
        return self.client.visualizations.create(config)

    @monitor_api_calls
    def analyze_data(self, query):
        return self.client.agents.analyze(query)
```

**Health Checks and Circuit Breaker**
```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful function execution"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed function execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
class ResilientAIAClient:
    def __init__(self, api_key):
        self.client = AIAClient(api_key=api_key)
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

    def safe_api_call(self, func, *args, **kwargs):
        """Make API call with circuit breaker protection"""
        return self.circuit_breaker.call(func, *args, **kwargs)

    def create_visualization(self, config):
        return self.safe_api_call(
            self.client.visualizations.create,
            config
        )
```

---

**Contact Information:**
Developer Relations Team
AIA Integration Support
Email: developers@013a.tech
Documentation: https://developers.013a.tech
GitHub: https://github.com/013atech/aia-sdk
Stack Overflow: https://stackoverflow.com/questions/tagged/aia-platform