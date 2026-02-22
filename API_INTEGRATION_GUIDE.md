# API Integration Summary

## Changes Made

The web application has been completely refactored to use API endpoints instead of directly calling Python functions. This provides better separation of concerns and allows the API to be used independently.

## Before vs After

### Before (Direct Function Calls)
```python
# web/app.py - Direct imports and function calls
from src.agents.graph import run_sales_scan, run_full_workflow_for_rfp

rfps = run_sales_scan()  # Direct function call
final_response = run_full_workflow_for_rfp(rfp_id)  # Direct function call
```

**Issues:**
- Tight coupling between web app and agent code
- Both running in same process
- Difficult to scale
- API endpoints were not being used

### After (HTTP API Calls)
```python
# web/app.py - HTTP requests to API
import requests

API_BASE_URL = "http://localhost:8000/api/v1"
WORKFLOW_API = f"{API_BASE_URL}/workflow"

# Call via HTTP
response = requests.get(f"{WORKFLOW_API}/scan-rfps")
rfps = response.json()

response = requests.post(f"{WORKFLOW_API}/process-rfp/{rfp_id}")
final_response = response.json()
```

**Benefits:**
- Clean separation between frontend and backend
- API can be deployed independently
- Enables horizontal scaling
- Supports multiple client applications
- Better error handling and logging

## New API Endpoints

### 1. Scan RFPs
**Endpoint**: `GET /api/v1/workflow/scan-rfps`

**Used by**: RFP Discovery section

**Returns**: List of RFP overviews
```json
[
  {
    "rfp_id": "RFP-2025-DEMO-001",
    "title": "Procurement of XLPE insulated armoured cables",
    "source_url": "https://...",
    "submission_deadline": "2026-05-22T00:00:00",
    "brief_summary": "Procurement details..."
  }
]
```

### 2. Process RFP
**Endpoint**: `POST /api/v1/workflow/process-rfp/{rfp_id}`

**Used by**: AI Workflow section

**Returns**: Final RFP response with recommendations and pricing
```json
{
  "rfp_id": "RFP-2025-DEMO-001",
  "rfp_summary": "Procurement of XLPE insulated armoured cables...",
  "final_product_table": [
    {
      "rfp_item_id": "ITEM-001",
      "selected_sku_id": "SKU-12345",
      "product_name": "Product Name",
      "spec_match_percent": 95.5,
      "quantity": 100,
      "unit_price": 1000.0,
      "total_cost": 100000.0
    }
  ],
  "pricing_table": [
    {
      "rfp_item_id": "ITEM-001",
      "sku_id": "SKU-12345",
      "quantity": 100,
      "unit_price": 1000.0,
      "material_cost": 80000.0,
      "test_cost": 5000.0,
      "total_cost": 100000.0
    },
    {
      "rfp_item_id": "TOTAL",
      "sku_id": "",
      "quantity": 0,
      "unit_price": 0,
      "material_cost": 80000.0,
      "test_cost": 5000.0,
      "total_cost": 100000.0
    }
  ],
  "narrative_summary": "Based on the RFP requirements..."
}
```

## System Architecture

