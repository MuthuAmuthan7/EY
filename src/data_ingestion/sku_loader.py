"""SKU loader for product specifications."""

import logging
import csv
from pathlib import Path
from typing import List, Dict, Any

from ..models.sku_models import SKU, SKUFeature, SKURepository
from ..config import settings

logger = logging.getLogger(__name__)


class SKULoader:
    """Loader for SKU product specifications."""
    
    def __init__(self, specs_dir: Path | None = None):
        """Initialize SKU loader.
        
        Args:
            specs_dir: Directory containing product spec files
        """
        self.specs_dir = specs_dir or settings.get_product_specs_dir()
    
    def load_from_csv(self, filename: str = "product_specs.csv") -> SKURepository:
        """Load SKUs from CSV file.
        
        Args:
            filename: CSV filename
            
        Returns:
            SKU repository
        """
        filepath = self.specs_dir / filename
        repository = SKURepository()
        
        if not filepath.exists():
            logger.warning(f"SKU file not found: {filepath}")
            return repository
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sku = self._parse_row(row)
                    if sku:
                        repository.add_sku(sku)
            
            logger.info(f"Loaded {len(repository)} SKUs from {filepath}")
            return repository
            
        except Exception as e:
            logger.error(f"Error loading SKUs from {filepath}: {e}")
            return repository
    
    def _parse_row(self, row: Dict[str, str]) -> SKU | None:
        """Parse CSV row into SKU object.
        
        Args:
            row: CSV row dictionary
            
        Returns:
            SKU object or None
        """
        try:
            # Required fields
            sku_id = row.get('sku_id', '').strip()
            product_name = row.get('product_name', '').strip()
            category = row.get('category', '').strip()
            
            if not sku_id or not product_name:
                return None
            
            # Parse features from remaining columns
            features = []
            feature_columns = [
                'conductor_material', 'conductor_size', 'conductor_size_unit',
                'insulation_type', 'voltage_grade', 'voltage_unit',
                'cores', 'armour_type', 'standard'
            ]
            
            for col in feature_columns:
                value = row.get(col, '').strip()
                if value and value.lower() not in ['', 'n/a', 'na', 'none']:
                    # Extract unit if present in column name
                    unit = None
                    if '_unit' in col:
                        continue  # Skip unit columns, they're handled separately
                    
                    unit_col = f"{col}_unit"
                    if unit_col in row:
                        unit = row[unit_col].strip() or None
                    
                    feature = SKUFeature(
                        name=col.replace('_', ' ').title(),
                        value=value,
                        unit=unit
                    )
                    features.append(feature)
            
            return SKU(
                sku_id=sku_id,
                product_name=product_name,
                category=category,
                features=features,
                raw_record=dict(row)
            )
            
        except Exception as e:
            logger.warning(f"Error parsing SKU row: {e}")
            return None


def load_skus(filename: str = "product_specs.csv") -> SKURepository:
    """Convenience function to load SKUs.
    
    Args:
        filename: CSV filename
        
    Returns:
        SKU repository
    """
    loader = SKULoader()
    return loader.load_from_csv(filename)
