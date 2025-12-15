"""Technical Agent for spec matching and SKU recommendation."""

import logging
from typing import List, Dict, Any

from .base_agent import BaseAgent
from ..llm.client import LLMClient
from ..llm.prompts import TECHNICAL_AGENT_SYSTEM_PROMPT
from ..llm.retrieval import get_sku_candidates
from ..services.spec_match_service import get_spec_match_service
from ..models.rfp_models import RFP
from ..models.sku_models import SKU, SKUFeature
from ..api.schema import (
    TechnicalAgentOutput,
    TechnicalRecommendation,
    SpecMatchRow
)

logger = logging.getLogger(__name__)


class TechnicalAgent(BaseAgent):
    """Agent responsible for technical spec matching."""
    
    def __init__(self, llm_client: LLMClient | None = None):
        """Initialize Technical Agent.
        
        Args:
            llm_client: LLM client
        """
        super().__init__("Technical")
        self.llm_client = llm_client or LLMClient()
        self.spec_match_service = get_spec_match_service()
    
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Match RFP items to SKUs.
        
        Args:
            payload: Must contain 'rfp' (RFP object dict)
            
        Returns:
            Technical agent output
        """
        self.log_start("Matching RFP specs to SKUs")
        
        try:
            # Parse RFP from payload
            rfp = RFP(**payload['rfp'])
            
            # Process each RFP item
            recommendations = []
            for item in rfp.scope_of_supply:
                rec = self._process_rfp_item(item)
                recommendations.append(rec)
            
            output = TechnicalAgentOutput(
                rfp_id=rfp.rfp_id,
                recommendations=recommendations
            )
            
            self.log_complete(f"Processed {len(recommendations)} items")
            
            return output.model_dump()
            
        except Exception as e:
            self.log_error(e)
            raise
    
    def _process_rfp_item(self, rfp_item) -> TechnicalRecommendation:
        """Process single RFP item.
        
        Args:
            rfp_item: RFP item
            
        Returns:
            Technical recommendation
        """
        # Get candidate SKUs from vector search
        candidates = get_sku_candidates(rfp_item, top_k=10)
        
        # Compute spec match for each candidate
        scored_skus = []
        for candidate in candidates:
            # Convert candidate dict to SKU object
            sku = self._dict_to_sku(candidate)
            
            # Compute match
            match_percent, comparison = self.spec_match_service.compute_spec_match(
                rfp_item, sku
            )
            
            scored_skus.append({
                "sku_id": sku.sku_id,
                "product_name": sku.product_name,
                "spec_match_percent": round(match_percent, 2),
                "comparison": comparison,
                "sku": sku
            })
        
        # Sort by match percentage
        scored_skus.sort(key=lambda x: x["spec_match_percent"], reverse=True)
        
        # Take top 3
        top_3 = scored_skus[:3]
        
        # Build comparison table
        spec_comparison = self._build_comparison_table(rfp_item, top_3)
        
        # Select best SKU
        best_sku_id = top_3[0]["sku_id"] if top_3 else "NONE"
        
        # Format top SKUs for output
        top_skus_output = [
            {
                "sku_id": sku["sku_id"],
                "product_name": sku["product_name"],
                "spec_match_percent": sku["spec_match_percent"],
                "explanation": f"Match: {sku['spec_match_percent']}%"
            }
            for sku in top_3
        ]
        
        return TechnicalRecommendation(
            rfp_item_id=rfp_item.item_id,
            top_skus=top_skus_output,
            spec_comparison_table=spec_comparison,
            selected_best_sku_id=best_sku_id
        )
    
    def _dict_to_sku(self, candidate: Dict[str, Any]) -> SKU:
        """Convert candidate dict to SKU object.
        
        Args:
            candidate: Candidate dictionary
            
        Returns:
            SKU object
        """
        features = []
        for name, value in candidate.get("features", {}).items():
            features.append(SKUFeature(name=name, value=str(value)))
        
        return SKU(
            sku_id=candidate.get("sku_id", ""),
            product_name=candidate.get("product_name", ""),
            category=candidate.get("category", ""),
            features=features
        )
    
    def _build_comparison_table(
        self,
        rfp_item,
        top_skus: List[Dict[str, Any]]
    ) -> List[SpecMatchRow]:
        """Build spec comparison table.
        
        Args:
            rfp_item: RFP item
            top_skus: Top 3 SKUs with comparison data
            
        Returns:
            List of comparison rows
        """
        rows = []
        
        for spec_name, rfp_value in rfp_item.specs.items():
            sku_values = []
            
            for sku_data in top_skus:
                comparison = sku_data.get("comparison", {})
                spec_comp = comparison.get(spec_name, {})
                sku_val = spec_comp.get("sku_value", "N/A")
                sku_values.append(sku_val)
            
            # Pad with N/A if less than 3 SKUs
            while len(sku_values) < 3:
                sku_values.append("N/A")
            
            row = SpecMatchRow(
                rfp_item_id=rfp_item.item_id,
                rfp_description=rfp_item.description,
                spec_name=spec_name,
                rfp_value=str(rfp_value),
                sku1_value=sku_values[0],
                sku2_value=sku_values[1],
                sku3_value=sku_values[2]
            )
            rows.append(row)
        
        return rows
