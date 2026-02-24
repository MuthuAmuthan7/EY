"""Build vector indexes for SKUs using Cohere embeddings and Qdrant."""

import logging
from pathlib import Path
import json
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import cohere

from ..config import settings as app_settings
from .sku_loader import load_skus
from ..models.sku_models import SKU

logger = logging.getLogger(__name__)


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


def build_sku_index(force_rebuild: bool = False) -> bool:
    """Build vector index for SKU product specifications using Cohere embeddings and Qdrant.
    
    Args:
        force_rebuild: Force rebuild even if index exists
        
    Returns:
        True if successful
    """
    logger.info("Building SKU vector index with Cohere embeddings and Qdrant...")
    
    try:
        # Initialize Cohere client
        cohere_client = cohere.ClientV2(api_key=app_settings.cohere_api_key)
        logger.info("✓ Cohere client initialized")
        
        # Initialize Qdrant client
        qdrant_client = QdrantClient(
            url=app_settings.qdrant_url,
            api_key=app_settings.qdrant_api_key,
            prefer_grpc=False
        )
        logger.info(f"✓ Qdrant client connected to {app_settings.qdrant_url}")
        
        # Load SKUs from CSV
        logger.info("Loading SKUs from product_specs.csv...")
        repository = load_skus()
        
        if len(repository.skus) == 0:
            logger.warning("No SKUs loaded from product_specs.csv")
            return False
        
        logger.info(f"✓ Loaded {len(repository.skus)} SKUs")
        
        # Convert SKUs to text documents
        documents = []
        for sku in repository.skus:
            doc_text = _sku_to_text(sku)
            doc_metadata = {
                "sku_id": sku.sku_id,
                "product_name": sku.product_name,
                "category": sku.category,
                "features": {f.name: str(f.value) for f in sku.features}
            }
            documents.append({
                "text": doc_text,
                "metadata": doc_metadata,
                "id": str(uuid.uuid4())
            })
        
        logger.info(f"✓ Created {len(documents)} documents for indexing")
        
        # Generate embeddings using Cohere
        logger.info("Generating embeddings using Cohere (embed-v4.0)...")
        
        # Batch embeddings to avoid rate limits
        batch_size = 100
        all_texts = [doc["text"] for doc in documents]
        all_embeddings = []
        
        for i in range(0, len(all_texts), batch_size):
            batch_texts = all_texts[i:i + batch_size]
            logger.info(f"  Embedding batch {i // batch_size + 1}/{(len(all_texts) + batch_size - 1) // batch_size}")
            
            response = cohere_client.embed(
                model="embed-v4.0",
                input_type="search_document",
                texts=batch_texts
            )
            all_embeddings.extend(response.embeddings)
        
        logger.info(f"✓ Generated {len(all_embeddings)} embeddings")
        
        # Create or recreate collection
        collection_name = "sku_index"
        
        try:
            qdrant_client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted existing collection: {collection_name}")
        except Exception:
            pass  # Collection doesn't exist yet
        
        # Create collection with embedding dimension
        embedding_dim = len(all_embeddings[0]) if all_embeddings else 1024
        logger.info(f"Creating Qdrant collection: {collection_name} (dim={embedding_dim})")
        
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
        )
        logger.info(f"✓ Collection created")
        
        # Create points from documents and embeddings
        logger.info("Preparing points for upload to Qdrant...")
        points = []
        for idx, (doc, embedding) in enumerate(zip(documents, all_embeddings)):
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "text": doc["text"],
                    "metadata": doc["metadata"]
                }
            )
            points.append(point)
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch_points = points[i:i + batch_size]
            qdrant_client.upsert(
                collection_name=collection_name,
                points=batch_points
            )
            logger.info(f"  Uploaded {min(i + batch_size, len(points))}/{len(points)} points")
        
        logger.info(f"✓ SKU index created in Qdrant (collection: {collection_name})")
        logger.info(f"  Total points: {len(points)}")
        logger.info(f"  Embedding dimension: {embedding_dim}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error building SKU index: {e}", exc_info=True)
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return False


def build_all_indexes(force_rebuild: bool = False) -> bool:
    """Build all vector indexes.
    
    Args:
        force_rebuild: Force rebuild even if indexes exist
        
    Returns:
        True if all successful
    """
    logger.info("=" * 60)
    logger.info("Building all indexes with Cohere embeddings and Qdrant")
    logger.info("=" * 60)
    
    success = True
    
    # Build SKU index
    if not build_sku_index(force_rebuild=force_rebuild):
        logger.error("Failed to build SKU index")
        success = False
    
    logger.info("=" * 60)
    if success:
        logger.info("✓ All indexes built successfully")
    else:
        logger.error("✗ Some indexes failed to build")
    logger.info("=" * 60)
    
    return success


if __name__ == "__main__":
    # For direct execution: python -m src.data_ingestion.build_indexes
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    build_all_indexes(force_rebuild=True)