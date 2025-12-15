"""Streamlit web application for RFP Automation Platform."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import logging
from datetime import datetime
import pandas as pd

from src.agents.graph import run_sales_scan, run_full_workflow_for_rfp
from src.data_ingestion.build_indexes import build_all_indexes
from src.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Page configuration
st.set_page_config(
    page_title="RFP Automation Platform",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
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
        st.success("✅ All agents ready")
        
        st.markdown("---")
        
        st.subheader("Developer Tools")
        
        if st.button("🔧 Build Indexes", use_container_width=True):
            with st.spinner("Building vector indexes..."):
                try:
                    success = build_all_indexes(force_rebuild=True)
                    if success:
                        st.success("Indexes built successfully!")
                    else:
                        st.error("Failed to build indexes")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        
        st.subheader("About")
        st.info("""
        **Agentic AI RFP Automation**
        
        Powered by:
        - LangGraph for orchestration
        - LlamaIndex for retrieval
        - Google Gemini for intelligence
        """)


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
                    rfps = run_sales_scan()
                    st.session_state.rfps = rfps
                    st.success(f"Found {len(rfps)} relevant RFPs!")
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
                "RFP ID": rfp.rfp_id,
                "Title": rfp.title,
                "Deadline": rfp.submission_deadline.strftime("%Y-%m-%d"),
                "Summary": rfp.brief_summary[:100] + "..." if len(rfp.brief_summary) > 100 else rfp.brief_summary
            })
        
        df = pd.DataFrame(rfp_data)
        
        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Selection
        st.markdown("---")
        selected_id = st.selectbox(
            "Select RFP to process:",
            options=[rfp.rfp_id for rfp in st.session_state.rfps],
            format_func=lambda x: f"{x} - {next(r.title for r in st.session_state.rfps if r.rfp_id == x)}"
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
        (r for r in st.session_state.rfps if r.rfp_id == st.session_state.selected_rfp_id),
        None
    )
    
    if selected_rfp:
        st.markdown(f"**Selected RFP:** {selected_rfp.title}")
        st.markdown(f"**Deadline:** {selected_rfp.submission_deadline.strftime('%Y-%m-%d %H:%M')}")
    
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
                
                # Run workflow
                final_response = run_full_workflow_for_rfp(st.session_state.selected_rfp_id)
                st.session_state.final_response = final_response
                
                progress_bar.progress(100)
                status_text.text("✅ Workflow completed successfully!")
                
                st.success("AI workflow completed! View results below.")
                
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
        st.write(response.rfp_summary)
        
        st.markdown("---")
        st.subheader("AI-Generated Response")
        st.write(response.narrative_summary)
    
    with tab2:
        st.subheader("Technical Recommendations")
        
        # Product table
        product_df = pd.DataFrame(response.final_product_table)
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
        pricing_df = pd.DataFrame(response.pricing_table)
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
            total_row = response.pricing_table[-1]
            
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
            json_str = json.dumps(response.model_dump(), indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"rfp_response_{response.rfp_id}.json",
                mime="application/json"
            )


def main():
    """Main application."""
    init_session_state()
    
    # Sidebar
    sidebar()
    
    # Main content
    st.title("🤖 Agentic AI RFP Automation Platform")
    st.markdown("Automated RFP processing with Sales, Technical, and Pricing AI agents")
    
    st.markdown("---")
    
    # Sections
    rfp_discovery_section()
    
    st.markdown("---")
    
    agent_workflow_section()
    
    st.markdown("---")
    
    results_section()


if __name__ == "__main__":
    main()
