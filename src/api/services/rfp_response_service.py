"""RFP Response service for database operations."""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from src.db.models import RFPResponseModel
from src.api.api_schemas import RFPResponseCreate, RFPResponseUpdate


class RFPResponseService:
    """Service for RFP response operations."""
    
    @staticmethod
    def create_response(db: Session, response_data: RFPResponseCreate) -> RFPResponseModel:
        """Create a new RFP response."""
        response = RFPResponseModel(
            rfp_id=response_data.rfp_id,
            status=response_data.status,
            sales_summary=response_data.sales_summary,
            technical_response=response_data.technical_response,
            pricing_response=response_data.pricing_response,
            final_narrative=response_data.final_narrative
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        return response
    
    @staticmethod
    def get_response(db: Session, response_id: int) -> Optional[RFPResponseModel]:
        """Get RFP response by ID."""
        return db.query(RFPResponseModel).filter(
            RFPResponseModel.response_id == response_id
        ).first()
    
    @staticmethod
    def get_response_by_rfp(db: Session, rfp_id: str) -> Optional[RFPResponseModel]:
        """Get RFP response by RFP ID."""
        return db.query(RFPResponseModel).filter(
            RFPResponseModel.rfp_id == rfp_id
        ).first()
    
    @staticmethod
    def get_all_responses(db: Session, skip: int = 0, limit: int = 10) -> tuple[List[RFPResponseModel], int]:
        """Get all RFP responses with pagination."""
        query = db.query(RFPResponseModel)
        total = query.count()
        responses = query.offset(skip).limit(limit).all()
        return responses, total
    
    @staticmethod
    def get_responses_by_status(db: Session, status: str, skip: int = 0, limit: int = 10) -> tuple[List[RFPResponseModel], int]:
        """Get RFP responses by status."""
        query = db.query(RFPResponseModel).filter(RFPResponseModel.status == status)
        total = query.count()
        responses = query.offset(skip).limit(limit).all()
        return responses, total
    
    @staticmethod
    def update_response(db: Session, response_id: int, response_data: RFPResponseUpdate) -> Optional[RFPResponseModel]:
        """Update RFP response."""
        response = db.query(RFPResponseModel).filter(
            RFPResponseModel.response_id == response_id
        ).first()
        if not response:
            return None
        
        update_data = response_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(response, key, value)
        
        response.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(response)
        return response
    
    @staticmethod
    def submit_response(db: Session, response_id: int) -> Optional[RFPResponseModel]:
        """Mark response as submitted."""
        response = db.query(RFPResponseModel).filter(
            RFPResponseModel.response_id == response_id
        ).first()
        if not response:
            return None
        
        response.status = "submitted"
        response.submitted_at = datetime.utcnow()
        response.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(response)
        return response
    
    @staticmethod
    def delete_response(db: Session, response_id: int) -> bool:
        """Delete RFP response."""
        response = db.query(RFPResponseModel).filter(
            RFPResponseModel.response_id == response_id
        ).first()
        if not response:
            return False
        db.delete(response)
        db.commit()
        return True
