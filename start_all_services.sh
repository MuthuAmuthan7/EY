#!/bin/bash

# RFP Platform - Complete Startup Script
# This script starts all services locally

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  RFP Automation Platform - Complete Startup                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed"
    exit 1
fi

echo "📦 Checking dependencies..."
pip list | grep -q streamlit || { echo "Installing streamlit..."; pip install streamlit; }
pip list | grep -q fastapi || { echo "Installing fastapi..."; pip install fastapi; }
pip list | grep -q uvicorn || { echo "Installing uvicorn..."; pip install uvicorn; }
pip list | grep -q google-genai || { echo "Installing google-genai..."; pip install google-genai; }
pip list | grep -q pdfplumber || { echo "Installing pdfplumber..."; pip install pdfplumber; }

echo "✅ Dependencies ready"
echo ""

# Create logs directory
mkdir -p logs

echo "🚀 Starting RFP Platform services..."
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start FastAPI Backend
echo "📡 Starting FastAPI Backend (port 8000)..."
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
API_PID=$!
echo "   ✓ Backend started (PID: $API_PID)"

# Wait for API to be ready
sleep 3

# Start Main Streamlit App
echo "🌐 Starting Main Streamlit App (port 8501)..."
streamlit run web/app.py --server.port=8501 --server.address=0.0.0.0 > logs/web.log 2>&1 &
WEB_PID=$!
echo "   ✓ Main app started (PID: $WEB_PID)"

# Start RFP Upload App
echo "📄 Starting RFP Upload App (port 8502)..."
streamlit run web/rfp_upload_app.py --server.port=8502 --server.address=0.0.0.0 > logs/rfp_upload.log 2>&1 &
RFP_PID=$!
echo "   ✓ RFP upload app started (PID: $RFP_PID)"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Services Started Successfully!                                ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  API Backend:        http://localhost:8000                    ║"
echo "║  API Docs:           http://localhost:8000/docs               ║"
echo "║  Main App:           http://localhost:8501                    ║"
echo "║  RFP Upload:         http://localhost:8502                    ║"
echo "║                                                                ║"
echo "║  Logs:                                                         ║"
echo "║    - API:            logs/api.log                             ║"
echo "║    - Main:           logs/web.log                             ║"
echo "║    - RFP Upload:     logs/rfp_upload.log                      ║"
echo "║                                                                ║"
echo "║  Press Ctrl+C to stop all services                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Keep script running
wait
