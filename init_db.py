"""Database initialization script."""

import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.db.database import init_db, Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with all tables."""
    logger.info("🔄 Initializing database...")
    try:
        init_db()
        logger.info("✅ Database initialized successfully!")
        logger.info(f"📊 Created tables: {', '.join(Base.metadata.tables.keys())}")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


if __name__ == "__main__":
    init_database()
