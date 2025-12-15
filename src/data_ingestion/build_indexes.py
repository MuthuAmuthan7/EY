"""Build vector indexes for SKUs using HuggingFace embeddings."""

import logging
from pathlib import Path

from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
    Settings
)
from langchain_huggingface import HuggingFaceEmbeddings

from ..config import settings as app_settings
from .sku_loader import load_skus
from ..models.sku_models import SKU

logger = logging.getLogger(__name__)


def build_sku_index(force_rebuild: bool = False) -> bool:
    """Build vector index for SKU product specifications using HuggingFace embeddings.
    
    Args:
        force_rebuild: Force rebuild even if index exists
        
    Returns:
        True if successful
    """
    index_dir = app_settings.get_sku_index_dir()
    
    # Check if index already exists
    if index_dir.exists() and not force_rebuild:
        logger.info(f"SKU index already exists at {index_dir}")
        return True
    
    logger.info("Building SKU vector index with HuggingFace embeddings...")
    
    try:
        logger.info("Configuring HuggingFace embeddings...")
        
        # Configure LlamaIndex settings for HuggingFace embeddings
        Settings.embed_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        logger.info("Loading SKUs from product_specs.csv...")
        # Load SKUs
        repository = load_skus()
        
        if len(repository) == 0:
            logger.warning("No SKUs loaded from product_specs.csv")
            return False
        
        logger.info(f"✓ Loaded {len(repository)} SKUs")
        
        # Convert SKUs to documents
        documents = []
        for sku in repository.skus:
            doc_text = _sku_to_text(sku)
            metadata = {
                "sku_id": sku.sku_id,
                "product_name": sku.product_name,
                "category": sku.category,
                "features": {f.name: f.value for f in sku.features}
            }
            
            doc = Document(
                text=doc_text,
                metadata=metadata
            )
            documents.append(doc)
        
        logger.info(f"✓ Created {len(documents)} documents for indexing")
        
        logger.info("Building vector index (this may take a minute)...")
        # Build index
        index = VectorStoreIndex.from_documents(
            documents,
            show_progress=True
        )
        
        logger.info("✓ Vector index created, persisting to disk...")
        # Persist index
        index_dir.mkdir(parents=True, exist_ok=True)
        index.storage_context.persist(persist_dir=str(index_dir))
        
        logger.info(f"✓ SKU index built and saved to {index_dir}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error building SKU index: {e}", exc_info=True)
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return False


def _sku_to_text(sku: SKU) -> str:
    """Convert SKU to text representation for indexing.
    
    Args:
        sku: SKU object
        
    Returns:
        Text representation
    """
    parts = [
        f"Product: {sku.product_name}",
        f"Category: {sku.category}",
        f"SKU ID: {sku.sku_id}",
        "Specifications:"
    ]
    
    for feature in sku.features:
        unit_str = f" {feature.unit}" if feature.unit else ""
        parts.append(f"  - {feature.name}: {feature.value}{unit_str}")
    
    return "\n".join(parts)


def build_all_indexes(force_rebuild: bool = False) -> bool:
    """Build all vector indexes.
    
    Args:
        force_rebuild: Force rebuild even if indexes exist
        
    Returns:
        True if all successful
    """
    logger.info("Building all indexes with HuggingFace embeddings...")
    
    success = build_sku_index(force_rebuild)
    
    if success:
        logger.info("All indexes built successfully")
    else:
        logger.error("Some indexes failed to build")
    
    return success


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Build indexes
    build_all_indexes(force_rebuild=True)
