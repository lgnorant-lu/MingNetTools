"""
---------------------------------------------------------------
File name:                  performance.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                性能监控中间件，自动跟踪请求性能指标
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
                            2025/05/23: 集成真实性能监控器;
----
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.performance import performance_monitor

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件
    
    自动跟踪所有HTTP请求的性能指标，包括：
    - 响应时间
    - 请求成功/失败率
    - 并发请求数
    - 端点性能统计
    """
    
    def __init__(self, app, enable_detailed_logging: bool = False):
        """初始化性能监控中间件
        
        Args:
            app: ASGI应用
            enable_detailed_logging: 是否启用详细日志记录
        """
        super().__init__(app)
        self.enable_detailed_logging = enable_detailed_logging
        logger.info("性能监控中间件已初始化")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并监控性能
        
        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: HTTP响应
        """
        # 跳过静态文件和监控端点的性能监控
        if (request.url.path.startswith("/static/") or 
            request.url.path.startswith("/api/v1/performance/metrics")):
            return await call_next(request)
        
        # 使用性能监控器跟踪请求
        with performance_monitor.track_request(request.method, request.url.path) as request_info:
            try:
                # 处理请求
                response = await call_next(request)
                
                # 记录响应状态码
                request_info.status_code = response.status_code
                
                # 详细日志记录
                if self.enable_detailed_logging:
                    logger.info(
                        f"Request processed: {request.method} {request.url.path} "
                        f"[{response.status_code}] in {request_info.response_time:.3f}s"
                    )
                
                return response
                
            except Exception as e:
                # 记录错误
                request_info.status_code = 500
                request_info.error = str(e)
                
                if self.enable_detailed_logging:
                    logger.error(
                        f"Request failed: {request.method} {request.url.path} "
                        f"in {request_info.response_time:.3f}s - {str(e)}"
                    )
                
                # 重新抛出异常
                raise
    
    def get_request_id(self, request: Request) -> str:
        """获取或生成请求ID
        
        Args:
            request: HTTP请求
            
        Returns:
            str: 请求ID
        """
        # 尝试从header获取请求ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            # 生成新的请求ID
            request_id = f"{request.method}-{int(time.time() * 1000)}"
        
        return request_id 