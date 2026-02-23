"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from src.db.database import init_db
from src.api.routes import (
    health_routes,
    rfp_routes,
    rfp_upload_routes,
    sku_routes,
    recommendation_routes,
    pricing_routes,
    response_routes,
    workflow_routes
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting RFP Automation Platform API")
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down RFP Automation Platform API")


# Create FastAPI app
app = FastAPI(
    title="RFP Automation Platform API",
    description="Automated Request for Proposal Processing with AI-Driven Agents",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)


# Custom exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Include routers
app.include_router(health_routes.router)
app.include_router(rfp_routes.router)
app.include_router(rfp_upload_routes.router)
app.include_router(sku_routes.router)
app.include_router(recommendation_routes.router)
app.include_router(pricing_routes.router)
app.include_router(response_routes.router)
app.include_router(workflow_routes.router)


# API documentation
@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RFP Automation Platform API",
        "version": "1.0.0",
        "description": "AI-driven automated RFP processing system",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "available_endpoints": {
            "Workflow": "/api/v1/workflow",
            "RFPs": "/api/v1/rfps",
            "SKUs": "/api/v1/skus",
            "Recommendations": "/api/v1/recommendations",
            "Pricing": "/api/v1/pricing",
            "Responses": "/api/v1/responses",
            "Health": "/api/v1/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
