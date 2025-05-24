"""
---------------------------------------------------------------
File name:                  security.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                安全中间件，处理安全头和基础安全检查
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理安全头设置
        
        Args:
            request: HTTP请求
            call_next: 下一个中间件或处理器
            
        Returns:
            Response: HTTP响应
        """
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 对于WebSocket请求，不添加任何可能阻止连接的安全头
        if request.url.path.startswith("/api/v1/ws") or "upgrade" in request.headers.get("connection", "").lower():
            # WebSocket连接，不添加限制性头部
            pass
        else:
            # 普通HTTP请求才添加其他安全头
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # 添加允许WebSocket连接的CSP策略
            response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' ws: wss:; script-src 'self' 'unsafe-inline'"
        
        # 移除敏感信息
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response 