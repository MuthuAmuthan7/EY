"""LangGraph workflow for RFP processing."""

import logging
from typing import Dict, Any, List

from ..models.rfp_models import RFP
from ..api.schema import (
    GraphContext,
    SalesRFPOverview,
    TechnicalAgentOutput,
    PricingAgentOutput,
    FinalRFPResponse
)
from .sales_agent import SalesAgent
from .technical_agent import TechnicalAgent
from .pricing_agent import PricingAgent
from .master_agent import MasterAgent
from ..services.rfp_parser_service import RFPParserService

logger = logging.getLogger(__name__)


class RFPWorkflow:
    """Workflow orchestrator for RFP processing."""
    
    def __init__(self):
        """Initialize workflow with agents."""
        self.sales_agent = SalesAgent()
        self.technical_agent = TechnicalAgent()
        self.pricing_agent = PricingAgent()
        self.master_agent = MasterAgent()
        self.rfp_parser = RFPParserService()
    
    def run_sales_scan(self) -> List[SalesRFPOverview]:
        """Run sales agent to scan for RFPs.
        
        Returns:
            List of RFP overviews
        """
        logger.info("Running sales scan workflow")
        
        result = self.sales_agent.run({})
        rfps = [SalesRFPOverview(**rfp) for rfp in result.get("rfps", [])]
        
        return rfps
    
    def run_full_workflow_for_rfp(self, rfp_id: str) -> FinalRFPResponse:
        """Run complete workflow for a specific RFP.
        
        Args:
            rfp_id: RFP identifier
            
        Returns:
            Final RFP response
        """
        logger.info(f"Running full workflow for RFP: {rfp_id}")
        
        # Step 1: Load RFP
        rfp = self.rfp_parser.load_parsed_rfp(rfp_id)
        if not rfp:
            raise ValueError(f"RFP {rfp_id} not found")
        
        logger.info(f"Loaded RFP: {rfp.title}")
        
        # Step 2: Master agent prepares context
        context = self.master_agent.prepare_context(rfp)
        
        # Step 3: Technical agent processes
        logger.info("Running Technical Agent...")
        technical_result = self.technical_agent.run(context)
        technical_output = TechnicalAgentOutput(**technical_result)
        
        # Step 4: Pricing agent processes
        logger.info("Running Pricing Agent...")
        pricing_payload = {
            "rfp": context["rfp"],
            "technical_output": technical_result
        }
        pricing_result = self.pricing_agent.run(pricing_payload)
        pricing_output = PricingAgentOutput(**pricing_result)
        
        # Step 5: Master agent combines outputs
        logger.info("Combining outputs...")
        final_response = self.master_agent.combine_outputs(
            rfp,
            technical_output,
            pricing_output
        )
        
        logger.info("Workflow completed successfully")
        
        return final_response


# Global workflow instance
_workflow: RFPWorkflow | None = None


def get_workflow() -> RFPWorkflow:
    """Get global workflow instance."""
    global _workflow
    if _workflow is None:
        _workflow = RFPWorkflow()
    return _workflow


def run_sales_scan() -> List[SalesRFPOverview]:
    """Convenience function to run sales scan.
    
    Returns:
        List of RFP overviews
    """
    workflow = get_workflow()
    return workflow.run_sales_scan()


def run_full_workflow_for_rfp(rfp_id: str) -> FinalRFPResponse:
    """Convenience function to run full workflow.
    
    Args:
        rfp_id: RFP identifier
        
    Returns:
        Final RFP response
    """
    workflow = get_workflow()
    return workflow.run_full_workflow_for_rfp(rfp_id)
