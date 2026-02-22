"""Pricing API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.api.api_schemas import (
    PricingBreakdownResponse, PricingBreakdownCreate
)
from src.api.services.pricing_service import PricingService

router = APIRouter(prefix="/api/v1/pricing", tags=["Pricing"])


@router.post("/breakdown", response_model=PricingBreakdownResponse, status_code=201)
async def create_pricing_breakdown(
    pricing_data: PricingBreakdownCreate,
    db: Session = Depends(get_db)
):
    """Create a new pricing breakdown."""
    try:
        breakdown = PricingService.create_breakdown(db, pricing_data)
        return PricingBreakdownResponse.model_validate(breakdown)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/breakdown/{breakdown_id}", response_model=PricingBreakdownResponse)
async def get_pricing_breakdown(
    breakdown_id: int,
    db: Session = Depends(get_db)
):
    """Get pricing breakdown by ID."""
    breakdown = PricingService.get_breakdown(db, breakdown_id)
    if not breakdown:
        raise HTTPException(status_code=404, detail="Pricing breakdown not found")
    return PricingBreakdownResponse.model_validate(breakdown)


@router.get("/item/{item_id}", response_model=List[PricingBreakdownResponse])
async def get_breakdowns_by_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    """Get all pricing breakdowns for an RFP item."""
    breakdowns = PricingService.get_breakdowns_by_item(db, item_id)
    return [PricingBreakdownResponse.model_validate(breakdown) for breakdown in breakdowns]


@router.patch("/breakdown/{breakdown_id}", response_model=PricingBreakdownResponse)
async def update_pricing_breakdown(
    breakdown_id: int,
    material_cost: float = Query(None, ge=0),
    testing_cost: float = Query(None, ge=0),
    total_cost: float = Query(None, ge=0),
    cost_per_unit: float = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """Update pricing breakdown."""
    breakdown = PricingService.update_breakdown(
        db, breakdown_id, material_cost, testing_cost, total_cost, cost_per_unit
    )
    if not breakdown:
        raise HTTPException(status_code=404, detail="Pricing breakdown not found")
    return PricingBreakdownResponse.model_validate(breakdown)


@router.delete("/breakdown/{breakdown_id}", status_code=204)
async def delete_pricing_breakdown(
    breakdown_id: int,
    db: Session = Depends(get_db)
):
    """Delete pricing breakdown."""
    success = PricingService.delete_breakdown(db, breakdown_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pricing breakdown not found")
    return None


@router.get("/rfp/{rfp_id}/total")
async def get_rfp_total_cost(
    rfp_id: str,
    db: Session = Depends(get_db)
):
    """Get total cost for all items in an RFP."""
    total_cost = PricingService.get_total_cost_for_rfp(db, rfp_id)
    return {"rfp_id": rfp_id, "total_cost": total_cost, "currency": "INR"}
