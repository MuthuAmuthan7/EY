"""SKU and product specification models."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SKUFeature(BaseModel):
    """Represents a single feature/specification of a product SKU."""
    
    name: str = Field(..., description="Feature name (e.g., 'Conductor Material')")
    value: str = Field(..., description="Feature value (e.g., 'Aluminium')")
    unit: Optional[str] = Field(None, description="Unit of measurement if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Conductor Material",
                "value": "Aluminium",
                "unit": None
            }
        }


class SKU(BaseModel):
    """Represents a product SKU with its specifications."""
    
    sku_id: str = Field(..., description="Unique SKU identifier")
    product_name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category (e.g., 'Power Cable')")
    features: List[SKUFeature] = Field(
        default_factory=list,
        description="List of product features/specifications"
    )
    raw_record: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original data record for reference"
    )
    
    def get_feature_value(self, feature_name: str) -> Optional[str]:
        """Get the value of a specific feature by name."""
        for feature in self.features:
            if feature.name.lower() == feature_name.lower():
                return feature.value
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SKU to dictionary format."""
        return {
            "sku_id": self.sku_id,
            "product_name": self.product_name,
            "category": self.category,
            "features": {f.name: f.value for f in self.features}
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "sku_id": "SKU-CABLE-001",
                "product_name": "XLPE Insulated Armoured Cable 3.5C x 240 sq.mm",
                "category": "Power Cable",
                "features": [
                    {"name": "Conductor Material", "value": "Aluminium", "unit": None},
                    {"name": "Conductor Size", "value": "240", "unit": "sq.mm"},
                    {"name": "Insulation Type", "value": "XLPE", "unit": None},
                    {"name": "Voltage Grade", "value": "1.1", "unit": "kV"}
                ]
            }
        }


class SKURepository(BaseModel):
    """Repository containing multiple SKUs."""
    
    skus: List[SKU] = Field(default_factory=list, description="List of all SKUs")
    
    def get_by_id(self, sku_id: str) -> Optional[SKU]:
        """Get SKU by ID."""
        for sku in self.skus:
            if sku.sku_id == sku_id:
                return sku
        return None
    
    def get_by_category(self, category: str) -> List[SKU]:
        """Get all SKUs in a specific category."""
        return [sku for sku in self.skus if sku.category.lower() == category.lower()]
    
    def add_sku(self, sku: SKU) -> None:
        """Add a SKU to the repository."""
        self.skus.append(sku)
    
    def __len__(self) -> int:
        """Return number of SKUs in repository."""
        return len(self.skus)
