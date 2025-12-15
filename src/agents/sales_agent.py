"""Sales Agent for RFP discovery and filtering."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .base_agent import BaseAgent
from ..llm.client import LLMClient
from ..llm.prompts import SALES_AGENT_SYSTEM_PROMPT
from ..services.scraping_service import get_scraping_service
from ..services.rfp_parser_service import RFPParserService
from ..api.schema import SalesRFPOverview
from ..config import settings

logger = logging.getLogger(__name__)


class SalesAgent(BaseAgent):
    """Agent responsible for RFP discovery and qualification."""
    
    def __init__(self, llm_client: LLMClient | None = None):
        """Initialize Sales Agent.
        
        Args:
            llm_client: LLM client for summarization
        """
        super().__init__("Sales")
        self.llm_client = llm_client or LLMClient()
        self.scraping_service = get_scraping_service()
        self.parser_service = RFPParserService(self.llm_client)
    
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scan URLs for RFPs and filter by deadline.
        
        Args:
            payload: Input data (can be empty for scan)
            
        Returns:
            Dictionary with 'rfps' list
        """
        self.log_start("Scanning RFPs from configured URLs")
        
        try:
            rfps = self.scan_rfps()
            
            self.log_complete(f"Found {len(rfps)} relevant RFPs")
            
            return {
                "rfps": [rfp.model_dump() for rfp in rfps],
                "count": len(rfps)
            }
            
        except Exception as e:
            self.log_error(e)
            return {"rfps": [], "count": 0, "error": str(e)}
    
    def scan_rfps(self) -> List[SalesRFPOverview]:
        """Scan configured URLs for RFPs.
        
        Returns:
            List of RFP overviews
        """
        all_rfps = []
        
        # For demo purposes, we'll use the parsed RFP files
        # In production, this would scrape URLs
        parsed_dir = settings.get_rfp_parsed_dir()
        
        if not parsed_dir.exists():
            logger.warning(f"Parsed RFP directory not found: {parsed_dir}")
            return []
        
        # Load all parsed RFPs
        for rfp_file in parsed_dir.glob("*.json"):
            try:
                rfp = self.parser_service.load_parsed_rfp(rfp_file.stem)
                if rfp:
                    # Filter by deadline (next 3 months)
                    if self._is_within_deadline(rfp.submission_deadline):
                        overview = self._create_overview(rfp)
                        all_rfps.append(overview)
            except Exception as e:
                logger.warning(f"Error loading RFP from {rfp_file}: {e}")
        
        return all_rfps
    
    def _is_within_deadline(self, deadline: datetime) -> bool:
        """Check if deadline is within next 3 months or recently passed (within 7 days).
        
        Args:
            deadline: Submission deadline
            
        Returns:
            True if within 3 months or recently passed
        """
        now = datetime.now()
        three_months_later = now + timedelta(days=90)
        one_week_ago = now - timedelta(days=7)
        
        # Include RFPs within next 3 months or passed in the last 7 days
        return one_week_ago <= deadline <= three_months_later
    
    def _create_overview(self, rfp) -> SalesRFPOverview:
        """Create RFP overview with summary.
        
        Args:
            rfp: RFP object
            
        Returns:
            Sales RFP overview
        """
        # Generate brief summary if not present
        if not rfp.summary:
            summary = self._generate_summary(rfp)
        else:
            summary = rfp.summary
        
        return SalesRFPOverview(
            rfp_id=rfp.rfp_id,
            title=rfp.title,
            source_url=rfp.source_url,
            submission_deadline=rfp.submission_deadline,
            brief_summary=summary
        )
    
    def _generate_summary(self, rfp) -> str:
        """Generate brief summary using LLM.
        
        Args:
            rfp: RFP object
            
        Returns:
            Summary text
        """
        try:
            # Build context
            context = f"""Title: {rfp.title}
Buyer: {rfp.buyer or 'Unknown'}
Items: {len(rfp.scope_of_supply)}
Tests: {len(rfp.test_requirements)}"""
            
            summary = self.llm_client.summarize(
                text=context,
                max_length=50,
                focus="business opportunity and key requirements"
            )
            
            return summary
            
        except Exception as e:
            logger.warning(f"Error generating summary: {e}")
            return f"RFP for {len(rfp.scope_of_supply)} items from {rfp.buyer or 'buyer'}"
