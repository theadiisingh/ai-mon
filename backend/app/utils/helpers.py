"""
Helper utilities for the application.
"""
from typing import Any, Dict, Optional
import json
from datetime import datetime, timedelta
from enum import Enum


class DateTimeUtils:
    """Date and time utility functions."""
    
    @staticmethod
    def now() -> datetime:
        """Get current UTC datetime."""
        return datetime.utcnow()
    
    @staticmethod
    def format_iso(dt: datetime) -> str:
        """Format datetime to ISO format."""
        return dt.isoformat() if dt else None
    
    @staticmethod
    def parse_iso(date_string: str) -> Optional[datetime]:
        """Parse ISO format date string."""
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def get_time_ago(dt: datetime) -> str:
        """Get human-readable time ago string."""
        if not dt:
            return "Unknown"
        
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}s ago"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() / 60)}m ago"
        elif diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() / 3600)}h ago"
        else:
            return f"{int(diff.total_seconds() / 86400)}d ago"


class JsonUtils:
    """JSON utility functions."""
    
    @staticmethod
    def safe_dumps(obj: Any, default: Any = None) -> Optional[str]:
        """Safely serialize object to JSON string."""
        try:
            return json.dumps(obj, default=default)
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def safe_loads(json_string: str, default: Any = None) -> Any:
        """Safely deserialize JSON string."""
        try:
            return json.loads(json_string)
        except (TypeError, ValueError, json.JSONDecodeError):
            return default
    
    @staticmethod
    def truncate(text: str, max_length: int = 1000) -> str:
        """Truncate text to max length."""
        if not text:
            return ""
        return text[:max_length] + "..." if len(text) > max_length else text


class ResponseTimeUtils:
    """Response time utility functions."""
    
    @staticmethod
    def format_ms(milliseconds: float) -> str:
        """Format milliseconds to human-readable string."""
        if milliseconds is None:
            return "N/A"
        
        if milliseconds < 1:
            return f"{milliseconds * 1000:.2f}µs"
        elif milliseconds < 1000:
            return f"{milliseconds:.2f}ms"
        else:
            return f"{milliseconds / 1000:.2f}s"
    
    @staticmethod
    def get_status_color(response_time: float, thresholds: Dict[str, int] = None) -> str:
        """Get status color based on response time."""
        if thresholds is None:
            thresholds = {
                "green": 200,    # < 200ms
                "yellow": 500,   # < 500ms
                "orange": 1000,  # < 1000ms
                "red": float("inf")
            }
        
        if response_time < thresholds["green"]:
            return "green"
        elif response_time < thresholds["yellow"]:
            return "yellow"
        elif response_time < thresholds["orange"]:
            return "orange"
        else:
            return "red"


class EnumUtils:
    """Enum utility functions."""
    
    @staticmethod
    def get_enum_values(enum_class: Enum) -> list:
        """Get all values from an enum class."""
        return [e.value for e in enum_class]
    
    @staticmethod
    def get_enum_names(enum_class: Enum) -> list:
        """Get all names from an enum class."""
        return [e.name for e in enum_class]


class PaginationUtils:
    """Pagination utility functions."""
    
    @staticmethod
    def get_pagination_meta(
        total: int,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """Get pagination metadata."""
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }


class URLUtils:
    """URL utility functions."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if a string is a valid URL."""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return result.netloc
        except Exception:
            return None


def generate_random_string(length: int = 32) -> str:
    """Generate a random string."""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
