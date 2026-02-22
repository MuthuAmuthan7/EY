"""Database models for RFP Platform."""

from sqlalchemy import Column, String, Float, DateTime, Text, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.database import Base


class RFPModel(Base):
    """RFP document database model."""
    
    __tablename__ = "rfps"
    
    rfp_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(500), index=True)
    source_url = Column(String(500))
    submission_deadline = Column(DateTime, index=True)
    buyer = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("RFPItemModel", back_populates="rfp", cascade="all, delete-orphan")
    test_requirements = relationship("RFPTestRequirementModel", back_populates="rfp", cascade="all, delete-orphan")
    responses = relationship("RFPResponseModel", back_populates="rfp", cascade="all, delete-orphan")


class RFPItemModel(Base):
    """RFP scope of supply items database model."""
    
    __tablename__ = "rfp_items"
    
    item_id = Column(String(50), primary_key=True, index=True)
    rfp_id = Column(String(50), ForeignKey("rfps.rfp_id"), index=True)
    description = Column(Text)
    quantity = Column(Float)
    unit = Column(String(100))
    specs = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rfp = relationship("RFPModel", back_populates="items")
    recommendations = relationship("TechnicalRecommendationModel", back_populates="rfp_item")


class RFPTestRequirementModel(Base):
    """RFP testing requirements database model."""
    
    __tablename__ = "rfp_test_requirements"
    
    test_id = Column(String(50), primary_key=True, index=True)
    rfp_id = Column(String(50), ForeignKey("rfps.rfp_id"), index=True)
    test_name = Column(String(255), index=True)
    description = Column(Text)
    required_standard = Column(String(255))
    frequency = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rfp = relationship("RFPModel", back_populates="test_requirements")


class SKUModel(Base):
    """Product SKU database model."""
    
    __tablename__ = "skus"
    
    sku_id = Column(String(50), primary_key=True, index=True)
    product_name = Column(String(500), index=True)
    category = Column(String(100), index=True)
    description = Column(Text, nullable=True)
    raw_record = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    features = relationship("SKUFeatureModel", back_populates="sku", cascade="all, delete-orphan")
    pricing = relationship("SKUPricingModel", back_populates="sku", cascade="all, delete-orphan")


class SKUFeatureModel(Base):
    """SKU features/specifications database model."""
    
    __tablename__ = "sku_features"
    
    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String(50), ForeignKey("skus.sku_id"), index=True)
    name = Column(String(255), index=True)
    value = Column(String(500))
    unit = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sku = relationship("SKUModel", back_populates="features")


class SKUPricingModel(Base):
    """SKU pricing database model."""
    
    __tablename__ = "sku_pricing"
    
    pricing_id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String(50), ForeignKey("skus.sku_id"), index=True)
    unit_price = Column(Float)
    currency = Column(String(10), default="INR")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sku = relationship("SKUModel", back_populates="pricing")


class TechnicalRecommendationModel(Base):
    """Technical recommendation for RFP items database model."""
    
    __tablename__ = "technical_recommendations"
    
    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(50), ForeignKey("rfp_items.item_id"), index=True)
    top_skus = Column(JSON, default=[])  # List of SKU matches with scores
    selected_sku_id = Column(String(50), nullable=True)
    spec_match_percent = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rfp_item = relationship("RFPItemModel", back_populates="recommendations")


class PricingBreakdownModel(Base):
    """Pricing breakdown for RFP response database model."""
    
    __tablename__ = "pricing_breakdowns"
    
    breakdown_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(50), ForeignKey("rfp_items.item_id"), index=True)
    material_cost = Column(Float)
    testing_cost = Column(Float)
    total_cost = Column(Float)
    cost_per_unit = Column(Float)
    currency = Column(String(10), default="INR")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RFPResponseModel(Base):
    """RFP response/proposal database model."""
    
    __tablename__ = "rfp_responses"
    
    response_id = Column(Integer, primary_key=True, autoincrement=True)
    rfp_id = Column(String(50), ForeignKey("rfps.rfp_id"), index=True)
    status = Column(String(50), default="draft", index=True)  # draft, submitted, accepted, rejected
    sales_summary = Column(Text, nullable=True)
    technical_response = Column(JSON, nullable=True)
    pricing_response = Column(JSON, nullable=True)
    final_narrative = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    
    # Relationships
    rfp = relationship("RFPModel", back_populates="responses")
