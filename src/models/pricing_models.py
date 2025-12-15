"""Pricing domain models."""

from typing import List
from pydantic import BaseModel, Field


class PricingLine(BaseModel):
    """Represents pricing for a single SKU."""
    
    sku_id: str = Field(..., description="SKU identifier")
    unit_price: float = Field(..., description="Price per unit", gt=0)
    currency: str = Field(default="INR", description="Currency code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sku_id": "SKU-CABLE-001",
                "unit_price": 1250.50,
                "currency": "INR"
            }
        }


class TestPricingLine(BaseModel):
    """Represents pricing for a specific test."""
    
    test_name: str = Field(..., description="Test name")
    price: float = Field(..., description="Test price", gt=0)
    currency: str = Field(default="INR", description="Currency code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_name": "Routine Tests",
                "price": 5000.00,
                "currency": "INR"
            }
        }


class PricingTables(BaseModel):
    """Container for all pricing information."""
    
    product_pricing: List[PricingLine] = Field(
        default_factory=list,
        description="Product pricing table"
    )
    test_pricing: List[TestPricingLine] = Field(
        default_factory=list,
        description="Test pricing table"
    )
    
    def get_product_price(self, sku_id: str) -> float | None:
        """Get unit price for a specific SKU."""
        for line in self.product_pricing:
            if line.sku_id == sku_id:
                return line.unit_price
        return None
    
    def get_test_price(self, test_name: str) -> float | None:
        """Get price for a specific test."""
        for line in self.test_pricing:
            if line.test_name.lower() == test_name.lower():
                return line.price
        return None
