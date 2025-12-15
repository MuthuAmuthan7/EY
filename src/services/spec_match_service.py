"""Spec matching service for computing similarity between RFP specs and SKU features."""

import logging
import re
from typing import Dict, Any, Tuple , Optional

from ..models.rfp_models import RFPItem
from ..models.sku_models import SKU

logger = logging.getLogger(__name__)


class SpecMatchService:
    """Service for computing specification match percentages."""
    
    def __init__(self, numeric_tolerance: float = 0.1):
        """Initialize spec match service.
        
        Args:
            numeric_tolerance: Tolerance for numeric comparisons (default 10%)
        """
        self.numeric_tolerance = numeric_tolerance
        
        # Spec name synonyms for normalization
        self.synonyms = {
            "conductor material": ["conductor_material", "conductor", "material"],
            "conductor size": ["conductor_size", "size", "cross_section", "cross section"],
            "insulation": ["insulation_type", "insulation", "insulating material"],
            "voltage": ["voltage_grade", "voltage", "rated voltage", "voltage rating"],
            "cores": ["number of cores", "cores", "core count", "no of cores"],
        }
    
    def compute_spec_match(self, rfp_item: RFPItem, sku: SKU) -> Tuple[float, Dict[str, Any]]:
        """Compute specification match percentage between RFP item and SKU.
        
        Args:
            rfp_item: RFP item with specifications
            sku: SKU with features
            
        Returns:
            Tuple of (match_percentage, detailed_comparison)
        """
        if not rfp_item.specs:
            return 0.0, {}
        
        total_specs = len(rfp_item.specs)
        matched_score = 0.0
        comparison = {}
        
        for spec_name, rfp_value in rfp_item.specs.items():
            # Find matching SKU feature
            sku_value = self._find_matching_feature(spec_name, sku)
            
            # Compute match score for this spec
            spec_score = self._compare_values(rfp_value, sku_value)
            matched_score += spec_score
            
            comparison[spec_name] = {
                "rfp_value": str(rfp_value),
                "sku_value": str(sku_value) if sku_value is not None else "N/A",
                "match_score": spec_score,
                "match_type": self._get_match_type(spec_score)
            }
        
        # Calculate percentage
        match_percentage = (matched_score / total_specs) * 100 if total_specs > 0 else 0.0
        
        return match_percentage, comparison
    
    def _find_matching_feature(self, spec_name: str, sku: SKU) -> Any:
        """Find matching feature in SKU.
        
        Args:
            spec_name: RFP spec name
            sku: SKU object
            
        Returns:
            Feature value or None
        """
        normalized_spec = self._normalize_name(spec_name)
        
        # Try exact match first
        for feature in sku.features:
            if self._normalize_name(feature.name) == normalized_spec:
                return feature.value
        
        # Try synonym match
        for canonical, synonyms in self.synonyms.items():
            if normalized_spec in synonyms or normalized_spec == canonical:
                for feature in sku.features:
                    if self._normalize_name(feature.name) in synonyms:
                        return feature.value
        
        return None
    
    def _normalize_name(self, name: str) -> str:
        """Normalize spec/feature name.
        
        Args:
            name: Name to normalize
            
        Returns:
            Normalized name
        """
        return re.sub(r'[^a-z0-9]+', '_', name.lower().strip()).strip('_')
    
    def _compare_values(self, rfp_value: Any, sku_value: Any) -> float:
        """Compare RFP value with SKU value.
        
        Args:
            rfp_value: RFP specification value
            sku_value: SKU feature value
            
        Returns:
            Match score (0.0 to 1.0)
        """
        if sku_value is None:
            return 0.0
        
        # Convert to strings for comparison
        rfp_str = str(rfp_value).lower().strip()
        sku_str = str(sku_value).lower().strip()
        
        # Exact match
        if rfp_str == sku_str:
            return 1.0
        
        # Try numeric comparison
        rfp_num = self._extract_number(rfp_str)
        sku_num = self._extract_number(sku_str)
        
        if rfp_num is not None and sku_num is not None:
            # Check if within tolerance
            tolerance = abs(rfp_num * self.numeric_tolerance)
            if abs(rfp_num - sku_num) <= tolerance:
                return 0.8  # Good match within tolerance
            elif abs(rfp_num - sku_num) <= tolerance * 2:
                return 0.5  # Partial match
            else:
                return 0.0  # No match
        
        # Substring match
        if rfp_str in sku_str or sku_str in rfp_str:
            return 0.6
        
        # Check for common words
        rfp_words = set(rfp_str.split())
        sku_words = set(sku_str.split())
        common_words = rfp_words & sku_words
        
        if common_words:
            overlap = len(common_words) / max(len(rfp_words), len(sku_words))
            return overlap * 0.5
        
        return 0.0
    
    def _extract_number(self, text: str) -> float | None:
        """Extract numeric value from text.
        
        Args:
            text: Text containing number
            
        Returns:
            Numeric value or None
        """
        # Match numbers (including decimals)
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    def _get_match_type(self, score: float) -> str:
        """Get match type description from score.
        
        Args:
            score: Match score
            
        Returns:
            Match type string
        """
        if score >= 0.95:
            return "Exact Match"
        elif score >= 0.75:
            return "Good Match"
        elif score >= 0.5:
            return "Partial Match"
        elif score > 0:
            return "Weak Match"
        else:
            return "No Match"


# Global service instance
_spec_match_service: Optional[SpecMatchService] = None


def get_spec_match_service() -> SpecMatchService:
    """Get global spec match service instance."""
    global _spec_match_service
    if _spec_match_service is None:
        _spec_match_service = SpecMatchService()
    return _spec_match_service
