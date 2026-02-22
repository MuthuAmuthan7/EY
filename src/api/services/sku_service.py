"""SKU service for database operations."""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from src.db.models import SKUModel, SKUFeatureModel, SKUPricingModel
from src.api.api_schemas import SKUCreate, SKUUpdate, SKUResponse


class SKUService:
    """Service for SKU operations."""
    
    @staticmethod
    def create_sku(db: Session, sku_data: SKUCreate) -> SKUModel:
        """Create a new SKU with features and pricing."""
        sku = SKUModel(
            sku_id=sku_data.sku_id,
            product_name=sku_data.product_name,
            category=sku_data.category,
            description=sku_data.description,
            raw_record=sku_data.raw_record
        )
        db.add(sku)
        db.flush()
        
        # Add features
        for feature in sku_data.features:
            feature_obj = SKUFeatureModel(
                sku_id=sku.sku_id,
                name=feature.name,
                value=feature.value,
                unit=feature.unit
            )
            db.add(feature_obj)
        
        # Add pricing
        for pricing in sku_data.pricing:
            pricing_obj = SKUPricingModel(
                sku_id=sku.sku_id,
                unit_price=pricing.unit_price,
                currency=pricing.currency
            )
            db.add(pricing_obj)
        
        db.commit()
        db.refresh(sku)
        return sku
    
    @staticmethod
    def get_sku(db: Session, sku_id: str) -> Optional[SKUModel]:
        """Get SKU by ID."""
        return db.query(SKUModel).filter(SKUModel.sku_id == sku_id).first()
    
    @staticmethod
    def get_all_skus(db: Session, skip: int = 0, limit: int = 10) -> tuple[List[SKUModel], int]:
        """Get all SKUs with pagination."""
        query = db.query(SKUModel)
        total = query.count()
        skus = query.offset(skip).limit(limit).all()
        return skus, total
    
    @staticmethod
    def get_skus_by_category(db: Session, category: str, skip: int = 0, limit: int = 10) -> tuple[List[SKUModel], int]:
        """Get SKUs by category."""
        query = db.query(SKUModel).filter(SKUModel.category.ilike(f"%{category}%"))
        total = query.count()
        skus = query.offset(skip).limit(limit).all()
        return skus, total
    
    @staticmethod
    def search_skus(db: Session, query_text: str, skip: int = 0, limit: int = 10) -> tuple[List[SKUModel], int]:
        """Search SKUs by product name or category."""
        query = db.query(SKUModel).filter(
            (SKUModel.product_name.ilike(f"%{query_text}%")) |
            (SKUModel.category.ilike(f"%{query_text}%")) |
            (SKUModel.description.ilike(f"%{query_text}%"))
        )
        total = query.count()
        skus = query.offset(skip).limit(limit).all()
        return skus, total
    
    @staticmethod
    def update_sku(db: Session, sku_id: str, sku_data: SKUUpdate) -> Optional[SKUModel]:
        """Update SKU."""
        sku = db.query(SKUModel).filter(SKUModel.sku_id == sku_id).first()
        if not sku:
            return None
        
        update_data = sku_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(sku, key, value)
        
        sku.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(sku)
        return sku
    
    @staticmethod
    def delete_sku(db: Session, sku_id: str) -> bool:
        """Delete SKU and all related data."""
        sku = db.query(SKUModel).filter(SKUModel.sku_id == sku_id).first()
        if not sku:
            return False
        db.delete(sku)
        db.commit()
        return True
    
    @staticmethod
    def get_sku_features(db: Session, sku_id: str) -> List[SKUFeatureModel]:
        """Get all features for a SKU."""
        return db.query(SKUFeatureModel).filter(SKUFeatureModel.sku_id == sku_id).all()
    
    @staticmethod
    def get_sku_pricing(db: Session, sku_id: str) -> List[SKUPricingModel]:
        """Get pricing for a SKU."""
        return db.query(SKUPricingModel).filter(SKUPricingModel.sku_id == sku_id).all()
