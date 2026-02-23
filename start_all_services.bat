@echo off
REM RFP Platform - Complete Startup Script (Windows)
REM This script starts all services locally

setlocal enabledelayedexpansion

echo.
echo ===================================================================
echo   RFP Automation Platform - Complete Startup
echo ===================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    exit /b 1
)

echo Checking dependencies...

REM Install dependencies if needed
pip show streamlit >nul 2>&1 || (
    echo Installing streamlit...
    pip install streamlit
)

pip show fastapi >nul 2>&1 || (
    echo Installing fastapi...
    pip install fastapi
)

pip show uvicorn >nul 2>&1 || (
    echo Installing uvicorn...
    pip install uvicorn
)

pip show google-genai >nul 2>&1 || (
    echo Installing google-genai...
    pip install google-genai
)

pip show pdfplumber >nul 2>&1 || (
    echo Installing pdfplumber...
    pip install pdfplumber
)

echo Dependencies ready
echo.

REM Create logs directory
if not exist "logs" mkdir logs

echo Starting RFP Platform services...
echo.

REM Start FastAPI Backend
echo Starting FastAPI Backend (port 8000)...
start "RFP API" cmd /k python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
timeout /t 3 /nobreak

REM Start Main Streamlit App
echo Starting Main Streamlit App (port 8501)...
start "RFP Main App" cmd /k streamlit run web/app.py --server.port=8501 --server.address=0.0.0.0
timeout /t 2 /nobreak

REM Start RFP Upload App
echo Starting RFP Upload App (port 8502)...
start "RFP Upload App" cmd /k streamlit run web/rfp_upload_app.py --server.port=8502 --server.address=0.0.0.0

echo.
echo ===================================================================
echo   Services Started Successfully!
echo ===================================================================
echo.
echo   API Backend:        http://localhost:8000
echo   API Docs:           http://localhost:8000/docs
echo   Main App:           http://localhost:8501
echo   RFP Upload:         http://localhost:8502
echo.
echo   Note: Each service is running in a separate window
echo         Close the windows to stop the services
echo.
echo ===================================================================
echo.

pause