```
┌─────────────────────────────────────┐
│      Streamlit Web App              │
│   (web/app.py)                      │
│                                     │
│  - RFP Discovery Section            │
│  - Agent Workflow Section           │
│  - Results Display Section          │
└──────────────┬──────────────────────┘
               │
               │ HTTP Requests
               │ (requests library)
               ▼
┌─────────────────────────────────────┐
│     FastAPI Backend                 │
│   (src/main.py)                     │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Workflow Routes              │  │
│  │ (workflow_routes.py)         │  │
│  │                              │  │
│  │ GET  /scan-rfps              │  │
│  │ POST /process-rfp/{rfp_id}   │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│               ▼                     │
│  ┌──────────────────────────────┐  │
│  │ RFPWorkflow                  │  │
│  │ (src/agents/graph.py)        │  │
│  │                              │  │
│  │ - run_sales_scan()           │  │
│  │ - run_full_workflow_for_rfp()│  │
│  └────────────┬─────────────────┘  │
│               │                     │
│               ▼                     │
│  ┌──────────────────────────────┐  │
│  │ Agent Orchestration          │  │
│  │                              │  │
│  │ ├─ Sales Agent               │  │
│  │ ├─ Technical Agent           │  │
│  │ ├─ Pricing Agent             │  │
│  │ └─ Master Agent              │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Files Modified/Created

### New Files
- `src/api/routes/workflow_routes.py` - Workflow API endpoints

### Modified Files
- `src/main.py` - Added workflow_routes to router imports and app.include_router()
- `src/api/routes/__init__.py` - Added workflow_routes import
- `web/app.py` - Replaced direct function calls with HTTP requests

## Running the System

### Step 1: Start FastAPI Backend
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Output should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 2: Start Streamlit Frontend (New Terminal)
```bash
streamlit run web/app.py
```

Output should show:
```
You can now view your Streamlit app in your browser.
  Network URL: http://localhost:8501
```

## Configuration

The API base URL can be configured in `web/app.py`:

```python
# Default configuration
API_BASE_URL = "http://localhost:8000/api/v1"
WORKFLOW_API = f"{API_BASE_URL}/workflow"
```

Change `API_BASE_URL` if your API is running on a different host or port.

## Error Handling

The web app now properly handles API errors:

### Connection Error
```python
except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to API. Make sure the FastAPI server is running...")
```

### HTTP Errors
```python
except requests.exceptions.HTTPError as e:
    st.error(f"Error running workflow: {e.response.json().get('detail', str(e))}")
```

### General Errors
```python
except Exception as e:
    st.error(f"Error running workflow: {e}")
```

## Testing the API

### Using curl

Scan RFPs:
```bash
curl -X GET "http://localhost:8000/api/v1/workflow/scan-rfps"
```

Process RFP:
```bash
curl -X POST "http://localhost:8000/api/v1/workflow/process-rfp/RFP-2025-DEMO-001"
```

### Using Python requests

```python
import requests

# Scan RFPs
response = requests.get("http://localhost:8000/api/v1/workflow/scan-rfps")
rfps = response.json()
print(f"Found {len(rfps)} RFPs")

# Process RFP
response = requests.post("http://localhost:8000/api/v1/workflow/process-rfp/RFP-2025-DEMO-001")
result = response.json()
print(f"Processing completed: {result['rfp_id']}")
```

## Data Flow Example

1. **User clicks "🔍 Scan RFPs"**
   - Streamlit: `requests.get(f"{WORKFLOW_API}/scan-rfps")`
   - FastAPI: `GET /api/v1/workflow/scan-rfps` → `scan_rfps()`
   - Workflow: `get_workflow().run_sales_scan()`
   - Returns: List of RFP overviews as JSON

2. **User selects an RFP and clicks "▶️ Run AI Workflow"**
   - Streamlit: `requests.post(f"{WORKFLOW_API}/process-rfp/{rfp_id}")`
   - FastAPI: `POST /api/v1/workflow/process-rfp/{rfp_id}` → `process_rfp(rfp_id)`
   - Workflow: `get_workflow().run_full_workflow_for_rfp(rfp_id)`
   - Returns: Final response with recommendations and pricing as JSON

3. **Streamlit displays results**
   - Parse JSON response
   - Display in tabs (Summary, Technical Match, Pricing)
   - Provide download option

## Benefits of This Approach

✅ **Scalability**: API can be deployed separately and scaled independently
✅ **Flexibility**: Multiple clients can use the same API (web, mobile, other tools)
✅ **Maintainability**: Clear separation of concerns
✅ **Testability**: API endpoints can be tested independently
✅ **Robustness**: Better error handling and logging
✅ **Standard Protocol**: Uses standard HTTP/REST conventions
✅ **Documentation**: Auto-generated OpenAPI/Swagger docs at `/docs`

## Next Steps

- Add authentication and authorization
- Implement request/response caching
- Add webhook support for async processing
- Deploy API and web app to production
- Add more API endpoints for individual agent operations
