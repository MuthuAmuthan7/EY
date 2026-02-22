# Quick Start Guide

## The Problem (Solved)
The web app was calling Python functions directly instead of using API endpoints. This tight coupling made it difficult to scale and deploy independently.

## The Solution (Implemented)
Refactored the web app to call HTTP API endpoints using the `requests` library.

## Quick Setup (2 Steps)

### Step 1: Start the FastAPI Backend (Terminal 1)
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 2: Start the Streamlit Web App (Terminal 2)
```bash
streamlit run web/app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

  Network URL: http://localhost:8501
  External URL: http://<your-ip>:8501
```

## Using the Application

### 1. Scan for RFPs
- Click **"🔍 Scan RFPs"** button
- Web app sends: `GET /api/v1/workflow/scan-rfps`
- Displays table of available RFPs

### 2. Select an RFP
- Choose an RFP from the dropdown
- Example: `RFP-2025-DEMO-001 - Procurement of XLPE insulated armoured cables`

### 3. Run AI Workflow
- Click **"▶️ Run AI Workflow"** button
- Web app sends: `POST /api/v1/workflow/process-rfp/RFP-2025-DEMO-001`
- Shows progress: Sales → Technical → Pricing → Master agents
- Takes 30-60 seconds

### 4. View Results
- **Summary Tab**: RFP summary and AI-generated narrative
- **Technical Match Tab**: Product recommendations (95%+ match examples)
- **Pricing Tab**: Cost breakdown (Material, Testing, Total)
- **Download**: Export results as JSON

## What Changed Behind the Scenes

### Before
```python
# web/app.py - Direct function import
from src.agents.graph import run_sales_scan

rfps = run_sales_scan()  # ❌ Direct call, no API
```

### After
```python
# web/app.py - HTTP API call
import requests

response = requests.get("http://localhost:8000/api/v1/workflow/scan-rfps")
rfps = response.json()  # ✅ Via API endpoint
```

## API Endpoints Available

### 1. Scan RFPs
```bash
curl -X GET "http://localhost:8000/api/v1/workflow/scan-rfps"
```

### 2. Process RFP
```bash
curl -X POST "http://localhost:8000/api/v1/workflow/process-rfp/RFP-2025-DEMO-001"
```

### 3. API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### "Cannot connect to API"
**Problem**: Web app shows connection error

**Solution**:
1. Ensure FastAPI is running on port 8000
2. Check firewall settings
3. Verify API_BASE_URL in web/app.py matches your API location

```bash
# Check if API is running
curl http://localhost:8000/docs
```

### "RFP not found"
**Problem**: API returns 404 error

**Solution**:
1. Verify RFP file exists in `data/rfps_parsed/`
2. Check file format is JSON
3. RFP ID must match filename (without .json)

```bash
ls -la data/rfps_parsed/
```

### "Cannot connect to Qdrant"
**Problem**: API shows Qdrant connection error

**Solution**:
```bash
# Start Qdrant
docker-compose up -d

# Check status
docker ps | grep qdrant
```

## File Structure

```
/Users/muthuamuthan/Documents/EY/
├── src/
│   ├── main.py                          # FastAPI app (includes workflow routes)
│   ├── api/
│   │   ├── routes/
│   │   │   ├── workflow_routes.py       # ✅ NEW: API endpoints
│   │   │   ├── rfp_routes.py
│   │   │   └── ...
│   │   └── schema.py
│   ├── agents/
│   │   ├── graph.py                     # Workflow orchestrator
│   │   ├── master_agent.py
│   │   ├── sales_agent.py
│   │   ├── technical_agent.py
│   │   └── pricing_agent.py
│   └── ...
├── web/
│   └── app.py                           # ✅ MODIFIED: Now uses API
├── data/
│   └── rfps_parsed/                     # RFP JSON files
└── ...
```

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | REST API for agent orchestration |
| Frontend | Streamlit | Web interface for user interaction |
| Communication | HTTP/REST | API calls between frontend and backend |
| Agents | LangGraph | Agent orchestration and workflow |
| LLM | Cohere/Gemini | Language model for summaries and analysis |
| Vector DB | Qdrant | Vector storage for semantic search |
| Database | SQLite/PostgreSQL | Persistent data storage |

## Performance Expectations

- **RFP Scanning**: 2-5 seconds
- **RFP Processing**: 30-60 seconds per RFP
- **Technical Matching**: 10-15 seconds
- **Pricing Calculation**: 10-20 seconds

## Next Steps

1. ✅ **Verify Setup**: Run both services and test RFP scanning
2. ✅ **Test Workflow**: Process sample RFP and check results
3. ✅ **Check API Docs**: Visit http://localhost:8000/docs
4. ✅ **Review Results**: Check Summary, Technical, and Pricing tabs

## Documentation

- **RUNNING_THE_APP.md** - Full setup and configuration guide
- **API_INTEGRATION_GUIDE.md** - Detailed API documentation
- **IMPLEMENTATION_COMPLETE.md** - Complete implementation details
- **CHANGE_VERIFICATION.md** - Detailed change log

## Support

If you encounter issues:

1. Check API logs (Terminal 1)
2. Check Streamlit logs (Terminal 2)
3. Verify API is accessible: `curl http://localhost:8000/docs`
4. Check RFP files exist: `ls data/rfps_parsed/`
5. Review error messages in web app

## Example Output

### RFP Summary (What the agent provides)
```
Procurement of XLPE insulated armoured cables for 11 kV transmission network expansion. 
Total estimated value: INR 25 lakhs.
```

### Results Breakdown
- **Match Quality**: 95.5% average
- **Best Match**: 98.2%
- **Items**: 50
- **Material Cost**: ₹20,00,000.00
- **Testing Cost**: ₹1,25,000.00
- **Grand Total**: ₹21,25,000.00

## Architecture

```
┌─────────────────────────────────┐
│   Web Browser                   │
│   http://localhost:8501         │
└─────────────────┬───────────────┘
                  │
                  │ HTTP Requests
                  │
┌─────────────────▼───────────────┐
│   Streamlit Web App             │
│   web/app.py                    │
│                                 │
│  • RFP Discovery Section        │
│  • AI Workflow Section          │
│  • Results Display Section      │
└─────────────────┬───────────────┘
                  │
                  │ HTTP Requests
                  │ requests library
                  │
┌─────────────────▼───────────────┐
│   FastAPI Backend               │
│   src/main.py                   │
│   Port: 8000                    │
│                                 │
│  GET  /api/v1/workflow/scan-rfps│
│  POST /api/v1/workflow/...      │
│  GET  /api/v1/rfps              │
│  POST /api/v1/responses         │
└─────────────────┬───────────────┘
                  │
                  │ Orchestrates
                  │
┌─────────────────▼───────────────┐
│   Agent Workflow                │
│   src/agents/graph.py           │
│                                 │
│  • Sales Agent                  │
│  • Technical Agent              │
│  • Pricing Agent                │
│  • Master Agent                 │
└─────────────────────────────────┘
```

---

**You're all set!** The application now uses a proper API-driven architecture. Start with Step 1 above and follow the flow.
