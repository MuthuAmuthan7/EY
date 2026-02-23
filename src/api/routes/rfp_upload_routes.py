"""RFP upload and extraction API routes."""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from ...db.database import get_db
from ...services.rfp_extraction_service import RFPExtractionService
from ...api.services.sku_service import SKUService
from ...api.api_schemas import SKUCreate, SKUFeatureBase, SKUPricingBase, SKUResponse
from ...config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rfp-upload", tags=["RFP Upload"])


@router.post("/extract-and-create-sku")
async def extract_rfp_and_create_sku(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Upload RFP PDF, extract data, and create SKU in database.
    
    Args:
        file: PDF file upload
        db: Database session
        
    Returns:
        Created SKU data
    """
    logger.info(f"Received RFP PDF upload: {file.filename}")
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Read file bytes
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="PDF file is empty")
        
        logger.info(f"PDF size: {len(pdf_bytes)} bytes")
        
        # Extract and convert RFP
        extraction_service = RFPExtractionService()
        sku_data_dict = extraction_service.process_rfp_pdf_complete(
            pdf_bytes,
            file.filename
        )
        
        logger.info(f"Extracted SKU data: {sku_data_dict['sku_id']}")
        
        # Convert to SKUCreate schema
        features = [
            SKUFeatureBase(
                name=f["name"],
                value=f["value"],
                unit=f.get("unit")
            )
            for f in sku_data_dict.get("features", [])
        ]
        
        pricing = [
            SKUPricingBase(
                unit_price=p["unit_price"],
                currency=p.get("currency", "INR")
            )
            for p in sku_data_dict.get("pricing", [])
        ]
        
        sku_create = SKUCreate(
            sku_id=sku_data_dict["sku_id"],
            product_name=sku_data_dict["product_name"],
            category=sku_data_dict["category"],
            description=sku_data_dict.get("description", ""),
            raw_record=sku_data_dict.get("raw_record", {}),
            features=features,
            pricing=pricing
        )
        
        # Create SKU in database
        created_sku = SKUService.create_sku(db, sku_create)
        
        logger.info(f"Successfully created SKU in database: {created_sku.sku_id}")
        
        return {
            "success": True,
            "message": f"RFP processed and SKU created successfully",
            "sku_id": created_sku.sku_id,
            "product_name": created_sku.product_name,
            "category": created_sku.category,
            "features_count": len(created_sku.features),
            "pricing_count": len(created_sku.pricing)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing RFP upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing RFP: {str(e)}"
        )


@router.post("/preview")
async def preview_rfp_extraction(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Preview RFP extraction without saving to database.
    
    Args:
        file: PDF file upload
        
    Returns:
        Extracted RFP and converted SKU preview data
    """
    logger.info(f"Received RFP preview request: {file.filename}")
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Read file bytes
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="PDF file is empty")
        
        # Extract RFP data
        extraction_service = RFPExtractionService()
        sku_data = extraction_service.process_rfp_pdf_complete(
            pdf_bytes,
            file.filename
        )
        
        logger.info(f"Generated preview for SKU: {sku_data['sku_id']}")
        
        return {
            "success": True,
            "sku_id": sku_data["sku_id"],
            "product_name": sku_data["product_name"],
            "category": sku_data["category"],
            "description": sku_data["description"][:200] + "..." if len(sku_data["description"]) > 200 else sku_data["description"],
            "features_count": len(sku_data.get("features", [])),
            "features": sku_data.get("features", [])[:5],  # First 5 features
            "raw_record": sku_data.get("raw_record", {})
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing RFP extraction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error previewing RFP: {str(e)}"
        )
