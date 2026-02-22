"""Retrieval layer for vector search using Cohere embeddings and Qdrant."""

import logging
from typing import List, Optional

from qdrant_client import QdrantClient
import cohere

from ..config import settings
from ..models.rfp_models import RFPItem
from ..models.sku_models import SKU
from ..data_ingestion.sku_loader import load_skus

logger = logging.getLogger(__name__)


class SKURetriever:
    """Retriever for SKU product specifications using Cohere and Qdrant."""
    
    def __init__(self):
        """Initialize SKU retriever with Cohere and Qdrant clients."""
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False
        )
        self.cohere_client = cohere.ClientV2(api_key=settings.cohere_api_key)
        self.collection_name = "sku_index"
        logger.info(f"SKU Retriever initialized (Qdrant: {settings.qdrant_url})")
    
    def get_sku_candidates(
        self,
        rfp_item: RFPItem,
        top_k: int = 10
    ) -> List[dict]:
        """Retrieve candidate SKUs for an RFP item using vector similarity.
        
        Args:
            rfp_item: RFP item to match
            top_k: Number of candidates to return
            
        Returns:
            List of SKU dictionaries with metadata and similarity scores
        """
        try:
            # Build query from RFP item
            query = self._build_query(rfp_item)
            logger.info(f"Searching for SKUs with query: {query}")
            
            # Generate query embedding using Cohere
            query_response = self.cohere_client.embed(
                model="embed-english-v3-large",
                input_type="search_query",
                texts=[query]
            )
            query_embedding = query_response.embeddings[0]
            logger.info(f"Generated query embedding (dimension: {len(query_embedding)})")
            
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            logger.info(f"Found {len(search_result)} candidate points")
            
            # Convert search results to SKU candidates
            candidates = []
            for point in search_result:
                metadata = point.payload.get("metadata", {})
                candidates.append({
                    "sku_id": metadata.get("sku_id", ""),
                    "product_name": metadata.get("product_name", ""),
                    "category": metadata.get("category", ""),
                    "features": metadata.get("features", {}),
                    "score": point.score,  # Similarity score
                    "text": point.payload.get("text", "")
                })
            
            logger.info(f"Returning {len(candidates)} SKU candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Error retrieving SKU candidates: {e}")
            logger.warning("Falling back to CSV-based retrieval")
            return self._fallback_get_all_skus()
    
    def _fallback_get_all_skus(self) -> List[dict]:
        """Fallback method to load all SKUs from CSV when Qdrant fails.
        
        Returns:
            List of all SKUs as dictionaries
        """
        try:
            repository = load_skus()
            candidates = []
            for sku in repository.skus:
                candidates.append({
                    "sku_id": sku.sku_id,
                    "product_name": sku.product_name,
                    "category": sku.category,
                    "features": {f.name: str(f.value) for f in sku.features},
                    "score": 0.5,  # Neutral score for fallback
                    "text": f"{sku.product_name} {sku.category}"
                })
            logger.info(f"Fallback: Loaded {len(candidates)} SKUs from CSV")
            return candidates
        except Exception as e:
            logger.error(f"Error in fallback SKU loading: {e}")
            return []
    
    def _build_query(self, rfp_item: RFPItem) -> str:
        """Build search query from RFP item.
        
        Args:
            rfp_item: RFP item
            
        Returns:
            Query string
        """
        parts = [rfp_item.description]
        
        # Add specifications to query
        for spec_name, spec_value in rfp_item.specs.items():
            parts.append(f"{spec_name}: {spec_value}")
        
        return " ".join(parts)


# Global retriever (lazy loaded)
_sku_retriever: Optional[SKURetriever] = None


def get_sku_retriever() -> SKURetriever:
    """Get global SKU retriever instance."""
    global _sku_retriever
    if _sku_retriever is None:
        _sku_retriever = SKURetriever()
    return _sku_retriever


def get_sku_candidates(rfp_item: RFPItem, top_k: int = 10) -> List[dict]:
    """Convenience function to get SKU candidates.
    
    Args:
        rfp_item: RFP item to match
        top_k: Number of candidates
        
    Returns:
        List of candidate SKUs
    """
    retriever = get_sku_retriever()
    return retriever.get_sku_candidates(rfp_item, top_k)
