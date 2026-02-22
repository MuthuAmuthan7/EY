"""RFP API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.db.database import get_db
from src.api.api_schemas import (
    RFPResponse, RFPCreate, RFPUpdate, RFPItemResponse,
    RFPTestRequirementResponse, SearchResponse, ErrorResponse
)
from src.api.services.rfp_service import RFPService

router = APIRouter(prefix="/api/v1/rfps", tags=["RFPs"])


@router.post("", response_model=RFPResponse, status_code=201)
async def create_rfp(
    rfp_data: RFPCreate,
    db: Session = Depends(get_db)
):
    """Create a new RFP with items and test requirements."""
    try:
        rfp = RFPService.create_rfp(db, rfp_data)
        return RFPResponse.model_validate(rfp)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{rfp_id}", response_model=RFPResponse)
async def get_rfp(
    rfp_id: str,
    db: Session = Depends(get_db)
):
    """Get RFP by ID."""
    rfp = RFPService.get_rfp(db, rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return RFPResponse.model_validate(rfp)


@router.get("", response_model=SearchResponse)
async def list_rfps(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all RFPs with pagination."""
    rfps, total = RFPService.get_all_rfps(db, skip, limit)
    return SearchResponse(
        total=total,
        items=[RFPResponse.model_validate(rfp).model_dump() for rfp in rfps],
        skip=skip,
        limit=limit
    )


@router.get("/search/", response_model=SearchResponse)
async def search_rfps(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search RFPs by title, summary, or buyer."""
    rfps, total = RFPService.search_rfps(db, q, skip, limit)
    return SearchResponse(
        total=total,
        items=[RFPResponse.model_validate(rfp).model_dump() for rfp in rfps],
        skip=skip,
        limit=limit
    )


@router.put("/{rfp_id}", response_model=RFPResponse)
async def update_rfp(
    rfp_id: str,
    rfp_data: RFPUpdate,
    db: Session = Depends(get_db)
):
    """Update RFP."""
    rfp = RFPService.update_rfp(db, rfp_id, rfp_data)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return RFPResponse.model_validate(rfp)


@router.delete("/{rfp_id}", status_code=204)
async def delete_rfp(
    rfp_id: str,
    db: Session = Depends(get_db)
):
    """Delete RFP and all related data."""
    success = RFPService.delete_rfp(db, rfp_id)
    if not success:
        raise HTTPException(status_code=404, detail="RFP not found")
    return None


@router.get("/{rfp_id}/items", response_model=List[RFPItemResponse])
async def get_rfp_items(
    rfp_id: str,
    db: Session = Depends(get_db)
):
    """Get all items for an RFP."""
    rfp = RFPService.get_rfp(db, rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return [RFPItemResponse.model_validate(item) for item in RFPService.get_rfp_items(db, rfp_id)]


@router.get("/{rfp_id}/test-requirements", response_model=List[RFPTestRequirementResponse])
async def get_rfp_test_requirements(
    rfp_id: str,
    db: Session = Depends(get_db)
):
    """Get all test requirements for an RFP."""
    rfp = RFPService.get_rfp(db, rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return [RFPTestRequirementResponse.model_validate(test) for test in RFPService.get_rfp_test_requirements(db, rfp_id)]
