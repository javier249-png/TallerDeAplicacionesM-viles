import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

# Limitador de peticiones para mitigar DDoS L7 y ataques de fuerza bruta / escaners
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Añade cabeceras de seguridad estrictas exigidas para el cumplimiento de 
    estándares de seguridad y protección de datos.
    """
    async def dispatch(self, request: Request, call_next):
        # Detección básica y bloqueo de peticiones automáticas sospechosas (Scanners/Bots)
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "zgrab"]
        if any(agent in user_agent for agent in suspicious_agents):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acceso denegado por políticas de seguridad interna."
            )

        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response