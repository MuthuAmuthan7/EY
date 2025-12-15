"""Pricing service for calculating RFP costs."""

import logging
from typing import List, Dict, Any

from ..models.rfp_models import RFP, RFPItem, RFPTestRequirement
from ..models.pricing_models import PricingTables
from ..api.schema import TechnicalAgentOutput, PricingResultLine, PricingAgentOutput

logger = logging.getLogger(__name__)


class PricingService:
    """Service for computing RFP pricing."""
    
    def __init__(self, pricing_tables: PricingTables):
        """Initialize pricing service.
        
        Args:
            pricing_tables: Pricing tables with product and test pricing
        """
        self.pricing_tables = pricing_tables
    
    def price_rfp(
        self,
        rfp: RFP,
        technical_output: TechnicalAgentOutput
    ) -> PricingAgentOutput:
        """Calculate complete pricing for an RFP.
        
        Args:
            rfp: RFP object
            technical_output: Technical agent's recommendations
            
        Returns:
            Pricing agent output with detailed costs
        """
        lines: List[PricingResultLine] = []
        total_material_cost = 0.0
        total_test_cost = 0.0
        
        # Calculate material costs per item
        for recommendation in technical_output.recommendations:
            rfp_item = self._find_rfp_item(rfp, recommendation.rfp_item_id)
            if not rfp_item:
                logger.warning(f"RFP item {recommendation.rfp_item_id} not found")
                continue
            
            sku_id = recommendation.selected_best_sku_id
            unit_price = self.pricing_tables.get_product_price(sku_id)
            
            if unit_price is None:
                logger.warning(f"No price found for SKU {sku_id}")
                unit_price = 0.0
            
            material_cost = rfp_item.quantity * unit_price
            total_material_cost += material_cost
            
            # Create pricing line (test cost allocated later)
            line = PricingResultLine(
                rfp_item_id=rfp_item.item_id,
                sku_id=sku_id,
                quantity=rfp_item.quantity,
                unit_price=unit_price,
                material_cost=material_cost,
                allocated_test_cost=0.0,  # Will be allocated
                total_cost=material_cost
            )
            lines.append(line)
        
        # Calculate test costs
        for test_req in rfp.test_requirements:
            test_price = self.pricing_tables.get_test_price(test_req.test_name)
            if test_price is None:
                logger.warning(f"No price found for test: {test_req.test_name}")
                test_price = 0.0
            
            total_test_cost += test_price
        
        # Allocate test costs proportionally across items
        if lines and total_test_cost > 0:
            for line in lines:
                # Allocate based on material cost proportion
                proportion = line.material_cost / total_material_cost if total_material_cost > 0 else 1.0 / len(lines)
                line.allocated_test_cost = total_test_cost * proportion
                line.total_cost = line.material_cost + line.allocated_test_cost
        
        grand_total = total_material_cost + total_test_cost
        
        return PricingAgentOutput(
            rfp_id=rfp.rfp_id,
            lines=lines,
            total_material_cost=total_material_cost,
            total_test_cost=total_test_cost,
            grand_total=grand_total
        )
    
    def _find_rfp_item(self, rfp: RFP, item_id: str) -> RFPItem | None:
        """Find RFP item by ID.
        
        Args:
            rfp: RFP object
            item_id: Item ID
            
        Returns:
            RFP item or None
        """
        for item in rfp.scope_of_supply:
            if item.item_id == item_id:
                return item
        return None


def get_pricing_service(pricing_tables: PricingTables) -> PricingService:
    """Create pricing service instance.
    
    Args:
        pricing_tables: Pricing tables
        
    Returns:
        Pricing service
    """
    return PricingService(pricing_tables)
