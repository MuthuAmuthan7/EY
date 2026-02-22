"""Utility functions and helpers for the API."""

from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T', bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    items: List[T]
    total: int
    skip: int
    limit: int
    
    @property
    def has_next(self) -> bool:
        """Check if there are more items."""
        return self.skip + self.limit < self.total
    
    @property
    def has_prev(self) -> bool:
        """Check if there are previous items."""
        return self.skip > 0


def paginate_results(items: List[T], total: int, skip: int, limit: int) -> PaginatedResponse[T]:
    """Create a paginated response."""
    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO format string."""
    return dt.isoformat() if dt else None


def get_offset_from_page(page: int, limit: int) -> int:
    """Calculate offset from page number."""
    if page < 1:
        page = 1
    return (page - 1) * limit
