"""Streamlit app for RFP PDF upload and extraction."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import logging
import requests
import json
import os
from io import BytesIO

from src.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# API Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_BASE_URL = f"http://{API_HOST}:8000/api/v1"
RFP_UPLOAD_API = f"{API_BASE_URL}/rfp-upload"

# Page configuration
st.set_page_config(
    page_title="RFP Upload & Extraction",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling - Minimal & Modern
st.markdown("""
    <style>
    /* Base styles */
    .main {
        padding: 2rem;
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 3rem 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    .hero h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .hero p {
        margin: 0.75rem 0 0;
        opacity: 0.85;
        font-size: 1.05rem;
    }
    
    /* Feature cards */
    .card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        text-align: center;
    }
    .card:hover {
        border-color: #d1d5db;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .card b {
        font-size: 1.1rem;
        color: #1f2937;
    }
    
    /* Tabs styling */
    [data-baseweb="tab-list"] {
        border-bottom: 1px solid #e5e7eb;
    }
    [data-baseweb="tab-list"] button {
        font-size: 15px;
        font-weight: 500;
        padding: 12px 16px;
        color: #6b7280;
    }
    [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #1f2937;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* Upload section */
    .upload-section {
        border: 2px dashed #3b82f6;
        border-radius: 10px;
        padding: 2.5rem;
        text-align: center;
        background-color: #f0f9ff;
        transition: all 0.3s ease;
    }
    .upload-section:hover {
        background-color: #e0f2fe;
        border-color: #0ea5e9;
    }
    
    /* Alert boxes - Modern minimal style */
    .success-box {
        background-color: #ecfdf5;
        border: 1px solid #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    .error-box {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        color: #7f1d1d;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    .info-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e40af;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0;
    }
    
    /* Metric boxes */
    [data-testid="metric-container"] {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
    }
    
    /* Expanders */
    [data-baseweb="accordion"] {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'upload_history' not in st.session_state:
        st.session_state.upload_history = []
    if 'last_extraction' not in st.session_state:
        st.session_state.last_extraction = None
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None


def upload_and_extract_rfp(uploaded_file, run_workflow: bool) -> dict:
    """Upload RFP PDF and extract/create SKU.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Response from API
    """
    logger.info(f"Uploading file: {uploaded_file.name}, run_workflow: {run_workflow}")
    
    try:
        # Prepare file for upload
        files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
        
        # Call API
        with st.spinner("🔄 Processing RFP PDF..."):
            response = requests.post(
                f"{RFP_UPLOAD_API}/extract-and-create-sku",
                files=files,
                params={"run_workflow": str(run_workflow).lower()},
                timeout=60
            )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"RFP processing successful: {result}")
        return result
    
    except requests.exceptions.Timeout:
        logger.error("API request timeout")
        raise Exception("Request timeout - processing took too long")
    except requests.exceptions.ConnectionError:
        logger.error("API connection error")
        raise Exception(f"Cannot connect to API at {RFP_UPLOAD_API}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"API error: {e.response.text}")
        try:
            error_detail = e.response.json().get('detail', str(e))
        except:
            error_detail = str(e)
        raise Exception(f"API Error: {error_detail}")
    except Exception as e:
        logger.error(f"Error uploading RFP: {str(e)}", exc_info=True)
        raise


def preview_rfp_extraction(uploaded_file) -> dict:
    """Preview RFP extraction without saving to database.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Preview data from API
    """
    logger.info(f"Previewing file: {uploaded_file.name}")
    
    try:
        # Prepare file for upload
        files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
        
        # Call API
        with st.spinner("👁️ Generating preview..."):
            response = requests.post(
                f"{RFP_UPLOAD_API}/preview",
                files=files,
                timeout=60
            )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"Preview generated: {result}")
        return result
    
    except requests.exceptions.Timeout:
        logger.error("API request timeout")
        raise Exception("Request timeout - preview took too long")
    except requests.exceptions.ConnectionError:
        logger.error("API connection error")
        raise Exception(f"Cannot connect to API at {RFP_UPLOAD_API}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"API error: {e.response.text}")
        try:
            error_detail = e.response.json().get('detail', str(e))
        except:
            error_detail = str(e)
        raise Exception(f"API Error: {error_detail}")
    except Exception as e:
        logger.error(f"Error previewing RFP: {str(e)}", exc_info=True)
        raise


def display_sku_preview(preview_data: dict):
    """Display SKU preview data.
    
    Args:
        preview_data: Preview data dictionary
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 SKU Information")
        st.write(f"**SKU ID:** `{preview_data['sku_id']}`")
        st.write(f"**Product Name:** {preview_data['product_name']}")
        st.write(f"**Category:** {preview_data['category']}")
    
    with col2:
        st.markdown("### 📊 Extracted Data")
        st.write(f"**Features Extracted:** {preview_data['features_count']}")
        st.write(f"**Description Length:** {len(preview_data['description'])} chars")
    
    # Display features
    if preview_data.get('features'):
        st.markdown("### 🔧 Extracted Features (Sample)")
        
        for feature in preview_data['features'][:5]:
            with st.container():
                col_name, col_value, col_unit = st.columns([2, 2, 1])
                with col_name:
                    st.write(f"**{feature.get('name', 'N/A')}**")
                with col_value:
                    st.write(feature.get('value', 'N/A'))
                with col_unit:
                    st.write(feature.get('unit', ''))
    
    # Display description
    if preview_data.get('description'):
        st.markdown("### 📝 Description")
        st.text(preview_data['description'])
    
    # Display raw extracted data
    if st.checkbox("Show Raw Extracted Data"):
        st.markdown("### 📋 Raw RFP Data")
        st.json(preview_data.get('raw_record', {}))


def display_upload_history():
    """Display upload history in sidebar."""
    if st.session_state.upload_history:
        st.sidebar.markdown("### 📜 Upload History")
        for idx, item in enumerate(reversed(st.session_state.upload_history), 1):
            with st.sidebar.expander(f"{idx}. {item['filename']}"):
                st.write(f"**SKU ID:** `{item['sku_id']}`")
                st.write(f"**Product:** {item['product_name']}")
                st.write(f"**Status:** {item['status']}")
                if item.get('timestamp'):
                    st.write(f"**Time:** {item['timestamp']}")


def main():
    """Main app function."""
    init_session_state()
    
    # Header
    st.markdown(
        """
        <div class="hero">
            <h1>📄 RFP Upload & SKU Extraction</h1>
            <p>Upload RFP PDFs to extract structured data and generate SKUs automatically.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("<div class='card'>📤 <b>Upload</b><br/>Drop a PDF and start extraction.</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<div class='card'>🧩 <b>Extract</b><br/>Features, specs, and metadata.</div>", unsafe_allow_html=True)
    with col_c:
        st.markdown("<div class='card'>🗂️ <b>Store</b><br/>Save RFP + SKU to SQLite.</div>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload RFP", "📊 View History", "ℹ️ Help"])
    
    with tab1:
        st.markdown("### Upload RFP PDF")
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown("#### Select PDF File")
            uploaded_file = st.file_uploader(
                "Choose an RFP PDF file",
                type=['pdf'],
                help="Upload a PDF containing RFP (Request for Proposal) details"
            )
        
        with col_right:
            st.markdown("#### Options")
            preview_mode = st.checkbox(
                "Preview Only",
                value=False,
                help="Preview extraction without saving to database"
            )
            run_workflow = st.checkbox(
                "Run AI Workflow",
                value=True,
                help="Run the full agentic workflow after saving the RFP"
            )
        
        if uploaded_file:
            st.markdown("---")
            
            file_info_col1, file_info_col2 = st.columns(2)
            with file_info_col1:
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**File Size:** {uploaded_file.size / 1024:.2f} KB")
            
            with file_info_col2:
                st.write(f"**Type:** PDF Document")
            
            st.markdown("---")
            
            # Action buttons
            col_submit, col_reset = st.columns(2)
            
            with col_submit:
                if st.button("🚀 Process RFP", use_container_width=True):
                    try:
                        if preview_mode:
                            # Preview mode
                            result = preview_rfp_extraction(uploaded_file)
                            
                            if result.get('success'):
                                st.session_state.preview_data = result
                                
                                # Display success message
                                st.markdown(
                                    f"""
                                    <div class="success-box">
                                    ✅ Preview generated successfully!
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                                # Display preview data
                                display_sku_preview(result)
                        else:
                            # Full processing mode
                            result = upload_and_extract_rfp(uploaded_file, run_workflow)
                            
                            if result.get('success'):
                                # Add to history
                                from datetime import datetime
                                st.session_state.upload_history.append({
                                    'filename': uploaded_file.name,
                                    'sku_id': result['sku_id'],
                                    'product_name': result['product_name'],
                                    'category': result['category'],
                                    'status': '✅ Success',
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                
                                st.session_state.last_extraction = result
                                
                                # Display success message
                                st.markdown(
                                    f"""
                                    <div class="success-box">
                                    ✅ RFP processed and SKU created successfully!
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                                # Display result
                                result_col1, result_col2 = st.columns(2)
                                
                                with result_col1:
                                    st.markdown("### 📦 Created SKU")
                                    st.write(f"**SKU ID:** `{result['sku_id']}`")
                                    st.write(f"**Product:** {result['product_name']}")
                                    st.write(f"**Category:** {result['category']}")
                                
                                with result_col2:
                                    st.markdown("### 📊 Extracted Data")
                                    st.write(f"**Features:** {result['features_count']}")
                                    st.write(f"**Pricing Entries:** {result['pricing_count']}")

                                if result.get("rfp_id"):
                                    st.markdown("### 🗂️ Stored RFP")
                                    st.write(f"**RFP ID:** {result['rfp_id']}")

                                if result.get("workflow_error"):
                                    st.warning(f"Workflow error: {result['workflow_error']}")
                                elif result.get("workflow_result"):
                                    wf = result["workflow_result"]
                                    st.markdown("### 🧠 AI Workflow Output")
                                    st.markdown(f"**RFP Summary:** {wf.get('rfp_summary', '')}")
                                    st.markdown("**Narrative Summary:**")
                                    st.write(wf.get("narrative_summary", ""))
                    
                    except Exception as e:
                        st.markdown(
                            f"""
                            <div class="error-box">
                            ❌ Error: {str(e)}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        logger.error(f"Error processing RFP: {str(e)}")
            
            with col_reset:
                if st.button("🔄 Reset", use_container_width=True):
                    st.rerun()
    
    with tab2:
        st.markdown("### 📜 Upload History")
        
        if st.session_state.upload_history:
            # Display as table
            history_data = []
            for item in st.session_state.upload_history:
                history_data.append({
                    'Filename': item['filename'],
                    'SKU ID': item['sku_id'],
                    'Product': item['product_name'],
                    'Category': item['category'],
                    'Status': item['status'],
                    'Time': item.get('timestamp', 'N/A')
                })
            
            st.dataframe(
                history_data,
                use_container_width=True,
                hide_index=True
            )
            
            # Download history as JSON
            if st.button("📥 Download History"):
                json_str = json.dumps(st.session_state.upload_history, indent=2)
                st.download_button(
                    label="Download as JSON",
                    data=json_str,
                    file_name="rfp_upload_history.json",
                    mime="application/json"
                )
        else:
            st.info("No upload history yet. Upload an RFP PDF to get started!")
    
    with tab3:
        st.markdown("### ℹ️ Help & Documentation")
        
        st.markdown("""
        #### 📄 What is an RFP?
        An RFP (Request for Proposal) is a procurement document that outlines the requirements 
        for a product or service that an organization wants to purchase.
        
        #### 🚀 How to use this tool:
        1. **Upload PDF**: Select an RFP PDF file from your computer
        2. **Preview (Optional)**: Check "Preview Only" to see extracted data without saving
        3. **Process**: Click "Process RFP" to extract data and create a SKU
        4. **Review**: Check the generated SKU ID and extracted product information
        
        #### 🤖 AI Extraction Features:
        - **Automatic Text Extraction**: Extracts text from PDF documents
        - **Smart Parsing**: Uses AI to identify product information from RFP text
        - **Feature Extraction**: Automatically identifies product features and specifications
        - **SKU Generation**: Creates structured SKU data ready for database insertion
        
        #### 📊 Extracted Data:
        The system extracts the following information:
        - **Product Name**: Name of the product/service
        - **Category**: Product category classification
        - **Description**: Detailed product description
        - **Features**: Technical specifications and features
        - **Pricing**: Any pricing information from the RFP
        - **Additional Requirements**: Special requirements or conditions
        
        #### 💾 Database Integration:
        Extracted SKU data is automatically saved to the database with:
        - Unique SKU IDs for inventory management
        - Feature/specification details
        - Pricing information
        - Raw RFP data for reference
        
        #### ⚠️ Requirements:
        - PDF file must be readable and contain extractable text
        - File size should be less than 25 MB
        - RFP should contain product/service information
        
        #### 🔧 Troubleshooting:
        - **"File must be a PDF"**: Ensure you're uploading a .pdf file
        - **"Cannot connect to API"**: Check if the backend API is running
        - **"Request timeout"**: Large PDF files may take longer - try a smaller file
        - **"Extraction failed"**: RFP may not contain sufficient product information
        """)
    
    # Display upload history in sidebar
    display_upload_history()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #888; padding: 1rem;">
        RFP Automation Platform | Powered by AI
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
