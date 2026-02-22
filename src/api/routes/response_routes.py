"""RFP Response API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.api.api_schemas import (
    RFPResponseDetail, RFPResponseCreate, RFPResponseUpdate, SearchResponse
)
from src.api.services.rfp_response_service import RFPResponseService

router = APIRouter(prefix="/api/v1/responses", tags=["RFP Responses"])


@router.post("", response_model=RFPResponseDetail, status_code=201)
async def create_response(
    response_data: RFPResponseCreate,
    db: Session = Depends(get_db)
):
    """Create a new RFP response."""
    try:
        response = RFPResponseService.create_response(db, response_data)
        return RFPResponseDetail.model_validate(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{response_id}", response_model=RFPResponseDetail)
async def get_response(
    response_id: int,
    db: Session = Depends(get_db)
):
    """Get RFP response by ID."""
    response = RFPResponseService.get_response(db, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="RFP response not found")
    return RFPResponseDetail.model_validate(response)


@router.get("/rfp/{rfp_id}", response_model=RFPResponseDetail)
async def get_response_by_rfp(
    rfp_id: str,
    db: Session = Depends(get_db)
):
    """Get RFP response by RFP ID."""
    response = RFPResponseService.get_response_by_rfp(db, rfp_id)
    if not response:
        raise HTTPException(status_code=404, detail="RFP response not found")
    return RFPResponseDetail.model_validate(response)


@router.get("", response_model=SearchResponse)
async def list_responses(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all RFP responses with pagination."""
    responses, total = RFPResponseService.get_all_responses(db, skip, limit)
    return SearchResponse(
        total=total,
        items=[RFPResponseDetail.model_validate(resp).model_dump() for resp in responses],
        skip=skip,
        limit=limit
    )


@router.get("/status/{status}", response_model=SearchResponse)
async def get_responses_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get RFP responses by status (draft, submitted, accepted, rejected)."""
    responses, total = RFPResponseService.get_responses_by_status(db, status, skip, limit)
    return SearchResponse(
        total=total,
        items=[RFPResponseDetail.model_validate(resp).model_dump() for resp in responses],
        skip=skip,
        limit=limit
    )


@router.put("/{response_id}", response_model=RFPResponseDetail)
async def update_response(
    response_id: int,
    response_data: RFPResponseUpdate,
    db: Session = Depends(get_db)
):
    """Update RFP response."""
    response = RFPResponseService.update_response(db, response_id, response_data)
    if not response:
        raise HTTPException(status_code=404, detail="RFP response not found")
    return RFPResponseDetail.model_validate(response)


@router.post("/{response_id}/submit", response_model=RFPResponseDetail)
async def submit_response(
    response_id: int,
    db: Session = Depends(get_db)
):
    """Submit an RFP response."""
    response = RFPResponseService.submit_response(db, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="RFP response not found")
    return RFPResponseDetail.model_validate(response)


@router.delete("/{response_id}", status_code=204)
async def delete_response(
    response_id: int,
    db: Session = Depends(get_db)
):
    """Delete RFP response."""
    success = RFPResponseService.delete_response(db, response_id)
    if not success:
        raise HTTPException(status_code=404, detail="RFP response not found")
    return None
