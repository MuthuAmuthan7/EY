# Running the RFP Automation Platform

## Architecture Overview

The platform consists of two main components:

1. **FastAPI Backend** - RESTful API that handles all RFP processing, workflow orchestration, and data management
2. **Streamlit Web Frontend** - User interface that communicates with the API via HTTP requests

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Qdrant vector database
- Required API keys (Cohere, Google Gemini)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory with:

```
COHERE_API_KEY=your_cohere_key
GEMINI_API_KEY=your_gemini_key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_key
DATABASE_URL=sqlite:///./rfp_platform.db
LOG_LEVEL=INFO
```

### 3. Start Supporting Services (Qdrant)

```bash
docker-compose up -d
```

This starts:
- **Qdrant** vector database on port 6333
- **PostgreSQL** (if configured) for persistent storage

## Running the Application

### Option 1: Run API and Web App in Separate Terminals

#### Terminal 1: Start FastAPI Backend

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Terminal 2: Start Streamlit Frontend

```bash
streamlit run web/app.py
```

The web interface will be available at:
- **URL**: http://localhost:8501

### Option 2: Run with Docker Compose

```bash
docker-compose up
```

This will start both services with proper networking.

## API Endpoints

### Workflow Endpoints

The web app uses these workflow endpoints:

#### Scan for RFPs
```
GET /api/v1/workflow/scan-rfps
```

**Response:**
```json
[
  {
    "rfp_id": "RFP-2025-DEMO-001",
    "title": "Procurement of XLPE insulated armoured cables",
    "source_url": "https://...",
    "submission_deadline": "2026-05-22T00:00:00",
    "brief_summary": "Procurement of XLPE insulated armoured cables for 11 kV transmission..."
  }
]
```

#### Process RFP with Full Workflow
```
POST /api/v1/workflow/process-rfp/{rfp_id}
```

**Response:**
```json
{
  "rfp_id": "RFP-2025-DEMO-001",
  "rfp_summary": "Procurement of XLPE insulated armoured cables for 11 kV transmission network expansion. Total estimated value: INR 25 lakhs.",
  "final_product_table": [...],
  "pricing_table": [...],
  "narrative_summary": "Based on the RFP requirements..."
}
```

## Application Flow

### 1. RFP Discovery
- User clicks "🔍 Scan RFPs" button
- Web app calls `GET /api/v1/workflow/scan-rfps`
- API scans parsed RFP files and returns summaries
- Results displayed in table

### 2. RFP Selection
- User selects an RFP from the list
- Selected RFP ID stored in session state

### 3. Workflow Execution
- User clicks "▶️ Run AI Workflow" button
- Web app calls `POST /api/v1/workflow/process-rfp/{rfp_id}`
- API orchestrates workflow:
  - **Sales Agent**: Loads and validates RFP
  - **Technical Agent**: Matches products to specifications
  - **Pricing Agent**: Calculates costs and pricing
  - **Master Agent**: Combines outputs into final response
- Response returned and displayed in tabs

### 4. Results Display
- **Summary Tab**: RFP summary and AI-generated response narrative
- **Technical Match Tab**: Product recommendations with spec match percentages
- **Pricing Tab**: Cost breakdown and totals
- **Export**: Download results as JSON

## Troubleshooting

### API Connection Error
**Error**: "Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000"

**Solution**:
1. Ensure FastAPI is running: `python -m uvicorn src.main:app --host 0.0.0.0 --port 8000`
2. Check firewall settings
3. Verify `API_BASE_URL` in `web/app.py` matches your API endpoint

### RFP Not Found
**Error**: "Error scanning RFPs" or "RFP not found"

**Solution**:
1. Verify parsed RFP files exist in `data/rfps_parsed/`
2. Check file format (should be JSON)
3. Review API logs for detailed error

### Qdrant Connection Error
**Error**: "Cannot connect to Qdrant"

**Solution**:
1. Ensure Qdrant is running: `docker-compose up -d`
2. Check Qdrant URL in environment: `QDRANT_URL=http://localhost:6333`
3. Verify port 6333 is not blocked

### Database Initialization Error
**Error**: "Error initializing database"

**Solution**:
1. Ensure database path is writable
2. Check database URL in environment
3. Delete and recreate database: `rm rfp_platform.db`

## Development

### Build Vector Indexes
In the web app sidebar:
1. Click "🔧 Build Indexes"
2. Wait for completion
3. Check status in Qdrant collections

### View API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Enable Debug Logging
Add to environment:
```
LOG_LEVEL=DEBUG
```

## Performance Notes

- **RFP Scanning**: Typically 2-5 seconds for 10 RFPs
- **Full Workflow**: 30-60 seconds depending on RFP complexity
- **Pricing Calculations**: 10-20 seconds for 50+ items

## Key Files

- `src/main.py` - FastAPI application and routes registration
- `src/api/routes/workflow_routes.py` - Workflow API endpoints
- `web/app.py` - Streamlit web application
- `src/agents/graph.py` - Agent workflow orchestration
- `src/agents/master_agent.py` - Response generation

## API Architecture

```
HTTP Request (Streamlit)
        ↓
FastAPI Endpoint (workflow_routes.py)
        ↓
RFPWorkflow (graph.py)
        ↓
Agent Orchestration
├── Sales Agent (scan RFPs)
├── Technical Agent (spec matching)
├── Pricing Agent (cost calculation)
└── Master Agent (response generation)
        ↓
HTTP Response (JSON)
        ↓
Streamlit Display
```

## Next Steps

- Add authentication and user management
- Implement RFP response submission tracking
- Add webhook support for real-time updates
- Deploy to production with proper CORS configuration
- Add request/response caching for improved performance
