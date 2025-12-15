"""Configuration management for RFP Agentic Platform."""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    google_api_key: str = Field(..., description="Google API key for Gemini")
    llm_model: str = Field(default="gemini-1.5-pro", description="LLM model to use")
    
    # Directory Paths
    data_dir: Path = Field(default=Path("./data"), description="Data directory path")
    indexes_dir: Path = Field(default=Path("./indexes"), description="Vector indexes directory")
    
    # RFP Source URLs
    rfp_urls: List[str] = Field(
        default_factory=lambda: [
            "https://example.com/rfp1",
            "https://example.com/rfp2"
        ],
        description="List of URLs to scan for RFPs"
    )
    
    # Vector Database
    vector_db_type: str = Field(default="chroma", description="Vector database type")
    vector_db_path: Path = Field(default=Path("./indexes"), description="Vector DB storage path")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Optional Proxy
    proxy_url: str | None = Field(default=None, description="HTTP proxy URL")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True
    )
    
    @field_validator("data_dir", "indexes_dir", "vector_db_path")
    @classmethod
    def resolve_paths(cls, v: Path) -> Path:
        """Resolve paths to absolute paths."""
        if not v.is_absolute():
            # Get project root (parent of src directory)
            project_root = Path(__file__).parent.parent
            v = (project_root / v).resolve()
        return v
    
    @field_validator("rfp_urls", mode="before")
    @classmethod
    def parse_urls(cls, v):
        """Parse comma-separated URLs from environment variable."""
        if isinstance(v, str):
            return [url.strip() for url in v.split(",") if url.strip()]
        return v
    
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
    # Fallback: Create a settings class that doesn't load from .env
    print(f"⚠️  Warning: Could not load settings from .env: {e}")
    print("Using default settings. Please fix .env file or it will be recreated.")
    
    # Define a fallback settings class without env file loading
    class FallbackSettings(BaseSettings):
        """Fallback settings without .env file loading."""
        google_api_key: str = Field(default="dummy_key_for_init")
        llm_model: str = Field(default="gemini-1.5-pro")
        data_dir: Path = Field(default=Path("./data"))
        indexes_dir: Path = Field(default=Path("./indexes"))
        rfp_urls: List[str] = Field(default_factory=lambda: ["https://example.com/rfp1"])
        vector_db_type: str = Field(default="chroma")
        vector_db_path: Path = Field(default=Path("./indexes"))
        log_level: str = Field(default="INFO")
        proxy_url: str | None = Field(default=None)
        
        model_config = SettingsConfigDict(
            case_sensitive=False,
            extra="ignore"
        )
        
        @field_validator("data_dir", "indexes_dir", "vector_db_path")
        @classmethod
        def resolve_paths(cls, v: Path) -> Path:
            if not v.is_absolute():
                project_root = Path(__file__).parent.parent
                v = (project_root / v).resolve()
            return v
        
        def get_rfp_parsed_dir(self) -> Path:
            return self.data_dir / "rfps_parsed"
        
        def get_product_specs_dir(self) -> Path:
            return self.data_dir / "product_specs"
        
        def get_pricing_dir(self) -> Path:
            return self.data_dir / "pricing"
        
        def get_sku_index_dir(self) -> Path:
            return self.indexes_dir / "sku_index"
        
        def get_rfp_index_dir(self) -> Path:
            return self.indexes_dir / "rfp_index"
    
    settings = FallbackSettings()
