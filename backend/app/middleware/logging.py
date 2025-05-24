"""
---------------------------------------------------------------
File name:                  logging.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                日志中间件，记录请求和响应信息
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求日志记录
        
        Args:
            request: HTTP请求
            call_next: 下一个中间件或处理器
            
        Returns:
            Response: HTTP响应
        """
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"请求开始 - ID: {request_id}, "
            f"方法: {request.method}, "
            f"路径: {request.url.path}, "
            f"客户端: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            # 执行请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"请求完成 - ID: {request_id}, "
                f"状态码: {response.status_code}, "
                f"处理时间: {process_time:.3f}s"
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"请求异常 - ID: {request_id}, "
                f"错误: {str(e)}, "
                f"处理时间: {process_time:.3f}s",
                exc_info=True
            )
            raise 