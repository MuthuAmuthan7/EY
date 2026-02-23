"""RFP extraction and conversion service."""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..llm.client import LLMClient
from ..config import settings
from .pdf_parser_service import PDFParserService

logger = logging.getLogger(__name__)


class RFPExtractionService:
    """Service for extracting RFP data from PDF and converting to SKU format."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None, pdf_parser: Optional[PDFParserService] = None):
        """Initialize RFP extraction service.
        
        Args:
            llm_client: LLM client for AI-powered parsing
            pdf_parser: PDF parser service
        """
        self.llm_client = llm_client or LLMClient()
        self.pdf_parser = pdf_parser or PDFParserService(llm_client)
    
    def extract_rfp_from_pdf_bytes(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Extract RFP data from PDF bytes.
        
        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename for logging
            
        Returns:
            Dictionary containing extracted RFP data
        """
        logger.info(f"Extracting RFP from PDF: {filename}")
        
        # Step 1: Extract text from PDF
        try:
            pdf_text = self.pdf_parser.extract_text_from_bytes(pdf_bytes)
            logger.info(f"Successfully extracted text from PDF ({len(pdf_text)} chars)")
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
        
        # Step 2: Use LLM to extract structured RFP data
        try:
            rfp_data = self._parse_rfp_with_llm(pdf_text, filename)
            logger.info(f"Successfully parsed RFP data from PDF")
            return rfp_data
        except Exception as e:
            logger.error(f"Failed to parse RFP data with LLM: {e}")
            raise
    
    def extract_rfp_from_text(self, text: str, filename: str = "unknown") -> Dict[str, Any]:
        """Extract RFP data from raw text.
        
        Args:
            text: Raw text content
            filename: Original filename for logging
            
        Returns:
            Dictionary containing extracted RFP data
        """
        logger.info(f"Extracting RFP from text: {filename}")
        
        try:
            rfp_data = self._parse_rfp_with_llm(text, filename)
            logger.info(f"Successfully parsed RFP data from text")
            return rfp_data
        except Exception as e:
            logger.error(f"Failed to parse RFP data with LLM: {e}")
            raise
    
    def _parse_rfp_with_llm(self, text: str, filename: str) -> Dict[str, Any]:
        """Parse RFP text using LLM.
        
        Args:
            text: Text to parse
            filename: Original filename
            
        Returns:
            Parsed RFP data
        """
        system_prompt = """You are an expert RFP (Request for Proposal) parser. 
Extract structured information from the provided RFP document text.
Focus on identifying: product name, category, description, specifications (features), and any pricing information.

Return ONLY a valid JSON object with NO additional text or markdown formatting."""
        
        user_prompt = f"""Parse the following RFP document and extract the key information. 
Return a JSON object matching this structure:

{{
  "product_name": "string - main product name",
  "category": "string - product category",
  "description": "string - detailed product description",
  "key_specs": {{"spec_name": "spec_value"}},
  "features": [
    {{"name": "feature name", "value": "feature value", "unit": "measurement unit (optional)"}}
  ],
  "pricing_info": "any pricing details mentioned",
  "quantity_required": "quantity if specified",
  "delivery_timeline": "delivery timeline if specified",
  "additional_requirements": "any other important requirements"
}}

RFP Document:
---
{text[:5000]}
---

Return only the JSON object, no additional text."""
        
        try:
            response = self.llm_client.chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,  # Lower temperature for more consistent parsing
                max_tokens=2000
            )
            
            # Parse JSON response
            try:
                # Clean response - remove markdown code blocks if present
                cleaned = response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                rfp_data = json.loads(cleaned)
                return rfp_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.debug(f"LLM Response: {response[:500]}")
                raise
        except Exception as e:
            logger.error(f"LLM parsing error: {e}")
            raise
    
    def convert_rfp_to_sku(self, rfp_data: Dict[str, Any], sku_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert extracted RFP data to SKU format.
        
        Args:
            rfp_data: Extracted RFP data from LLM
            sku_id: Optional SKU ID (will be generated if not provided)
            
        Returns:
            SKU formatted data
        """
        logger.info("Converting RFP data to SKU format")
        
        # Generate SKU ID if not provided
        if not sku_id:
            sku_id = self._generate_sku_id(rfp_data.get("product_name", "UNKNOWN"))
        
        # Extract features
        features = []
        if "features" in rfp_data and isinstance(rfp_data["features"], list):
            for idx, feature in enumerate(rfp_data["features"]):
                features.append({
                    "name": feature.get("name", ""),
                    "value": feature.get("value", ""),
                    "unit": feature.get("unit"),
                    "feature_id": idx
                })
        
        # Extract specs as features if not already present
        if "key_specs" in rfp_data and isinstance(rfp_data["key_specs"], dict) and not features:
            for idx, (spec_name, spec_value) in enumerate(rfp_data["key_specs"].items()):
                features.append({
                    "name": spec_name,
                    "value": str(spec_value),
                    "unit": None,
                    "feature_id": idx
                })
        
        # Create pricing entry
        pricing = []
        if rfp_data.get("pricing_info"):
            # Try to extract price if available
            pricing.append({
                "unit_price": 0.0,  # Will be updated if price is extracted
                "currency": "INR",
                "pricing_id": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            })
        else:
            # Add placeholder pricing
            pricing.append({
                "unit_price": 0.0,
                "currency": "INR",
                "pricing_id": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            })
        
        sku_format = {
            "product_name": rfp_data.get("product_name", "Unknown Product"),
            "category": rfp_data.get("category", "Uncategorized"),
            "description": rfp_data.get("description", ""),
            "sku_id": sku_id,
            "raw_record": rfp_data,  # Store original RFP data
            "features": features,
            "pricing": pricing,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Successfully converted RFP to SKU format: {sku_id}")
        return sku_format
    
    def _generate_sku_id(self, product_name: str) -> str:
        """Generate a unique SKU ID.
        
        Args:
            product_name: Product name for slug generation
            
        Returns:
            Generated SKU ID
        """
        # Create slug from product name
        slug = product_name.upper().replace(" ", "_")[:20]
        # Add unique identifier
        unique_id = str(uuid.uuid4())[:8].upper()
        sku_id = f"SKU-{slug}-{unique_id}"
        return sku_id
    
    def process_rfp_pdf_complete(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Complete pipeline: PDF -> RFP extraction -> SKU conversion.
        
        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename
            
        Returns:
            Final SKU formatted data ready for database insertion
        """
        logger.info(f"Starting complete RFP processing pipeline: {filename}")
        
        # Step 1: Extract RFP data from PDF
        rfp_data = self.extract_rfp_from_pdf_bytes(pdf_bytes, filename)
        
        # Step 2: Convert to SKU format
        sku_data = self.convert_rfp_to_sku(rfp_data)
        
        logger.info(f"RFP processing pipeline complete: {sku_data['sku_id']}")
        return sku_data
