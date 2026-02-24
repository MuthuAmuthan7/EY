"""Streamlit web application for RFP Automation Platform."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import logging
from datetime import datetime
import pandas as pd
import requests
from src.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# API Configuration
# Use 'api' service name when running in Docker, 'localhost' for local development
import os
API_HOST = os.getenv("API_HOST", "localhost")
API_BASE_URL = f"http://{API_HOST}:8000/api/v1"
WORKFLOW_API = f"{API_BASE_URL}/workflow"


# Page configuration
st.set_page_config(
    page_title="RFP Automation Platform",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern UI styling - Minimal & Clean
st.markdown(
    """
    <style>
    /* Base styles */
    .main { padding: 2rem; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    
    /* Hero section - Clean and minimal */
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
    
    /* Badge/pill styling */
    .pill {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(59, 130, 246, 0.3);
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
    
    /* Metric boxes */
    [data-testid="metric-container"] {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
    }
    
    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0;
    }
    
    /* Expanders */
    [data-baseweb="accordion"] {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def init_session_state():
    """Initialize session state variables."""
    if 'rfps' not in st.session_state:
        st.session_state.rfps = []
    if 'selected_rfp_id' not in st.session_state:
        st.session_state.selected_rfp_id = None
    if 'final_response' not in st.session_state:
        st.session_state.final_response = None
    if 'workflow_running' not in st.session_state:
        st.session_state.workflow_running = False


def sidebar():
    """Render sidebar."""
    with st.sidebar:
        st.title("🤖 RFP AI Platform")
        st.markdown("---")
        
        st.subheader("System Status")
        
        # Check Qdrant connection
        try:
            from qdrant_client import QdrantClient
            qdrant_client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                prefer_grpc=False
            )
            collections = qdrant_client.get_collections()
            st.success(f"✅ Qdrant connected ({len(collections.collections)} collections)")
        except Exception as e:
            st.error(f"❌ Qdrant: {str(e)[:50]}")
        
        # Check Cohere API
        try:
            import cohere
            cohere_client = cohere.ClientV2(api_key=settings.cohere_api_key)
            st.success("✅ Cohere API ready")
        except Exception as e:
            st.error(f"❌ Cohere: {str(e)[:50]}")
        
        st.markdown("---")

        st.header("Created By ")
        st.subheader("Team Soul To Syntax")
        # st.info("""
        # **Agentic AI RFP Automation**
        
        # Powered by:
        # - LangGraph for orchestration
        # - LlamaIndex for retrieval
        # - Google Gemini for intelligence
        # """)


def rfp_discovery_section():
    """Render RFP discovery section."""
    st.header("📋 RFP Discovery")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("Scan configured URLs for new RFPs due in the next 3 months")
    
    with col2:
        if st.button("🔍 Scan RFPs", use_container_width=True, type="primary"):
            with st.spinner("Scanning for RFPs..."):
                try:
                    response = requests.get(f"{WORKFLOW_API}/scan-rfps")
                    response.raise_for_status()
                    rfps = response.json()
                    st.session_state.rfps = rfps
                    st.success(f"Found {len(rfps)} relevant RFPs!")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
                    logger.error("API connection error")
                except Exception as e:
                    st.error(f"Error scanning RFPs: {e}")
                    logger.error(f"Scan error: {e}", exc_info=True)
    
    if st.session_state.rfps:
        st.markdown("---")
        st.subheader("Available RFPs")
        
        # Create DataFrame for display
        rfp_data = []
        for rfp in st.session_state.rfps:
            rfp_data.append({
                "RFP ID": rfp['rfp_id'],
                "Title": rfp['title'],
                "Deadline": datetime.fromisoformat(rfp['submission_deadline']).strftime("%Y-%m-%d"),
                "Summary": rfp['brief_summary'][:100] + "..." if len(rfp['brief_summary']) > 100 else rfp['brief_summary']
            })
        
        df = pd.DataFrame(rfp_data)
        
        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Selection
        st.markdown("---")
        selected_id = st.selectbox(
            "Select RFP to process:",
            options=[rfp['rfp_id'] for rfp in st.session_state.rfps],
            format_func=lambda x: f"{x} - {next(r['title'] for r in st.session_state.rfps if r['rfp_id'] == x)}"
        )
        
        if selected_id:
            st.session_state.selected_rfp_id = selected_id


def agent_workflow_section():
    """Render agent workflow section."""
    if not st.session_state.selected_rfp_id:
        st.info("👆 Please select an RFP from the discovery section above")
        return
    
    st.header("🤖 AI Agent Workflow")
    
    selected_rfp = next(
        (r for r in st.session_state.rfps if r['rfp_id'] == st.session_state.selected_rfp_id),
        None
    )
    
    if selected_rfp:
        st.markdown(f"**Selected RFP:** {selected_rfp['title']}")
        st.markdown(f"**Deadline:** {datetime.fromisoformat(selected_rfp['submission_deadline']).strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    
    if st.button("▶️ Run AI Workflow", use_container_width=True, type="primary"):
        st.session_state.workflow_running = True
        
        with st.spinner("Running AI workflow..."):
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("🔍 Sales Agent: Loading RFP...")
                progress_bar.progress(20)
                
                status_text.text("🔧 Technical Agent: Matching specifications...")
                progress_bar.progress(40)
                
                status_text.text("💰 Pricing Agent: Calculating costs...")
                progress_bar.progress(60)
                
                status_text.text("📝 Master Agent: Generating final response...")
                progress_bar.progress(80)
                
                # Run workflow via API
                api_url = f"{WORKFLOW_API}/process-rfp/{st.session_state.selected_rfp_id}"
                response = requests.post(api_url)
                response.raise_for_status()
                final_response = response.json()
                st.session_state.final_response = final_response
                
                progress_bar.progress(100)
                status_text.text("✅ Workflow completed successfully!")
                
                st.success("AI workflow completed! View results below.")
                
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
                logger.error("API connection error during workflow")
            except requests.exceptions.HTTPError as e:
                st.error(f"Error running workflow: {e.response.json().get('detail', str(e))}")
                logger.error(f"Workflow HTTP error: {e}", exc_info=True)
            except Exception as e:
                st.error(f"Error running workflow: {e}")
                logger.error(f"Workflow error: {e}", exc_info=True)
            finally:
                st.session_state.workflow_running = False


def results_section():
    """Render results section."""
    if not st.session_state.final_response:
        return
    
    st.header("📊 Results")
    
    response = st.session_state.final_response
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📝 Summary", "🔧 Technical Match", "💰 Pricing"])
    
    with tab1:
        st.subheader("RFP Summary")
        st.write(response['rfp_summary'])
        
        st.markdown("---")
        st.subheader("AI-Generated Response")
        st.write(response['narrative_summary'])
    
    with tab2:
        st.subheader("Technical Recommendations")
        
        # Product table
        product_df = pd.DataFrame(response['final_product_table'])
        if not product_df.empty:
            st.dataframe(product_df, use_container_width=True, hide_index=True)
            
            # Highlight best matches
            st.markdown("---")
            st.subheader("Match Quality")
            avg_match = product_df['spec_match_percent'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Match", f"{avg_match:.1f}%")
            with col2:
                st.metric("Best Match", f"{product_df['spec_match_percent'].max():.1f}%")
            with col3:
                st.metric("Items Matched", len(product_df))
    
    with tab3:
        st.subheader("Pricing Breakdown")
        
        # Pricing table
        pricing_df = pd.DataFrame(response['pricing_table'])
        if not pricing_df.empty:
            # Format currency columns
            currency_cols = ['unit_price', 'material_cost', 'test_cost', 'total_cost']
            for col in currency_cols:
                if col in pricing_df.columns:
                    pricing_df[col] = pricing_df[col].apply(lambda x: f"₹{x:,.2f}")
            
            st.dataframe(pricing_df, use_container_width=True, hide_index=True)
            
            # Summary metrics
            st.markdown("---")
            st.subheader("Cost Summary")
            
            # Get totals from last row
            total_row = response['pricing_table'][-1]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Material Cost", f"₹{total_row['material_cost']:,.2f}")
            with col2:
                st.metric("Testing Cost", f"₹{total_row['test_cost']:,.2f}")
            with col3:
                st.metric("Grand Total", f"₹{total_row['total_cost']:,.2f}", 
                         delta=None, delta_color="normal")
    
    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download as JSON", use_container_width=True):
            import json
            json_str = json.dumps(response, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"rfp_response_{response['rfp_id']}.json",
                mime="application/json"
            )


def sku_database_section():
    """Render SKU database section showing uploaded SKUs."""
    st.header("📦 SKU Database")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("View all SKUs created from uploaded RFP documents")
    
    with col2:
        refresh = st.button("🔄 Refresh SKUs", use_container_width=True, type="primary")
    
    # Fetch SKUs from API
    if refresh or 'skus_loaded' not in st.session_state:
        try:
            response = requests.get(f"{API_BASE_URL}/skus?limit=100")
            response.raise_for_status()
            data = response.json()
            st.session_state.sku_list = data.get("items", [])
            st.session_state.sku_total = data.get("total", 0)
            st.session_state.skus_loaded = True
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the FastAPI server is running.")
            return
        except Exception as e:
            st.error(f"Error fetching SKUs: {e}")
            return
    
    sku_list = st.session_state.get("sku_list", [])
    sku_total = st.session_state.get("sku_total", 0)
    
    if not sku_list:
        st.info("No SKUs found. Upload an RFP document on the Upload page (port 8502) to create SKUs.")
        return
    
    st.success(f"Found **{sku_total}** SKU(s) in the database")
    
    for sku in sku_list:
        with st.expander(f"📦 {sku.get('product_name', 'Unknown')} — `{sku.get('sku_id', '')}`"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Category:** {sku.get('category', 'N/A')}")
                st.markdown(f"**SKU ID:** `{sku.get('sku_id', 'N/A')}`")
                if sku.get('description'):
                    st.markdown(f"**Description:** {sku['description'][:300]}")
            
            with col2:
                features = sku.get('features', [])
                pricing = sku.get('pricing', [])
                st.markdown(f"**Features:** {len(features)}")
                st.markdown(f"**Pricing Entries:** {len(pricing)}")
                if sku.get('created_at'):
                    st.markdown(f"**Created:** {sku['created_at'][:19]}")
            
            # Show features table
            if features:
                st.markdown("**Features:**")
                feat_data = [{"Name": f.get("name", ""), "Value": f.get("value", ""), "Unit": f.get("unit", "-")} for f in features]
                st.dataframe(pd.DataFrame(feat_data), use_container_width=True, hide_index=True)
            
            # Show pricing table
            if pricing:
                st.markdown("**Pricing:**")
                price_data = [{"Unit Price": f"₹{p.get('unit_price', 0):,.2f}", "Currency": p.get("currency", "INR")} for p in pricing]
                st.dataframe(pd.DataFrame(price_data), use_container_width=True, hide_index=True)


def main():
    """Main application."""
    init_session_state()
    
    # Sidebar
    sidebar()
    
    # Main content
    st.markdown(
        """
        <div class="hero">
            <div class="pill">AI Powered</div>
            <div class="pill">RFP Automation</div>
            <h1>🤖 Agentic AI RFP Automation Platform</h1>
            <p>Modern, interactive workflow for RFP discovery, matching, and pricing.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("<div class='card'>📡 <b>Discover</b><br/>Scan RFP sources with deadline filters.</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<div class='card'>🧠 <b>Analyze</b><br/>Spec match using vector search.</div>", unsafe_allow_html=True)
    with col_c:
        st.markdown("<div class='card'>💰 <b>Price</b><br/>Automated cost breakdowns and totals.</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SKU Database section
    sku_database_section()
    
    st.markdown("---")
    
    # Sections
    rfp_discovery_section()
    
    st.markdown("---")
    
    agent_workflow_section()
    
    st.markdown("---")
    
    results_section()


if __name__ == "__main__":
    main()
