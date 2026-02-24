"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==================== RFP Schemas ====================

class RFPItemBase(BaseModel):
    """Base RFP item schema."""
    
    description: str = Field(..., description="Item description")
    quantity: float = Field(..., description="Required quantity", gt=0)
    unit: str = Field(..., description="Unit of measurement")
    specs: Dict[str, Any] = Field(default_factory=dict, description="Technical specifications")


class RFPItemCreate(RFPItemBase):
    """Create RFP item schema."""
    
    item_id: str = Field(..., description="Unique item identifier")


class RFPItemResponse(RFPItemBase):
    """RFP item response schema."""
    
    item_id: str
    rfp_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RFPTestRequirementBase(BaseModel):
    """Base RFP test requirement schema."""
    
    test_name: str = Field(..., description="Name of the test")
    description: str = Field(..., description="Test description")
    required_standard: str = Field(..., description="Required standard")
    frequency: Optional[str] = Field(None, description="Testing frequency")


class RFPTestRequirementCreate(RFPTestRequirementBase):
    """Create RFP test requirement schema."""
    
    test_id: str = Field(..., description="Unique test identifier")


class RFPTestRequirementResponse(RFPTestRequirementBase):
    """RFP test requirement response schema."""
    
    test_id: str
    rfp_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RFPBase(BaseModel):
    """Base RFP schema."""
    
    title: str = Field(..., description="RFP title")
    source_url: str = Field(..., description="Source URL")
    submission_deadline: datetime = Field(..., description="Submission deadline")
    buyer: Optional[str] = Field(None, description="Buyer organization")
    summary: Optional[str] = Field(None, description="RFP summary")


class RFPCreate(RFPBase):
    """Create RFP schema."""
    
    rfp_id: str = Field(..., description="Unique RFP identifier")
    raw_text: Optional[str] = Field(None, description="Raw RFP text")
    items: List[RFPItemCreate] = Field(default_factory=list)
    test_requirements: List[RFPTestRequirementCreate] = Field(default_factory=list)


class RFPUpdate(BaseModel):
    """Update RFP schema."""
    
    title: Optional[str] = None
    source_url: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    buyer: Optional[str] = None
    summary: Optional[str] = None
    raw_text: Optional[str] = None


