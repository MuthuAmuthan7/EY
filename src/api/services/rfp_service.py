"""RFP service for database operations."""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from src.db.models import RFPModel, RFPItemModel, RFPTestRequirementModel
from src.api.api_schemas import RFPCreate, RFPUpdate, RFPResponse, RFPItemCreate, RFPTestRequirementCreate


class RFPService:
    """Service for RFP operations."""
    
    @staticmethod
    def create_rfp(db: Session, rfp_data: RFPCreate) -> RFPModel:
        """Create a new RFP with items and test requirements."""
        rfp = RFPModel(
            rfp_id=rfp_data.rfp_id,
            title=rfp_data.title,
            source_url=rfp_data.source_url,
            submission_deadline=rfp_data.submission_deadline,
            buyer=rfp_data.buyer,
            summary=rfp_data.summary,
            raw_text=rfp_data.raw_text
        )
        db.add(rfp)
        db.flush()
        
        # Add items
        for item in rfp_data.items:
            rfp_item = RFPItemModel(
                item_id=item.item_id,
                rfp_id=rfp.rfp_id,
                description=item.description,
                quantity=item.quantity,
                unit=item.unit,
                specs=item.specs
            )
            db.add(rfp_item)
        
        # Add test requirements
        for test_req in rfp_data.test_requirements:
            test = RFPTestRequirementModel(
                test_id=test_req.test_id,
                rfp_id=rfp.rfp_id,
                test_name=test_req.test_name,
                description=test_req.description,
                required_standard=test_req.required_standard,
                frequency=test_req.frequency
            )
            db.add(test)
        
        db.commit()
        db.refresh(rfp)
        return rfp
    
    @staticmethod
    def get_rfp(db: Session, rfp_id: str) -> Optional[RFPModel]:
        """Get RFP by ID."""
        return db.query(RFPModel).filter(RFPModel.rfp_id == rfp_id).first()
    
    @staticmethod
    def get_all_rfps(db: Session, skip: int = 0, limit: int = 10) -> tuple[List[RFPModel], int]:
        """Get all RFPs with pagination."""
        query = db.query(RFPModel)
        total = query.count()
        rfps = query.offset(skip).limit(limit).all()
        return rfps, total
    
    @staticmethod
    def search_rfps(db: Session, query_text: str, skip: int = 0, limit: int = 10) -> tuple[List[RFPModel], int]:
        """Search RFPs by title or summary."""
        query = db.query(RFPModel).filter(
            (RFPModel.title.ilike(f"%{query_text}%")) |
            (RFPModel.summary.ilike(f"%{query_text}%")) |
            (RFPModel.buyer.ilike(f"%{query_text}%"))
        )
        total = query.count()
        rfps = query.offset(skip).limit(limit).all()
        return rfps, total
    
    @staticmethod
    def update_rfp(db: Session, rfp_id: str, rfp_data: RFPUpdate) -> Optional[RFPModel]:
        """Update RFP."""
        rfp = db.query(RFPModel).filter(RFPModel.rfp_id == rfp_id).first()
        if not rfp:
            return None
        
        update_data = rfp_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rfp, key, value)
        
        rfp.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(rfp)
        return rfp
    
    @staticmethod
    def delete_rfp(db: Session, rfp_id: str) -> bool:
        """Delete RFP."""
        rfp = db.query(RFPModel).filter(RFPModel.rfp_id == rfp_id).first()
        if not rfp:
            return False
        db.delete(rfp)
        db.commit()
        return True
    
    @staticmethod
    def get_rfp_items(db: Session, rfp_id: str) -> List[RFPItemModel]:
        """Get all items for an RFP."""
        return db.query(RFPItemModel).filter(RFPItemModel.rfp_id == rfp_id).all()
    
    @staticmethod
    def get_rfp_test_requirements(db: Session, rfp_id: str) -> List[RFPTestRequirementModel]:
        """Get all test requirements for an RFP."""
        return db.query(RFPTestRequirementModel).filter(RFPTestRequirementModel.rfp_id == rfp_id).all()
