"""PDF extraction service for parsing RFP PDFs."""

import logging
import json
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
import io

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from ..llm.client import LLMClient
from ..config import settings

logger = logging.getLogger(__name__)


class PDFParserService:
    """Service for parsing PDF documents and extracting text."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize PDF parser service.
        
        Args:
            llm_client: LLM client for AI-powered parsing
        """
        self.llm_client = llm_client or LLMClient()
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Validate that required PDF libraries are available."""
        if not PyPDF2 and not pdfplumber:
            raise ImportError(
                "At least one of PyPDF2 or pdfplumber is required. "
                "Install with: pip install PyPDF2 pdfplumber"
            )
        logger.info("PDF parser dependencies validated")
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """Extract text from PDF file.
        
        Args:
            pdf_file_path: Path to PDF file
            
        Returns:
            Extracted text from PDF
        """
        logger.info(f"Extracting text from PDF: {pdf_file_path}")
        
        try:
            # Try pdfplumber first (better for structured data)
            if pdfplumber:
                return self._extract_with_pdfplumber(pdf_file_path)
            # Fallback to PyPDF2
            elif PyPDF2:
                return self._extract_with_pypdf2(pdf_file_path)
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes.
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Extracted text from PDF
        """
        logger.info("Extracting text from PDF bytes")
        
        try:
            if pdfplumber:
                return self._extract_with_pdfplumber_bytes(pdf_bytes)
            elif PyPDF2:
                return self._extract_with_pypdf2_bytes(pdf_bytes)
        except Exception as e:
            logger.error(f"Error extracting PDF text from bytes: {e}")
            raise
    
    def _extract_with_pdfplumber(self, pdf_file_path: str) -> str:
        """Extract text using pdfplumber.
        
        Args:
            pdf_file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text_parts = []
        
        with pdfplumber.open(pdf_file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- PAGE {page_num} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
        
        return "\n\n".join(text_parts)
    
    def _extract_with_pdfplumber_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text using pdfplumber from bytes.
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Extracted text
        """
        text_parts = []
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- PAGE {page_num} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
        
        return "\n\n".join(text_parts)
    
    def _extract_with_pypdf2(self, pdf_file_path: str) -> str:
        """Extract text using PyPDF2.
        
        Args:
            pdf_file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text_parts = []
        
        with open(pdf_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- PAGE {page_num + 1} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
        
        return "\n\n".join(text_parts)
    
    def _extract_with_pypdf2_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text using PyPDF2 from bytes.
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Extracted text
        """
        text_parts = []
        
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(pdf_reader.pages)
        
        for page_num in range(num_pages):
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- PAGE {page_num + 1} ---\n{text}")
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
        
        return "\n\n".join(text_parts)
