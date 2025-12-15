"""Web scraping service for fetching RFP pages."""

import logging
from typing import Optional, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config import settings

logger = logging.getLogger(__name__)


class ScrapingService:
    """Service for fetching web pages."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """Initialize scraping service.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.timeout = timeout
        self.session = self._create_session(max_retries)
    
    def _create_session(self, max_retries: int) -> requests.Session:
        """Create requests session with retry logic.
        
        Args:
            max_retries: Maximum retries
            
        Returns:
            Configured session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Add proxy if configured
        if settings.proxy_url:
            session.proxies = {
                "http": settings.proxy_url,
                "https": settings.proxy_url
            }
        
        return session
    
    def fetch_url(self, url: str) -> Optional[Dict[str, str]]:
        """Fetch content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with 'url', 'content', 'status_code' or None on error
        """
        try:
            logger.info(f"Fetching URL: {url}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            return {
                "url": url,
                "content": response.text,
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type", "")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def fetch_multiple(self, urls: list[str]) -> list[Dict[str, str]]:
        """Fetch multiple URLs.
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            List of successful fetch results
        """
        results = []
        for url in urls:
            result = self.fetch_url(url)
            if result:
                results.append(result)
        return results


# Global service instance
_scraping_service: Optional[ScrapingService] = None


def get_scraping_service() -> ScrapingService:
    """Get global scraping service instance."""
    global _scraping_service
    if _scraping_service is None:
        _scraping_service = ScrapingService()
    return _scraping_service
