"""Pricing Agent for cost calculation."""

import logging
from typing import Dict, Any

from .base_agent import BaseAgent
from ..llm.client import LLMClient
from ..llm.prompts import PRICING_AGENT_SYSTEM_PROMPT
from ..models.rfp_models import RFP
from ..models.pricing_models import PricingTables
from ..services.pricing_service import get_pricing_service
from ..api.schema import TechnicalAgentOutput, PricingAgentOutput
from ..data_ingestion.pricing_loader import load_pricing_tables

logger = logging.getLogger(__name__)


class PricingAgent(BaseAgent):
    """Agent responsible for pricing calculation."""
    
    def __init__(
        self,
        llm_client: LLMClient | None = None,
        pricing_tables: PricingTables | None = None
    ):
        """Initialize Pricing Agent.
        
        Args:
            llm_client: LLM client
            pricing_tables: Pricing tables (loaded if not provided)
        """
        super().__init__("Pricing")
        self.llm_client = llm_client or LLMClient()
        self.pricing_tables = pricing_tables or load_pricing_tables()
        self.pricing_service = get_pricing_service(self.pricing_tables)
    
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pricing for RFP.
        
        Args:
            payload: Must contain 'rfp' and 'technical_output'
            
        Returns:
            Pricing agent output
        """
        self.log_start("Calculating RFP pricing")
        
        try:
            # Parse inputs
            rfp = RFP(**payload['rfp'])
            technical_output = TechnicalAgentOutput(**payload['technical_output'])
            
            # Calculate pricing
            pricing_output = self.pricing_service.price_rfp(rfp, technical_output)
            
            self.log_complete(
                f"Total: INR {pricing_output.grand_total:,.2f} "
                f"({len(pricing_output.lines)} items)"
            )
            
            return pricing_output.model_dump()
            
        except Exception as e:
            self.log_error(e)
            raise
