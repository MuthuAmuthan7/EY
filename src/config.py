"""Configuration management for RFP Agentic Platform."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


# Default RFP URLs
DEFAULT_RFP_URLS = ["https://example.com/rfp1", "https://example.com/rfp2"]


def parse_rfp_urls(urls_str: Optional[str]) -> List[str]:
    """Parse RFP URLs from environment variable or return defaults."""
    if not urls_str:
        return DEFAULT_RFP_URLS
    try:
        urls = [url.strip() for url in urls_str.split(",") if url.strip()]
        return urls if urls else DEFAULT_RFP_URLS
    except Exception:
        return DEFAULT_RFP_URLS


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    google_api_key: str = Field(default="dummy_key", description="Google API key for Gemini")
    llm_model: str = Field(default="gemini-1.5-pro", description="LLM model to use")
    
    # Directory Paths
    data_dir: Path = Field(default=Path("./data"), description="Data directory path")
    indexes_dir: Path = Field(default=Path("./indexes"), description="Vector indexes directory")
    
    # RFP Source URLs - simple string field, parsed separately
    rfp_urls_str: Optional[str] = Field(default=None, description="Comma-separated RFP URLs")
    
    # Vector Database
    vector_db_type: str = Field(default="qdrant", description="Vector database type")
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant server URL")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API key")
    vector_db_path: Path = Field(default=Path("./indexes"), description="Vector DB storage path")
    
    # Embedding Model
    embedding_model: str = Field(default="cohere", description="Embedding model provider")
    cohere_api_key: str = Field(default="dummy_key", description="Cohere API key")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Optional Proxy
    proxy_url: Optional[str] = Field(default=None, description="HTTP proxy URL")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True
    )
    
    @field_validator("data_dir", "indexes_dir", "vector_db_path", mode="before")
    @classmethod
    def resolve_paths(cls, v):
        """Resolve paths to absolute paths."""
        if isinstance(v, str):
            v = Path(v)
        if not v.is_absolute():
            # Get project root (parent of src directory)
            project_root = Path(__file__).parent.parent
            v = (project_root / v).resolve()
        return v
    
    @property
    def rfp_urls(self) -> List[str]:
        """Get parsed RFP URLs."""
        return parse_rfp_urls(self.rfp_urls_str)
    
    def get_rfp_raw_dir(self) -> Path:
        """Get raw RFP documents directory."""
        return self.data_dir / "rfps_raw"
    
    def get_rfp_parsed_dir(self) -> Path:
        """Get parsed RFP documents directory."""
        return self.data_dir / "rfps_parsed"
    
    def get_product_specs_dir(self) -> Path:
        """Get product specs directory."""
        return self.data_dir / "product_specs"
    
    def get_pricing_dir(self) -> Path:
        """Get pricing tables directory."""
        return self.data_dir / "pricing"
    
    def get_tests_dir(self) -> Path:
        """Get tests directory."""
        return self.data_dir / "tests"
    
    def get_sku_index_dir(self) -> Path:
        """Get SKU vector index directory."""
        return self.indexes_dir / "sku_index"
    
    def get_rfp_index_dir(self) -> Path:
        """Get RFP vector index directory."""
        return self.indexes_dir / "rfp_index"


# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"⚠️  Warning: Could not load settings from .env: {e}")
    print("Using fallback settings...")
    # Create a minimal fallback
    settings = Settings(
        google_api_key="dummy_key",
        llm_model="gemini-1.5-pro",
        data_dir=Path("./data"),
        indexes_dir=Path("./indexes"),
        rfp_urls_str=None,
        vector_db_type="qdrant",
        qdrant_url="http://localhost:6333",
        qdrant_api_key=None,
        vector_db_path=Path("./indexes"),
        embedding_model="cohere",
        cohere_api_key="dummy_key",
        log_level="INFO"
    )
