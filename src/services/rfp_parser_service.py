"""RFP parsing service for extracting structured data from RFP documents."""

import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from dateutil import parser as date_parser
from bs4 import BeautifulSoup

from ..models.rfp_models import RFP, RFPItem, RFPTestRequirement
from ..llm.client import LLMClient
from ..config import settings

logger = logging.getLogger(__name__)


class RFPParserService:
    """Service for parsing RFP documents."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize parser service.
        
        Args:
            llm_client: LLM client for AI-powered parsing
        """
        self.llm_client = llm_client or LLMClient()
    
    def parse_html_page(self, html_content: str, source_url: str) -> list[Dict[str, Any]]:
        """Parse HTML page to extract RFP listings.
        
        Args:
            html_content: HTML content
            source_url: Source URL
            
        Returns:
            List of RFP metadata dictionaries
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        rfps = []
        
        # This is a simplified parser - in production, you'd customize for specific sites
        # Look for common RFP indicators
        rfp_blocks = soup.find_all(['div', 'tr', 'article'], class_=re.compile(r'rfp|tender|procurement', re.I))
        
        for block in rfp_blocks:
            try:
                rfp_data = self._extract_rfp_from_block(block, source_url)
                if rfp_data:
                    rfps.append(rfp_data)
            except Exception as e:
                logger.warning(f"Error parsing RFP block: {e}")
        
        return rfps
    
    def _extract_rfp_from_block(self, block, source_url: str) -> Optional[Dict[str, Any]]:
        """Extract RFP data from HTML block.
        
        Args:
            block: BeautifulSoup element
            source_url: Source URL
            
        Returns:
            RFP metadata dictionary or None
        """
        text = block.get_text(separator=' ', strip=True)
        
        # Extract deadline using regex
        deadline = self._extract_deadline(text)
        if not deadline:
            return None
        
        # Extract title
        title_elem = block.find(['h1', 'h2', 'h3', 'h4', 'a'])
        title = title_elem.get_text(strip=True) if title_elem else text[:100]
        
        # Generate ID
        rfp_id = f"RFP-{hash(title + source_url) % 100000:05d}"
        
        return {
            "rfp_id": rfp_id,
            "title": title,
            "source_url": source_url,
            "submission_deadline": deadline,
            "raw_text": text[:500]  # First 500 chars
        }
    
    def _extract_deadline(self, text: str) -> Optional[datetime]:
        """Extract deadline date from text.
        
        Args:
            text: Text to search
            
        Returns:
            Deadline datetime or None
        """
        # Common date patterns
        date_patterns = [
            r'deadline[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'due[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'submit by[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    return date_parser.parse(date_str, fuzzy=True)
                except:
                    continue
        
        return None
    
    def parse_rfp_document(self, content: str, rfp_id: str, source_url: str) -> Optional[RFP]:
        """Parse complete RFP document using LLM.
        
        Args:
            content: RFP document content
            rfp_id: RFP identifier
            source_url: Source URL
            
        Returns:
            Parsed RFP object or None
        """
        system_prompt = """You are an expert at parsing RFP (Request for Proposal) documents.
Extract structured information from the RFP text and return it in JSON format.

Extract:
1. Title
2. Submission deadline (ISO format)
3. Buyer organization
4. Summary (2-3 sentences)
5. Scope of supply (list of items with specs)
6. Test requirements

Return JSON matching the RFP schema."""
        
        user_prompt = f"""Parse this RFP document:

{content[:4000]}  # Limit to avoid token limits

RFP ID: {rfp_id}
Source URL: {source_url}

Return structured JSON."""
        
        try:
            # Use LLM to parse
            response = self.llm_client.structured_output(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=RFP,
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error parsing RFP document with LLM: {e}")
            return None
    
    def load_parsed_rfp(self, rfp_id: str) -> Optional[RFP]:
        """Load previously parsed RFP from disk.
        
        Args:
            rfp_id: RFP identifier
            
        Returns:
            RFP object or None
        """
        parsed_dir = settings.get_rfp_parsed_dir()
        rfp_file = parsed_dir / f"{rfp_id}.json"
        
        if not rfp_file.exists():
            return None
        
        try:
            with open(rfp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return RFP(**data)
        except Exception as e:
            logger.error(f"Error loading RFP {rfp_id}: {e}")
            return None
    
    def save_parsed_rfp(self, rfp: RFP) -> bool:
        """Save parsed RFP to disk.
        
        Args:
            rfp: RFP object
            
        Returns:
            True if successful
        """
        parsed_dir = settings.get_rfp_parsed_dir()
        parsed_dir.mkdir(parents=True, exist_ok=True)
        
        rfp_file = parsed_dir / f"{rfp.rfp_id}.json"
        
        try:
            with open(rfp_file, 'w', encoding='utf-8') as f:
                json.dump(rfp.model_dump(mode='json'), f, indent=2, default=str)
            logger.info(f"Saved RFP {rfp.rfp_id} to {rfp_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving RFP {rfp.rfp_id}: {e}")
            return False
