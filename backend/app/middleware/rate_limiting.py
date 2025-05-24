"""
---------------------------------------------------------------
File name:                  rate_limiting.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                速率限制中间件
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

import time
from typing import Callable, Dict
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    
    def __init__(self, app, calls_per_minute: int = 100):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.clients: Dict[str, Dict] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理速率限制
        
        Args:
            request: HTTP请求
            call_next: 下一个中间件或处理器
            
        Returns:
            Response: HTTP响应
        """
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 简单的内存速率限制实现
        if client_ip not in self.clients:
            self.clients[client_ip] = {"calls": 1, "reset_time": current_time + 60}
        else:
            if current_time > self.clients[client_ip]["reset_time"]:
                self.clients[client_ip] = {"calls": 1, "reset_time": current_time + 60}
            else:
                self.clients[client_ip]["calls"] += 1
                
                if self.clients[client_ip]["calls"] > self.calls_per_minute:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="请求频率过高，请稍后再试"
                    )
        
        response = await call_next(request)
        return response 