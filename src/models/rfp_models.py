"""RFP domain models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RFPItem(BaseModel):
    """Represents a single item in the RFP scope of supply."""
    
    item_id: str = Field(..., description="Unique identifier for this RFP item")
    description: str = Field(..., description="Item description")
    quantity: float = Field(..., description="Required quantity", gt=0)
    unit: str = Field(..., description="Unit of measurement (e.g., 'meters', 'pieces')")
    specs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Technical specifications as key-value pairs"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "ITEM-001",
                "description": "3.5 Core 240 sq.mm XLPE Insulated Armoured Cable",
                "quantity": 1000.0,
                "unit": "meters",
                "specs": {
                    "conductor_material": "Aluminium",
                    "conductor_size": "240 sq.mm",
                    "insulation_type": "XLPE",
                    "voltage_grade": "1.1 kV"
                }
            }
        }


class RFPTestRequirement(BaseModel):
    """Represents a testing requirement in the RFP."""
    
    test_name: str = Field(..., description="Name of the test")
    description: str = Field(..., description="Test description")
    required_standard: str = Field(..., description="Required standard (e.g., 'IS: 7098 Part 1')")
    frequency: Optional[str] = Field(None, description="Testing frequency (e.g., 'per lot')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_name": "Routine Tests",
                "description": "Standard electrical and mechanical tests",
                "required_standard": "IS: 7098 Part 1",
                "frequency": "per lot"
            }
        }


class RFP(BaseModel):
    """Complete RFP document model."""
    
    rfp_id: str = Field(..., description="Unique RFP identifier")
    title: str = Field(..., description="RFP title")
    source_url: str = Field(..., description="Source URL where RFP was found")
    submission_deadline: datetime = Field(..., description="Submission deadline")
    buyer: Optional[str] = Field(None, description="Buyer organization name")
    summary: Optional[str] = Field(None, description="High-level RFP summary")
    scope_of_supply: List[RFPItem] = Field(
        default_factory=list,
        description="List of items in scope of supply"
    )
    test_requirements: List[RFPTestRequirement] = Field(
        default_factory=list,
        description="List of testing requirements"
    )
    raw_text: Optional[str] = Field(None, description="Raw RFP text for reference")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rfp_id": "RFP-2025-001",
                "title": "Supply of Power Cables for Substation Project",
                "source_url": "https://example.com/rfp/2025-001",
                "submission_deadline": "2025-03-15T17:00:00",
                "buyer": "State Electricity Board",
                "summary": "Procurement of various power cables for new substation",
                "scope_of_supply": [],
                "test_requirements": []
            }
        }
