"""Workflow/Agent orchestration API routes."""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

from src.agents.graph import get_workflow
from src.api.schema import (
    SalesRFPOverview,
    FinalRFPResponse
)

router = APIRouter(prefix="/api/v1/workflow", tags=["Workflow"])

logger = logging.getLogger(__name__)


@router.get("/scan-rfps", response_model=List[SalesRFPOverview])
async def scan_rfps():
    """Scan for available RFPs.
    
    Returns:
        List of RFP overviews
    """
    try:
        workflow = get_workflow()
        rfps = workflow.run_sales_scan()
        return rfps
    except Exception as e:
        logger.error(f"Error scanning RFPs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error scanning RFPs: {str(e)}")


@router.post("/process-rfp/{rfp_id}", response_model=FinalRFPResponse)
async def process_rfp(rfp_id: str):
    """Run full workflow for a specific RFP.
    
    Args:
        rfp_id: RFP identifier
        
    Returns:
        Final RFP response with recommendations and pricing
    """
    try:
        logger.info(f"Processing RFP: {rfp_id}")
        workflow = get_workflow()
        result = workflow.run_full_workflow_for_rfp(rfp_id)
        logger.info(f"Successfully processed RFP: {rfp_id}")
        return result
    except ValueError as e:
        logger.error(f"RFP not found: {rfp_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing RFP {rfp_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing RFP: {str(e)}")