class RFPResponse(RFPBase):
    """RFP response schema."""
    
    rfp_id: str
    raw_text: Optional[str]
    items: List[RFPItemResponse] = Field(default_factory=list)
    test_requirements: List[RFPTestRequirementResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RFPDetailResponse(RFPResponse):
    """Detailed RFP response with relationships."""
    
    items: List[RFPItemResponse]
    test_requirements: List[RFPTestRequirementResponse]


# ==================== SKU Schemas ====================

class SKUFeatureBase(BaseModel):
    """Base SKU feature schema."""
    
    name: str = Field(..., description="Feature name")
    value: str = Field(..., description="Feature value")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class SKUFeatureResponse(SKUFeatureBase):
    """SKU feature response schema."""
    
    feature_id: int
    
    class Config:
        from_attributes = True


class SKUPricingBase(BaseModel):
    """Base SKU pricing schema."""
    
    unit_price: float = Field(..., description="Price per unit", ge=0)
    currency: str = Field(default="INR", description="Currency code")


class SKUPricingResponse(SKUPricingBase):
    """SKU pricing response schema."""
    
    pricing_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SKUBase(BaseModel):
    """Base SKU schema."""
    
    product_name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    description: Optional[str] = Field(None, description="Product description")


class SKUCreate(SKUBase):
    """Create SKU schema."""
    
    sku_id: str = Field(..., description="Unique SKU identifier")
    raw_record: Dict[str, Any] = Field(default_factory=dict)
    features: List[SKUFeatureBase] = Field(default_factory=list)
    pricing: List[SKUPricingBase] = Field(default_factory=list)


class SKUUpdate(BaseModel):
    """Update SKU schema."""
    
    product_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class SKUResponse(SKUBase):
    """SKU response schema."""
    
    sku_id: str
    raw_record: Dict[str, Any]
    features: List[SKUFeatureResponse] = Field(default_factory=list)
    pricing: List[SKUPricingResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SKUListResponse(BaseModel):
    """SKU list response schema."""
    
    skus: List[SKUResponse]
    total: int


# ==================== Technical Recommendation Schemas ====================

class TopSKUMatch(BaseModel):
    """Top SKU match result."""
    
    sku_id: str
    product_name: str
    match_percentage: float
    explanation: Optional[str] = None


class TechnicalRecommendationBase(BaseModel):
    """Base technical recommendation schema."""
    
    top_skus: List[Dict[str, Any]] = Field(..., description="Top SKU matches")
    selected_sku_id: Optional[str] = Field(None, description="Selected SKU ID")
    spec_match_percent: float = Field(default=0.0)
    explanation: Optional[str] = None


class TechnicalRecommendationCreate(TechnicalRecommendationBase):
    """Create technical recommendation schema."""
    
    item_id: str = Field(..., description="RFP item ID")


class TechnicalRecommendationResponse(TechnicalRecommendationBase):
    """Technical recommendation response schema."""
    
    recommendation_id: int
    item_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Pricing Breakdown Schemas ====================

class PricingBreakdownBase(BaseModel):
    """Base pricing breakdown schema."""
    
    material_cost: float = Field(..., description="Material cost", ge=0)
    testing_cost: float = Field(..., description="Testing cost", ge=0)
    total_cost: float = Field(..., description="Total cost", ge=0)
    cost_per_unit: float = Field(..., description="Cost per unit", ge=0)
    currency: str = Field(default="INR")


class PricingBreakdownCreate(PricingBreakdownBase):
    """Create pricing breakdown schema."""
    
    item_id: str = Field(..., description="RFP item ID")


class PricingBreakdownResponse(PricingBreakdownBase):
    """Pricing breakdown response schema."""
    
    breakdown_id: int
    item_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== RFP Response Schemas ====================

class RFPResponseBase(BaseModel):
    """Base RFP response schema."""
    
    status: str = Field(default="draft", description="Response status")
    sales_summary: Optional[str] = None
    technical_response: Optional[Dict[str, Any]] = None
    pricing_response: Optional[Dict[str, Any]] = None
    final_narrative: Optional[str] = None


class RFPResponseCreate(RFPResponseBase):
    """Create RFP response schema."""
    
    rfp_id: str = Field(..., description="RFP ID")


class RFPResponseUpdate(BaseModel):
    """Update RFP response schema."""
    
    status: Optional[str] = None
    sales_summary: Optional[str] = None
    technical_response: Optional[Dict[str, Any]] = None
    pricing_response: Optional[Dict[str, Any]] = None
    final_narrative: Optional[str] = None


class RFPResponseDetail(RFPResponseBase):
    """Detailed RFP response schema."""
    
    response_id: int
    rfp_id: str
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== Workflow Schemas ====================

class WorkflowExecutionRequest(BaseModel):
    """Workflow execution request schema."""
    
    rfp_id: str = Field(..., description="RFP ID to process")
    workflow_type: str = Field(default="full", description="Workflow type: full, sales_only, technical_only, pricing_only")


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response schema."""
    
    execution_id: str
    rfp_id: str
    workflow_type: str
    status: str
    started_at: datetime
    message: str


# ==================== Search & Filter Schemas ====================

class SearchFilters(BaseModel):
    """Search and filter schema."""
    
    query: Optional[str] = None
    category: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)


class SearchResponse(BaseModel):
    """Generic search response schema."""
    
    total: int
    items: List[Dict[str, Any]]
    skip: int
    limit: int


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str
    detail: Optional[str] = None
    status_code: int


class ValidationError(BaseModel):
    """Validation error response."""
    
    field: str
    message: str


# ==================== Health Check Schemas ====================

class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    
    status: str = "healthy"
    version: str
    database: str = "connected"
    timestamp: datetime
