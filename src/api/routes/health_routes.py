"""Health and utility API routes."""

from fastapi import APIRouter
from datetime import datetime

from src.api.api_schemas import HealthCheckResponse

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        database="connected",
        timestamp=datetime.utcnow()
    )


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RFP Automation Platform - FastAPI Backend",
        "version": "1.0.0",
        "description": "Backend API for RFP processing with LLM integration",
        "docs": "/docs",
        "openapi_schema": "/openapi.json"
    }
