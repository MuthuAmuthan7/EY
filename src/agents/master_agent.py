"""Master Agent for orchestrating the RFP workflow."""

import logging
from typing import Dict, Any

from .base_agent import BaseAgent
from ..llm.client import LLMClient
from ..llm.prompts import MASTER_AGENT_SYSTEM_PROMPT
from ..models.rfp_models import RFP
from ..api.schema import (
    TechnicalAgentOutput,
    PricingAgentOutput,
    FinalRFPResponse
)

logger = logging.getLogger(__name__)


class MasterAgent(BaseAgent):
    """Master agent for orchestrating the RFP response workflow."""
    
    def __init__(self, llm_client: LLMClient | None = None):
        """Initialize Master Agent.
        
        Args:
            llm_client: LLM client
        """
        super().__init__("Master")
        self.llm_client = llm_client or LLMClient()
    
    def prepare_context(self, rfp: RFP) -> Dict[str, Any]:
        """Prepare context for sub-agents.
        
        Args:
            rfp: RFP object
            
        Returns:
            Context dictionary
        """
        self.log_start(f"Preparing context for RFP {rfp.rfp_id}")
        
        return {
            "rfp": rfp.model_dump(),
            "rfp_id": rfp.rfp_id
        }
    
    def combine_outputs(
        self,
        rfp: RFP,
        technical_output: TechnicalAgentOutput,
        pricing_output: PricingAgentOutput
    ) -> FinalRFPResponse:
        """Combine sub-agent outputs into final response.
        
        Args:
            rfp: RFP object
            technical_output: Technical agent output
            pricing_output: Pricing agent output
            
        Returns:
            Final RFP response
        """
        self.log_start("Combining outputs into final response")
        
        # Build final product table
        final_product_table = []
        for rec in technical_output.recommendations:
            # Find corresponding pricing
            pricing_line = None
            for line in pricing_output.lines:
                if line.rfp_item_id == rec.rfp_item_id:
                    pricing_line = line
                    break
            
            # Get best SKU details
            best_sku = rec.top_skus[0] if rec.top_skus else None
            
            product_entry = {
                "rfp_item_id": rec.rfp_item_id,
                "selected_sku_id": rec.selected_best_sku_id,
                "product_name": best_sku["product_name"] if best_sku else "N/A",
                "spec_match_percent": best_sku["spec_match_percent"] if best_sku else 0,
                "quantity": pricing_line.quantity if pricing_line else 0,
                "unit_price": pricing_line.unit_price if pricing_line else 0,
                "total_cost": pricing_line.total_cost if pricing_line else 0
            }
            final_product_table.append(product_entry)
        
        # Build pricing table
        pricing_table = [
            {
                "rfp_item_id": line.rfp_item_id,
                "sku_id": line.sku_id,
                "quantity": line.quantity,
                "unit_price": line.unit_price,
                "material_cost": line.material_cost,
                "test_cost": line.allocated_test_cost,
                "total_cost": line.total_cost
            }
            for line in pricing_output.lines
        ]
        
        # Add summary row
        pricing_table.append({
            "rfp_item_id": "TOTAL",
            "sku_id": "",
            "quantity": 0,
            "unit_price": 0,
            "material_cost": pricing_output.total_material_cost,
            "test_cost": pricing_output.total_test_cost,
            "total_cost": pricing_output.grand_total
        })
        
        # Generate narrative summary
        narrative = self._generate_narrative(
            rfp,
            technical_output,
            pricing_output
        )
        
        response = FinalRFPResponse(
            rfp_id=rfp.rfp_id,
            rfp_summary=rfp.summary or rfp.title,
            final_product_table=final_product_table,
            pricing_table=pricing_table,
            narrative_summary=narrative
        )
        
        self.log_complete("Final response generated")
        
        return response
    
    def _generate_narrative(
        self,
        rfp: RFP,
        technical_output: TechnicalAgentOutput,
        pricing_output: PricingAgentOutput
    ) -> str:
        """Generate narrative summary using LLM.
        
        Args:
            rfp: RFP object
            technical_output: Technical output
            pricing_output: Pricing output
            
        Returns:
            Narrative summary
        """
        try:
            # Build context for LLM
            context = f"""RFP: {rfp.title}
Buyer: {rfp.buyer or 'Unknown'}

Technical Recommendations:
"""
            for rec in technical_output.recommendations:
                best_sku = rec.top_skus[0] if rec.top_skus else None
                if best_sku:
                    context += f"- Item {rec.rfp_item_id}: {best_sku['product_name']} (Match: {best_sku['spec_match_percent']}%)\n"
            
            context += f"""
Pricing Summary:
- Material Cost: INR {pricing_output.total_material_cost:,.2f}
- Testing Cost: INR {pricing_output.total_test_cost:,.2f}
- Grand Total: INR {pricing_output.grand_total:,.2f}
"""
            
            prompt = f"""Based on this RFP analysis, write a professional 2-3 paragraph summary 
explaining our proposed solution and pricing. Focus on:
1. How well our products match the requirements
2. Key technical highlights
3. Competitive pricing

{context}"""
            
            narrative = self.llm_client.chat_completion(
                system_prompt=MASTER_AGENT_SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.7
            )
            
            return narrative
            
        except Exception as e:
            logger.warning(f"Error generating narrative: {e}")
            return f"Proposed solution for {rfp.title} with total cost of INR {pricing_output.grand_total:,.2f}"
    
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run master agent (for compatibility).
        
        Args:
            payload: Input data
            
        Returns:
            Output data
        """
        # Master agent typically doesn't run standalone
        # It's used via prepare_context and combine_outputs
        return {"status": "Master agent ready"}
