"""RFP upload and extraction API routes."""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from ...db.database import get_db
from ...services.rfp_extraction_service import RFPExtractionService
from ...services.pdf_parser_service import PDFParserService
from ...services.rfp_parser_service import RFPParserService
from ...agents.graph import get_workflow
from ...api.services.rfp_service import RFPService
from ...models.rfp_models import RFP
from ...api.services.sku_service import SKUService
from ...api.api_schemas import (
    SKUCreate,
    SKUFeatureBase,
    SKUPricingBase,
    SKUResponse,
    RFPCreate,
    RFPItemCreate,
    RFPTestRequirementCreate
)
from ...config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rfp-upload", tags=["RFP Upload"])


@router.post("/extract-and-create-sku")
async def extract_rfp_and_create_sku(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    run_workflow: bool = Query(True, description="Run agentic workflow after storing RFP")
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
        
        # Extract and convert RFP to SKU format
        extraction_service = RFPExtractionService()
        sku_data_dict = extraction_service.process_rfp_pdf_complete(
            pdf_bytes,
            file.filename
        )

        # Parse full RFP for storage and workflow
        pdf_parser = PDFParserService()
        rfp_parser = RFPParserService()
        pdf_text = pdf_parser.extract_text_from_bytes(pdf_bytes)

        base_name = file.filename.rsplit('.', 1)[0].strip()
        rfp_id = f"RFP-UPLOAD-{base_name[:20].upper().replace(' ', '_')}-{uuid.uuid4().hex[:6].upper()}"
        source_url = f"upload://{file.filename}"

        parsed_rfp = rfp_parser.parse_rfp_document(pdf_text, rfp_id=rfp_id, source_url=source_url)
        if not parsed_rfp:
            # Fallback minimal RFP for storage and workflow
            parsed_rfp = RFP(
                rfp_id=rfp_id,
                title=f"RFP Upload - {file.filename}",
                source_url=source_url,
                submission_deadline=datetime.utcnow() + timedelta(days=30),
                buyer=None,
                summary=pdf_text[:200] if pdf_text else None,
                scope_of_supply=[],
                test_requirements=[],
                raw_text=pdf_text
            )

        if not parsed_rfp.raw_text:
            parsed_rfp.raw_text = pdf_text

        # Persist parsed RFP to disk for workflow use
        rfp_parser.save_parsed_rfp(parsed_rfp)

        # Build RFPCreate for database
        submission_deadline = parsed_rfp.submission_deadline or (datetime.utcnow() + timedelta(days=30))
        rfp_create = RFPCreate(
            rfp_id=parsed_rfp.rfp_id,
            title=parsed_rfp.title or f"RFP Upload - {file.filename}",
            source_url=parsed_rfp.source_url or source_url,
            submission_deadline=submission_deadline,
            buyer=parsed_rfp.buyer,
            summary=parsed_rfp.summary,
            raw_text=parsed_rfp.raw_text,
            items=[
                RFPItemCreate(
                    item_id=item.item_id or f"ITEM-{uuid.uuid4().hex[:6].upper()}",
                    description=item.description or "Item",
                    quantity=item.quantity if item.quantity and item.quantity > 0 else 1.0,
                    unit=item.unit or "unit",
                    specs=item.specs or {}
                )
                for item in parsed_rfp.scope_of_supply
            ],
            test_requirements=[
                RFPTestRequirementCreate(
                    test_id=f"TEST-{uuid.uuid4().hex[:6].upper()}",
                    test_name=test_req.test_name or "Test",
                    description=test_req.description or "Not specified",
                    required_standard=test_req.required_standard or "Not specified",
                    frequency=test_req.frequency
                )
                for test_req in parsed_rfp.test_requirements
            ]
        )

        # Store RFP in database
        RFPService.create_rfp(db, rfp_create)
        
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
        
        response: Dict[str, Any] = {
            "success": True,
            "message": f"RFP processed and SKU created successfully",
            "rfp_id": parsed_rfp.rfp_id,
            "sku_id": created_sku.sku_id,
            "product_name": created_sku.product_name,
            "category": created_sku.category,
            "features_count": len(created_sku.features),
            "pricing_count": len(created_sku.pricing)
        }

        if run_workflow:
            try:
                workflow = get_workflow()
                workflow_result = workflow.run_full_workflow_for_rfp(parsed_rfp.rfp_id)
                response["workflow_result"] = workflow_result.model_dump()
            except Exception as workflow_error:
                logger.error(f"Workflow error for RFP {parsed_rfp.rfp_id}: {workflow_error}")
                response["workflow_error"] = str(workflow_error)

        return response
    
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
