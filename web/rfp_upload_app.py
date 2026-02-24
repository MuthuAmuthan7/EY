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

# Custom styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        padding: 10px 20px;
    }
    .upload-section {
        border: 2px dashed #4CAF50;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background-color: #f9f9f9;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
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
    st.title("📄 RFP Upload & SKU Extraction")
    st.markdown("""
    Upload RFP (Request for Proposal) PDF documents to automatically extract product information 
    and create SKU entries in the database using AI-powered parsing.
    """)
    
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
