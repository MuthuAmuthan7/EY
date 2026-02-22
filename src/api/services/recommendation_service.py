"""Technical recommendation service for database operations."""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from src.db.models import TechnicalRecommendationModel
from src.api.api_schemas import TechnicalRecommendationCreate


class TechnicalRecommendationService:
    """Service for technical recommendation operations."""
    
    @staticmethod
    def create_recommendation(db: Session, rec_data: TechnicalRecommendationCreate) -> TechnicalRecommendationModel:
        """Create a new technical recommendation."""
        recommendation = TechnicalRecommendationModel(
            item_id=rec_data.item_id,
            top_skus=rec_data.top_skus,
            selected_sku_id=rec_data.selected_sku_id,
            spec_match_percent=rec_data.spec_match_percent,
            explanation=rec_data.explanation
        )
        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)
        return recommendation
    
    @staticmethod
    def get_recommendation(db: Session, recommendation_id: int) -> Optional[TechnicalRecommendationModel]:
        """Get recommendation by ID."""
        return db.query(TechnicalRecommendationModel).filter(
            TechnicalRecommendationModel.recommendation_id == recommendation_id
        ).first()
    
    @staticmethod
    def get_recommendations_by_item(db: Session, item_id: str) -> List[TechnicalRecommendationModel]:
        """Get all recommendations for an RFP item."""
        return db.query(TechnicalRecommendationModel).filter(
            TechnicalRecommendationModel.item_id == item_id
        ).all()
    
    @staticmethod
    def update_recommendation(
        db: Session,
        recommendation_id: int,
        selected_sku_id: Optional[str] = None,
        explanation: Optional[str] = None
    ) -> Optional[TechnicalRecommendationModel]:
        """Update recommendation."""
        recommendation = db.query(TechnicalRecommendationModel).filter(
            TechnicalRecommendationModel.recommendation_id == recommendation_id
        ).first()
        if not recommendation:
            return None
        
        if selected_sku_id:
            recommendation.selected_sku_id = selected_sku_id
        if explanation:
            recommendation.explanation = explanation
        
        recommendation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(recommendation)
        return recommendation
    
    @staticmethod
    def delete_recommendation(db: Session, recommendation_id: int) -> bool:
        """Delete recommendation."""
        recommendation = db.query(TechnicalRecommendationModel).filter(
            TechnicalRecommendationModel.recommendation_id == recommendation_id
        ).first()
        if not recommendation:
            return False
        db.delete(recommendation)
        db.commit()
        return True
