"""Pricing service for database operations."""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from src.db.models import PricingBreakdownModel
from src.api.api_schemas import PricingBreakdownCreate


class PricingService:
    """Service for pricing breakdown operations."""
    
    @staticmethod
    def create_breakdown(db: Session, pricing_data: PricingBreakdownCreate) -> PricingBreakdownModel:
        """Create a new pricing breakdown."""
        breakdown = PricingBreakdownModel(
            item_id=pricing_data.item_id,
            material_cost=pricing_data.material_cost,
            testing_cost=pricing_data.testing_cost,
            total_cost=pricing_data.total_cost,
            cost_per_unit=pricing_data.cost_per_unit,
            currency=pricing_data.currency
        )
        db.add(breakdown)
        db.commit()
        db.refresh(breakdown)
        return breakdown
    
    @staticmethod
    def get_breakdown(db: Session, breakdown_id: int) -> Optional[PricingBreakdownModel]:
        """Get pricing breakdown by ID."""
        return db.query(PricingBreakdownModel).filter(
            PricingBreakdownModel.breakdown_id == breakdown_id
        ).first()
    
    @staticmethod
    def get_breakdowns_by_item(db: Session, item_id: str) -> List[PricingBreakdownModel]:
        """Get all pricing breakdowns for an RFP item."""
        return db.query(PricingBreakdownModel).filter(
            PricingBreakdownModel.item_id == item_id
        ).all()
    
    @staticmethod
    def update_breakdown(
        db: Session,
        breakdown_id: int,
        material_cost: Optional[float] = None,
        testing_cost: Optional[float] = None,
        total_cost: Optional[float] = None,
        cost_per_unit: Optional[float] = None
    ) -> Optional[PricingBreakdownModel]:
        """Update pricing breakdown."""
        breakdown = db.query(PricingBreakdownModel).filter(
            PricingBreakdownModel.breakdown_id == breakdown_id
        ).first()
        if not breakdown:
            return None
        
        if material_cost is not None:
            breakdown.material_cost = material_cost
        if testing_cost is not None:
            breakdown.testing_cost = testing_cost
        if total_cost is not None:
            breakdown.total_cost = total_cost
        if cost_per_unit is not None:
            breakdown.cost_per_unit = cost_per_unit
        
        breakdown.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(breakdown)
        return breakdown
    
    @staticmethod
    def delete_breakdown(db: Session, breakdown_id: int) -> bool:
        """Delete pricing breakdown."""
        breakdown = db.query(PricingBreakdownModel).filter(
            PricingBreakdownModel.breakdown_id == breakdown_id
        ).first()
        if not breakdown:
            return False
        db.delete(breakdown)
        db.commit()
        return True
    
    @staticmethod
    def get_total_cost_for_rfp(db: Session, rfp_id: str) -> float:
        """Get total cost for all items in an RFP."""
        from src.db.models import RFPItemModel
        
        total = db.query(func.sum(PricingBreakdownModel.total_cost)).join(
            RFPItemModel,
            PricingBreakdownModel.item_id == RFPItemModel.item_id
        ).filter(RFPItemModel.rfp_id == rfp_id).scalar()
        
        return total or 0.0


from sqlalchemy import func
