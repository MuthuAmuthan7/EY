"""API routes initialization."""
from . import (
    health_routes,
    rfp_routes,
    sku_routes,
    recommendation_routes,
    pricing_routes,
    response_routes,
    workflow_routes
)

__all__ = [
    'health_routes',
    'rfp_routes',
    'sku_routes',
    'recommendation_routes',
    'pricing_routes',
    'response_routes',
    'workflow_routes'
]