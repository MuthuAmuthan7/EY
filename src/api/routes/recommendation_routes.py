"""Technical recommendation API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.api.api_schemas import (
    TechnicalRecommendationResponse, TechnicalRecommendationCreate
)
from src.api.services.recommendation_service import TechnicalRecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["Technical Recommendations"])


@router.post("", response_model=TechnicalRecommendationResponse, status_code=201)
async def create_recommendation(
    rec_data: TechnicalRecommendationCreate,
    db: Session = Depends(get_db)
):
    """Create a new technical recommendation."""
    try:
        recommendation = TechnicalRecommendationService.create_recommendation(db, rec_data)
        return TechnicalRecommendationResponse.model_validate(recommendation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{recommendation_id}", response_model=TechnicalRecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Get recommendation by ID."""
    recommendation = TechnicalRecommendationService.get_recommendation(db, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return TechnicalRecommendationResponse.model_validate(recommendation)


@router.get("/item/{item_id}", response_model=List[TechnicalRecommendationResponse])
async def get_recommendations_by_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    """Get all recommendations for an RFP item."""
    recommendations = TechnicalRecommendationService.get_recommendations_by_item(db, item_id)
    return [TechnicalRecommendationResponse.model_validate(rec) for rec in recommendations]


@router.patch("/{recommendation_id}", response_model=TechnicalRecommendationResponse)
async def update_recommendation(
    recommendation_id: int,
    selected_sku_id: str = Query(None),
    explanation: str = Query(None),
    db: Session = Depends(get_db)
):
    """Update recommendation with selected SKU and explanation."""
    recommendation = TechnicalRecommendationService.update_recommendation(
        db, recommendation_id, selected_sku_id, explanation
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return TechnicalRecommendationResponse.model_validate(recommendation)


@router.delete("/{recommendation_id}", status_code=204)
async def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Delete recommendation."""
    success = TechnicalRecommendationService.delete_recommendation(db, recommendation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return None
