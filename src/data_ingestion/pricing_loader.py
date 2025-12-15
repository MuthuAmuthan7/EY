"""Pricing loader for pricing tables."""

import logging
import csv
from pathlib import Path
from typing import List

from ..models.pricing_models import PricingLine, TestPricingLine, PricingTables
from ..config import settings

logger = logging.getLogger(__name__)


class PricingLoader:
    """Loader for pricing tables."""
    
    def __init__(self, pricing_dir: Path | None = None):
        """Initialize pricing loader.
        
        Args:
            pricing_dir: Directory containing pricing files
        """
        self.pricing_dir = pricing_dir or settings.get_pricing_dir()
    
    def load_pricing_tables(
        self,
        product_file: str = "product_pricing.csv",
        test_file: str = "test_pricing.csv"
    ) -> PricingTables:
        """Load all pricing tables.
        
        Args:
            product_file: Product pricing CSV filename
            test_file: Test pricing CSV filename
            
        Returns:
            Pricing tables object
        """
        product_pricing = self.load_product_pricing(product_file)
        test_pricing = self.load_test_pricing(test_file)
        
        return PricingTables(
            product_pricing=product_pricing,
            test_pricing=test_pricing
        )
    
    def load_product_pricing(self, filename: str = "product_pricing.csv") -> List[PricingLine]:
        """Load product pricing from CSV.
        
        Args:
            filename: CSV filename
            
        Returns:
            List of pricing lines
        """
        filepath = self.pricing_dir / filename
        pricing_lines = []
        
        if not filepath.exists():
            logger.warning(f"Product pricing file not found: {filepath}")
            return pricing_lines
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    line = PricingLine(
                        sku_id=row['sku_id'].strip(),
                        unit_price=float(row['unit_price']),
                        currency=row.get('currency', 'INR').strip()
                    )
                    pricing_lines.append(line)
            
            logger.info(f"Loaded {len(pricing_lines)} product pricing lines from {filepath}")
            return pricing_lines
            
        except Exception as e:
            logger.error(f"Error loading product pricing from {filepath}: {e}")
            return pricing_lines
    
    def load_test_pricing(self, filename: str = "test_pricing.csv") -> List[TestPricingLine]:
        """Load test pricing from CSV.
        
        Args:
            filename: CSV filename
            
        Returns:
            List of test pricing lines
        """
        filepath = self.pricing_dir / filename
        test_lines = []
        
        if not filepath.exists():
            logger.warning(f"Test pricing file not found: {filepath}")
            return test_lines
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    line = TestPricingLine(
                        test_name=row['test_name'].strip(),
                        price=float(row['price']),
                        currency=row.get('currency', 'INR').strip()
                    )
                    test_lines.append(line)
            
            logger.info(f"Loaded {len(test_lines)} test pricing lines from {filepath}")
            return test_lines
            
        except Exception as e:
            logger.error(f"Error loading test pricing from {filepath}: {e}")
            return test_lines


def load_pricing_tables() -> PricingTables:
    """Convenience function to load all pricing tables.
    
    Returns:
        Pricing tables
    """
    loader = PricingLoader()
    return loader.load_pricing_tables()
