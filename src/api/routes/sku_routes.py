"""SKU API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.api.api_schemas import (
    SKUResponse, SKUCreate, SKUUpdate, SKUListResponse, SearchResponse
)
from src.api.services.sku_service import SKUService

router = APIRouter(prefix="/api/v1/skus", tags=["SKUs"])


@router.post("", response_model=SKUResponse, status_code=201)
async def create_sku(
    sku_data: SKUCreate,
    db: Session = Depends(get_db)
):
    """Create a new SKU with features and pricing."""
    try:
        sku = SKUService.create_sku(db, sku_data)
        return SKUResponse.model_validate(sku)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{sku_id}", response_model=SKUResponse)
async def get_sku(
    sku_id: str,
    db: Session = Depends(get_db)
):
    """Get SKU by ID."""
    sku = SKUService.get_sku(db, sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    return SKUResponse.model_validate(sku)


@router.get("", response_model=SearchResponse)
async def list_skus(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all SKUs with pagination."""
    skus, total = SKUService.get_all_skus(db, skip, limit)
    return SearchResponse(
        total=total,
        items=[SKUResponse.model_validate(sku).model_dump() for sku in skus],
        skip=skip,
        limit=limit
    )


@router.get("/category/{category}", response_model=SearchResponse)
async def get_skus_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get SKUs by category."""
    skus, total = SKUService.get_skus_by_category(db, category, skip, limit)
    return SearchResponse(
        total=total,
        items=[SKUResponse.model_validate(sku).model_dump() for sku in skus],
        skip=skip,
        limit=limit
    )


@router.get("/search/", response_model=SearchResponse)
async def search_skus(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search SKUs by product name, category, or description."""
    skus, total = SKUService.search_skus(db, q, skip, limit)
    return SearchResponse(
        total=total,
        items=[SKUResponse.model_validate(sku).model_dump() for sku in skus],
        skip=skip,
        limit=limit
    )


@router.put("/{sku_id}", response_model=SKUResponse)
async def update_sku(
    sku_id: str,
    sku_data: SKUUpdate,
    db: Session = Depends(get_db)
):
    """Update SKU."""
    sku = SKUService.update_sku(db, sku_id, sku_data)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    return SKUResponse.model_validate(sku)


@router.delete("/{sku_id}", status_code=204)
async def delete_sku(
    sku_id: str,
    db: Session = Depends(get_db)
):
    """Delete SKU and all related data."""
    success = SKUService.delete_sku(db, sku_id)
    if not success:
        raise HTTPException(status_code=404, detail="SKU not found")
    return None
