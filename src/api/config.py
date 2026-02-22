"""Application configuration and utilities."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "false").lower() == "true"

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./rfp_platform.db"
)

# Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-pro")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Data directories
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
INDEXES_DIR = Path(os.getenv("INDEXES_DIR", "./indexes"))

# API configuration
API_TITLE = "RFP Automation Platform API"
API_DESCRIPTION = "Automated Request for Proposal Processing with AI-Driven Agents"
API_VERSION = "1.0.0"
