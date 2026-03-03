"""
CSP (Content Security Policy) Middleware for FastAPI.

This middleware adds CSP headers to responses with environment-aware configuration:
- Development: Allows 'unsafe-eval' and localhost origins for React dev server
- Production: Strict CSP without eval

Usage:
    from app.middleware.csp import CSPMiddleware
    app.add_middleware(CSPMiddleware)
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.config import settings


class CSPMiddleware(BaseHTTPMiddleware):
    """
    Content Security Policy middleware with environment-aware configuration.
    
    In development mode:
        - Allows 'unsafe-eval' for React hot reload and source maps
        - Allows localhost:3000 and localhost:5173 for React dev server
        
    In production mode:
        - Strict CSP without eval
        - No inline scripts (requires nonce/hash)
    """
    
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.is_dev = settings.is_development
    
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        
        # Skip CSP for API routes - APIs should not have CSP headers
        # as they may be consumed by other services
        if request.url.path.startswith("/api"):
            # Add security headers but skip CSP for API routes
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            return response
        
        # Get the appropriate CSP header based on environment
        csp_header = self._get_csp_header()
        
        # Add CSP header to response
        response.headers["Content-Security-Policy"] = csp_header
        
        # Add additional security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict-Transport-Security (HSTS) - only in production
        if not self.is_dev:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    def _get_csp_header(self) -> str:
        """
        Generate CSP header based on environment.
        
        Development CSP:
            - 'unsafe-eval' for React hot reload and source maps
            - 'unsafe-inline' for hot module replacement
            - localhost:3000 and localhost:5173 for dev servers
            - ws://localhost:* for WebSocket hot reload
            
        Production CSP:
            - No eval
            - No inline scripts (requires nonce or hash)
            - Self-only origins
        """
        if self.is_dev:
            # Development CSP - relaxed for React dev server
            return (
                "default-src 'self' "
                "script-src 'self' 'unsafe-eval' 'unsafe-inline' http://localhost:3000 http://localhost:5173 https://localhost:3000 https://localhost:5173 "
                "style-src 'self' 'unsafe-inline' http://localhost:3000 http://localhost:5173 "
                "img-src 'self' data: blob: http://localhost:3000 http://localhost:5173 "
                "font-src 'self' data: http://localhost:3000 http://localhost:5173 "
                "connect-src 'self' http://localhost:3000 http://localhost:5173 http://localhost:8000 ws://localhost:* wss://localhost:* "
                "frame-src 'self' "
                "worker-src 'self' blob: "
                "upgrade-insecure-requests"
            )
        else:
            # Production CSP - strict security
            return (
                "default-src 'self' "
                "script-src 'self' "
                "style-src 'self' 'unsafe-inline' "
                "img-src 'self' data: blob: "
                "font-src 'self' data: "
                "connect-src 'self' "
                "frame-src 'self' "
                "worker-src 'self' blob: "
                "upgrade-insecure-requests"
            )


def get_csp_header_value(is_development: bool = None) -> str:
    """
    Standalone function to get CSP header value.
    
    Args:
        is_development: Override environment detection
        
    Returns:
        CSP header value string
    """
    if is_development is None:
        is_development = settings.is_development
    
    if is_development:
        return (
            "default-src 'self' "
            "script-src 'self' 'unsafe-eval' 'unsafe-inline' http://localhost:3000 http://localhost:5173 https://localhost:3000 https://localhost:5173 "
            "style-src 'self' 'unsafe-inline' http://localhost:3000 http://localhost:5173 "
            "img-src 'self' data: blob: http://localhost:3000 http://localhost:5173 "
            "font-src 'self' data: http://localhost:3000 http://localhost:5173 "
            "connect-src 'self' http://localhost:3000 http://localhost:5173 http://localhost:8000 ws://localhost:* wss://localhost:* "
            "frame-src 'self' "
            "worker-src 'self' blob: "
            "upgrade-insecure-requests"
        )
    else:
        return (
            "default-src 'self' "
            "script-src 'self' "
            "style-src 'self' 'unsafe-inline' "
            "img-src 'self' data: blob: "
            "font-src 'self' data: "
            "connect-src 'self' "
            "frame-src 'self' "
            "worker-src 'self' blob: "
            "upgrade-insecure-requests"
        )

