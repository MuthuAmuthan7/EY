"""Example usage of RFP extraction system."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.rfp_extraction_service import RFPExtractionService
from src.llm.client import LLMClient
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_direct_text_parsing():
    """Example: Parse RFP from raw text."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: Direct RFP Text Parsing")
    logger.info("=" * 60)
    
    # Sample RFP text
    sample_text = """
    REQUEST FOR PROPOSAL
    
    Product Name: Industrial Grade Power Cable
    Category: Electrical Components
    
    Specifications:
    - Conductor Material: Copper
    - Conductor Size: 240 sq.mm
    - Insulation Type: XLPE
    - Voltage Grade: 1.1 kV
    - Maximum Temperature: 90°C
    - Minimum Bend Radius: 12D (where D is cable diameter)
    
    Description:
    High-quality 3.5 core power cable suitable for industrial applications.
    The cable is designed to withstand harsh environmental conditions and
    provides excellent electrical performance.
    
    Quantity Required: 1000 meters
    Delivery Timeline: 30 days from order
    
    Testing Requirements:
    - Insulation Resistance Test
    - Tensile Strength Test
    - Temperature Cycling Test
    - Flame Retardancy Test
    
    Pricing Information:
    The supplier should provide competitive pricing for bulk quantities.
    Price breaks for different quantity ranges are expected.
    """
    
    try:
        # Initialize service
        service = RFPExtractionService()
        
        # Parse RFP from text
        logger.info("Parsing RFP from text...")
        rfp_data = service.extract_rfp_from_text(sample_text, "sample_rfp.txt")
        
        logger.info("\n✅ Extracted RFP Data:")
        print(json.dumps(rfp_data, indent=2))
        
        # Convert to SKU format
        logger.info("\nConverting to SKU format...")
        sku_data = service.convert_rfp_to_sku(rfp_data)
        
        logger.info("\n✅ Converted SKU Data:")
        print(json.dumps(sku_data, indent=2, default=str))
        
        return sku_data
    
    except Exception as e:
        logger.error(f"Error in direct text parsing: {e}", exc_info=True)
        return None


def example_pdf_processing():
    """Example: Process RFP from PDF file."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 2: PDF RFP Processing")
    logger.info("=" * 60)
    
    pdf_path = "sample_rfp.pdf"  # Replace with actual PDF path
    
    try:
        import os
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF file not found: {pdf_path}")
            logger.info("To test PDF processing:")
            logger.info("1. Place a sample RFP PDF in the project root")
            logger.info("2. Update pdf_path in this script")
            logger.info("3. Run this script again")
            return None
        
        # Initialize service
        service = RFPExtractionService()
        
        # Read PDF bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        logger.info(f"Processing PDF: {pdf_path}")
        logger.info(f"PDF size: {len(pdf_bytes)} bytes")
        
        # Process complete pipeline
        sku_data = service.process_rfp_pdf_complete(pdf_bytes, pdf_path)
        
        logger.info("\n✅ Processed SKU Data:")
        print(json.dumps(sku_data, indent=2, default=str))
        
        return sku_data
    
    except FileNotFoundError:
        logger.error(f"PDF file not found: {pdf_path}")
        return None
    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        return None


def example_api_integration():
    """Example: Using the service with API."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 3: API Integration Example")
    logger.info("=" * 60)
    
    logger.info("""
    To use with the FastAPI backend:
    
    1. Start the API:
       uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    
    2. Upload RFP using curl:
       curl -X POST "http://localhost:8000/api/v1/rfp-upload/extract-and-create-sku" \\
         -F "file=@path/to/rfp.pdf"
    
    3. Or use Python requests:
       import requests
       
       with open('rfp.pdf', 'rb') as f:
           files = {'file': f}
           response = requests.post(
               'http://localhost:8000/api/v1/rfp-upload/extract-and-create-sku',
               files=files
           )
       print(response.json())
    
    4. Preview without saving:
       curl -X POST "http://localhost:8000/api/v1/rfp-upload/preview" \\
         -F "file=@path/to/rfp.pdf"
    """)


def example_streamlit_app():
    """Example: Using the Streamlit app."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 4: Streamlit App Usage")
    logger.info("=" * 60)
    
    logger.info("""
    To use the Streamlit web interface:
    
    1. Start Streamlit:
       streamlit run web/rfp_upload_app.py
    
    2. Open browser:
       http://localhost:8501
    
    3. Features:
       - Upload RFP PDF with drag-and-drop
       - Preview extraction before saving
       - View upload history
       - Export history as JSON
       - Comprehensive help documentation
    """)


def main():
    """Run examples."""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " RFP Extraction System - Usage Examples".center(58) + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    # Run examples
    example_direct_text_parsing()
    example_pdf_processing()
    example_api_integration()
    example_streamlit_app()
    
    logger.info("\n" + "=" * 60)
    logger.info("Examples complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
