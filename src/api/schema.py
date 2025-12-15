"""API schemas for agent communication and data transfer."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..models.rfp_models import RFP
from ..models.sku_models import SKU


# Sales Agent Schemas

class SalesRFPOverview(BaseModel):
    """Brief RFP overview returned by Sales Agent."""
    
    rfp_id: str
    title: str
    source_url: str
    submission_deadline: datetime
    brief_summary: str


# Technical Agent Schemas

class SpecMatchRow(BaseModel):
    """Single row in spec comparison table."""
    
    rfp_item_id: str
    rfp_description: str
    spec_name: str
    rfp_value: str
    sku1_value: Optional[str] = None
    sku2_value: Optional[str] = None
    sku3_value: Optional[str] = None


class TechnicalRecommendation(BaseModel):
    """Technical recommendation for a single RFP item."""
    
    rfp_item_id: str
    top_skus: List[Dict[str, Any]] = Field(
        description="Top SKU matches with sku_id, spec_match_percent, explanation"
    )
    spec_comparison_table: List[SpecMatchRow]
    selected_best_sku_id: str


class TechnicalAgentOutput(BaseModel):
    """Complete output from Technical Agent."""
    
    rfp_id: str
    recommendations: List[TechnicalRecommendation]


# Pricing Agent Schemas

class PricingResultLine(BaseModel):
    """Pricing result for a single RFP item."""
    
    rfp_item_id: str
    sku_id: str
    quantity: float
    unit_price: float
    material_cost: float
    allocated_test_cost: float
    total_cost: float


class PricingAgentOutput(BaseModel):
    """Complete output from Pricing Agent."""
    
    rfp_id: str
    lines: List[PricingResultLine]
    total_material_cost: float
    total_test_cost: float
    grand_total: float


# Master Agent Schemas

class FinalRFPResponse(BaseModel):
    """Final consolidated RFP response from Master Agent."""
    
    rfp_id: str
    rfp_summary: str
    final_product_table: List[Dict[str, Any]] = Field(
        description="Consolidated product recommendations with spec match"
    )
    pricing_table: List[Dict[str, Any]] = Field(
        description="Material and test costs breakdown"
    )
    narrative_summary: str = Field(
        description="LLM-generated explanation of the response"
    )


# Graph Context

class GraphContext(BaseModel):
    """Context passed between LangGraph nodes."""
    
    # Input
    rfp: Optional[RFP] = None
    sales_overview: Optional[SalesRFPOverview] = None
    
    # Intermediate outputs
    technical_output: Optional[TechnicalAgentOutput] = None
    pricing_output: Optional[PricingAgentOutput] = None
    
    # Final output
    final_response: Optional[FinalRFPResponse] = None
    
    # Metadata
    current_step: str = "init"
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
