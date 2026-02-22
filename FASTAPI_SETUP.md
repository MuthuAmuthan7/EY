# FastAPI Backend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
# Edit .env and add your Google API key
```

### 3. Initialize Database

```bash
python init_db.py
```

### 4. Run the API

#### Development Mode
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Access API Documentation

- **Interactive Docs (Swagger UI):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## Docker Deployment

### Run with Docker Compose

```bash
# Start FastAPI backend only
docker-compose up api

# Start with Streamlit web UI
docker-compose --profile web up

# Build images
docker-compose build

# Stop services
docker-compose down
```

### Environment Variables for Docker

Set `APP_TYPE` environment variable:
- `APP_TYPE=api` - Run FastAPI backend (default)
- `APP_TYPE=web` - Run Streamlit web UI

## Project Structure

```
src/
├── main.py                 # FastAPI application entry point
├── db/
│   ├── database.py        # Database configuration and session management
│   └── models.py          # SQLAlchemy database models
├── api/
│   ├── api_schemas.py     # Pydantic request/response schemas
│   ├── services/          # Business logic services
│   │   ├── rfp_service.py
│   │   ├── sku_service.py
│   │   ├── recommendation_service.py
│   │   ├── pricing_service.py
│   │   └── rfp_response_service.py
│   └── routes/            # API route handlers
│       ├── rfp_routes.py
│       ├── sku_routes.py
│       ├── recommendation_routes.py
│       ├── pricing_routes.py
│       ├── response_routes.py
│       └── health_routes.py
├── agents/                # LLM agents
├── services/              # Core domain services
└── llm/                   # LLM client and utilities
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### RFPs
- `GET /rfps` - List RFPs
- `POST /rfps` - Create RFP
- `GET /rfps/{rfp_id}` - Get specific RFP
- `PUT /rfps/{rfp_id}` - Update RFP
- `DELETE /rfps/{rfp_id}` - Delete RFP
- `GET /rfps/{rfp_id}/items` - Get RFP items
- `GET /rfps/{rfp_id}/test-requirements` - Get test requirements
- `GET /rfps/search/?q=query` - Search RFPs

### SKUs (Products)
- `GET /skus` - List SKUs
- `POST /skus` - Create SKU
- `GET /skus/{sku_id}` - Get specific SKU
- `PUT /skus/{sku_id}` - Update SKU
- `DELETE /skus/{sku_id}` - Delete SKU
- `GET /skus/category/{category}` - Get SKUs by category
- `GET /skus/search/?q=query` - Search SKUs

### Technical Recommendations
- `GET /recommendations/{id}` - Get recommendation
- `POST /recommendations` - Create recommendation
- `GET /recommendations/item/{item_id}` - Get recommendations for item
- `PATCH /recommendations/{id}` - Update recommendation
- `DELETE /recommendations/{id}` - Delete recommendation

### Pricing
- `GET /pricing/breakdown/{id}` - Get pricing breakdown
- `POST /pricing/breakdown` - Create pricing breakdown
- `GET /pricing/item/{item_id}` - Get pricing for item
- `PATCH /pricing/breakdown/{id}` - Update pricing
- `DELETE /pricing/breakdown/{id}` - Delete pricing
- `GET /pricing/rfp/{rfp_id}/total` - Get RFP total cost

### RFP Responses
- `GET /responses` - List responses
- `POST /responses` - Create response
- `GET /responses/{id}` - Get specific response
- `GET /responses/rfp/{rfp_id}` - Get response for RFP
- `PUT /responses/{id}` - Update response
- `POST /responses/{id}/submit` - Submit response
- `DELETE /responses/{id}` - Delete response
- `GET /responses/status/{status}` - Get responses by status

### Health & Info
- `GET /health` - Health check
- `GET /` - API information

## Database Models

### RFP
- rfp_id (PK)
- title
- source_url
- submission_deadline
- buyer
- summary
- raw_text
- created_at
- updated_at

### SKU
- sku_id (PK)
- product_name
- category
- description
- raw_record (JSON)
- created_at
- updated_at

### RFP Items
- item_id (PK)
- rfp_id (FK)
- description
- quantity
- unit
- specs (JSON)

### Technical Recommendations
- recommendation_id (PK)
- item_id (FK)
- top_skus (JSON)
- selected_sku_id
- spec_match_percent
- explanation

### Pricing Breakdown
- breakdown_id (PK)
- item_id (FK)
- material_cost
- testing_cost
- total_cost
- cost_per_unit
- currency

### RFP Responses
- response_id (PK)
- rfp_id (FK)
- status (draft/submitted/accepted/rejected)
- sales_summary
- technical_response (JSON)
- pricing_response (JSON)
- final_narrative
- created_at
- updated_at
- submitted_at

## Development

### Code Style

Format code with Black:
```bash
black src/
```

### Linting

Check code with Flake8:
```bash
flake8 src/
```

### Type Checking

Run MyPy:
```bash
mypy src/
```

### Testing

Run tests with pytest:
```bash
pytest tests/ -v
```

## Production Deployment

### Using Gunicorn with Uvicorn Workers

```bash
pip install gunicorn

gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Using PostgreSQL

Update `.env`:
```
DATABASE_URL=postgresql://user:password@db:5432/rfp_platform
```

Run database migrations:
```bash
alembic upgrade head
```

## Troubleshooting

### Database Connection Issues

```bash
# Reinitialize database
python init_db.py

# Check database file exists
ls -la rfp_platform.db
```

### Port Already in Use

```bash
# Change port in command
uvicorn src.main:app --port 8001
```

### Module Not Found Errors

```bash
# Ensure you're in project root and src is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` file
2. **CORS**: Configure allowed origins in production
3. **API Keys**: Store securely using environment variables
4. **Database**: Use PostgreSQL in production
5. **HTTPS**: Enable HTTPS with reverse proxy (nginx, etc.)

## Support

For issues and questions, please refer to the main README.md
