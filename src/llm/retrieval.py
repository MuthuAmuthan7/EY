"""Retrieval layer using LlamaIndex for vector search with HuggingFace embeddings."""

import logging
from pathlib import Path
from typing import List, Optional

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Document,
    Settings
)
from llama_index.core.node_parser import SimpleNodeParser
from langchain_huggingface import HuggingFaceEmbeddings

from ..config import settings
from ..models.rfp_models import RFPItem
from ..models.sku_models import SKU
from ..data_ingestion.sku_loader import load_skus

logger = logging.getLogger(__name__)


class SKURetriever:
    """Retriever for SKU product specifications."""
    
    def __init__(self, index_path: Optional[Path] = None):
        """Initialize SKU retriever.
        
        Args:
            index_path: Path to persisted index (defaults to settings)
        """
        self.index_path = index_path or settings.get_sku_index_dir()
        self.index: Optional[VectorStoreIndex] = None
        self._load_index()
    
    def _load_index(self):
        """Load existing index from disk."""
        try:
            if self.index_path.exists():
                # Configure HuggingFace embeddings before loading index
                Settings.embed_model = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-mpnet-base-v2"
                )
                
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(self.index_path)
                )
                self.index = load_index_from_storage(storage_context)
                logger.info(f"Loaded SKU index from {self.index_path}")
            else:
                logger.warning(f"SKU index not found at {self.index_path}")
        except Exception as e:
            logger.error(f"Error loading SKU index: {e}")
    
    def get_sku_candidates(
        self,
        rfp_item: RFPItem,
        top_k: int = 10
    ) -> List[dict]:
        """Retrieve candidate SKUs for an RFP item.
        
        Args:
            rfp_item: RFP item to match
            top_k: Number of candidates to return
            
        Returns:
            List of SKU dictionaries with metadata
        """
        # If index is not loaded, use fallback immediately
        if not self.index:
            logger.warning("SKU index not loaded. Using fallback: returning all SKUs from CSV")
            return self._fallback_get_all_skus()
        
        # Build query from RFP item
        query = self._build_query(rfp_item)
        logger.info(f"Searching for SKUs with query: {query}")
        
        try:
            # Query the index
            query_engine = self.index.as_query_engine(
                similarity_top_k=top_k
            )
            response = query_engine.query(query)
            
            # Extract SKU data from response
            candidates = []
            
            # Check if we have source nodes
            if hasattr(response, 'source_nodes') and response.source_nodes:
                logger.info(f"Found {len(response.source_nodes)} candidate nodes")
                for node in response.source_nodes:
                    candidates.append({
                        "sku_id": node.metadata.get("sku_id", ""),
                        "product_name": node.metadata.get("product_name", ""),
                        "category": node.metadata.get("category", ""),
                        "features": node.metadata.get("features", {}),
                        "score": node.score if hasattr(node, 'score') else 0,
                        "text": node.text if hasattr(node, 'text') else ""
                    })
            else:
                logger.warning(f"No source nodes found in response. Response type: {type(response)}")
                logger.warning(f"Response: {response}")
            
            if not candidates:
                logger.warning(f"No SKU candidates found for: {query}")
                logger.info("Falling back to all SKUs in repository...")
                # Fallback: return all SKUs from the repository
                candidates = self._fallback_get_all_skus()
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error querying SKU index: {e}", exc_info=True)
            logger.info("Falling back to all SKUs in repository due to error...")
            return self._fallback_get_all_skus()
    
    def _fallback_get_all_skus(self) -> List[dict]:
        """Fallback method to load all SKUs from CSV when index fails.
        
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
                    "features": {f.name: f.value for f in sku.features},
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


class RFPRetriever:
    """Retriever for RFP documents (optional)."""
    
    def __init__(self, index_path: Optional[Path] = None):
        """Initialize RFP retriever.
        
        Args:
            index_path: Path to persisted index (defaults to settings)
        """
        self.index_path = index_path or settings.get_rfp_index_dir()
        self.index: Optional[VectorStoreIndex] = None
        self._load_index()
    
    def _load_index(self):
        """Load existing index from disk."""
        try:
            if self.index_path.exists():
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(self.index_path)
                )
                self.index = load_index_from_storage(storage_context)
                logger.info(f"Loaded RFP index from {self.index_path}")
            else:
                logger.info(f"RFP index not found at {self.index_path} (optional)")
        except Exception as e:
            logger.error(f"Error loading RFP index: {e}")
    
    def search_similar_rfps(self, query: str, top_k: int = 5) -> List[dict]:
        """Search for similar RFPs.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of similar RFP metadata
        """
        if not self.index:
            return []
        
        try:
            query_engine = self.index.as_query_engine(similarity_top_k=top_k)
            response = query_engine.query(query)
            
            results = []
            for node in response.source_nodes:
                results.append({
                    "rfp_id": node.metadata.get("rfp_id", ""),
                    "title": node.metadata.get("title", ""),
                    "score": node.score,
                    "text": node.text
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching RFPs: {e}")
            return []


# Global retrievers (lazy loaded)
_sku_retriever: Optional[SKURetriever] = None
_rfp_retriever: Optional[RFPRetriever] = None


def get_sku_retriever() -> SKURetriever:
    """Get global SKU retriever instance."""
    global _sku_retriever
    if _sku_retriever is None:
        _sku_retriever = SKURetriever()
    return _sku_retriever


def get_rfp_retriever() -> RFPRetriever:
    """Get global RFP retriever instance."""
    global _rfp_retriever
    if _rfp_retriever is None:
        _rfp_retriever = RFPRetriever()
    return _rfp_retriever


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
