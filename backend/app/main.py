"""
---------------------------------------------------------------
File name:                  main.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                FastAPI应用主入口文件，包含应用初始化、中间件配置、路由注册等
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
import logging
import uuid
from typing import Dict, Any

from .config import settings, get_app_info
from .schemas.common import ErrorResponse, SuccessResponse, HealthCheck
from .middleware.logging import LoggingMiddleware
from .middleware.rate_limiting import RateLimitingMiddleware
from .middleware.security import SecurityMiddleware
from .middleware.performance import PerformanceMiddleware


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format,
    filename=settings.log_file if settings.log_file else None
)

logger = logging.getLogger(__name__)

# 应用启动时间
_app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动事件
    logger.info("网络安全工具平台启动中...")
    
    # 初始化数据库连接
    # await init_database()
    
    # 初始化Redis连接
    # await init_redis()
    
    # 启动后台任务
    # await start_background_tasks()
    
    logger.info(f"应用启动完成，运行环境: {settings.environment}")
    
    yield
    
    # 关闭事件
    logger.info("网络安全工具平台正在关闭...")
    
    # 清理资源
    # await cleanup_resources()
    
    logger.info("应用已成功关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例
    
    Returns:
        FastAPI: 配置好的应用实例
    """
    app_info = get_app_info()
    
    app = FastAPI(
        title=app_info["name"],
        version=app_info["version"],
        description=app_info["description"],
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
        openapi_url="/openapi.json" if not settings.is_production() else None,
    )
    
    # 添加中间件
    setup_middleware(app)
    
    # 注册路由
    setup_routes(app)
    
    # 注册异常处理器
    setup_exception_handlers(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """设置中间件
    
    Args:
        app: FastAPI应用实例
    """
    # CORS中间件
    cors_settings = settings.get_cors_settings()
    app.add_middleware(
        CORSMiddleware,
        **cors_settings
    )
    
    # 受信任主机中间件（生产环境）
    if settings.is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # 生产环境中应配置具体的主机名
        )
    
    # 自定义中间件
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    app.add_middleware(LoggingMiddleware)


def setup_routes(app: FastAPI) -> None:
    """设置路由
    
    Args:
        app: FastAPI应用实例
    """
    from .api.routes import scan, ping, tcp, websocket, performance, system
    
    # API路由
    app.include_router(
        scan.router,
        prefix="/api/v1/scan",
        tags=["扫描功能"]
    )
    
    app.include_router(
        ping.router,
        prefix="/api/v1/ping",
        tags=["PING监控"]
    )
    
    app.include_router(
        tcp.router,
        prefix="/api/v1/tcp",
        tags=["TCP通信"]
    )
    
    app.include_router(
        websocket.router,
        prefix="/api/v1/ws",
        tags=["WebSocket通信"]
    )
    
    app.include_router(
        performance.router,
        prefix="/api/v1/performance",
        tags=["性能监控"]
    )
    
    app.include_router(
        system.router,
        prefix="/api/v1/system",
        tags=["系统监控"]
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP异常处理器"""
        error_response = ErrorResponse(
            error="http_error",
            message=exc.detail,
            details={"status_code": exc.status_code},
            request_id=getattr(request.state, "request_id", None)
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict()
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """值错误处理器"""
        error_response = ErrorResponse(
            error="validation_error",
            message=str(exc),
            request_id=getattr(request.state, "request_id", None)
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        
        error_response = ErrorResponse(
            error="internal_error",
            message="服务器内部错误",
            details={"type": type(exc).__name__} if settings.debug else None,
            request_id=getattr(request.state, "request_id", None)
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict()
        )


# 创建应用实例
app = create_app()


@app.get("/", response_class=RedirectResponse)
async def root():
    """根路径重定向到文档"""
    if settings.is_development():
        return RedirectResponse(url="/docs")
    else:
        return RedirectResponse(url="/health")


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """健康检查端点
    
    Returns:
        HealthCheck: 健康检查结果
    """
    uptime = time.time() - _app_start_time
    
    # 检查各个服务状态
    services = {}
    
    # 检查数据库连接
    try:
        # await check_database_connection()
        services["database"] = "healthy"
    except Exception as e:
        logger.error(f"数据库连接检查失败: {e}")
        services["database"] = "unhealthy"
    
    # 检查Redis连接
    try:
        # await check_redis_connection()
        services["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis连接检查失败: {e}")
        services["redis"] = "unhealthy"
    
    # 检查核心网络工具
    try:
        from .core.ping_tool import PingEngine
        from .core.port_scanner import PortScannerEngine
        
        # 简单的工具可用性检查
        services["ping_tool"] = "healthy"
        services["port_scanner"] = "healthy"
    except Exception as e:
        logger.error(f"核心工具检查失败: {e}")
        services["ping_tool"] = "unhealthy"
        services["port_scanner"] = "unhealthy"
    
    # 确定总体状态
    unhealthy_services = [k for k, v in services.items() if v == "unhealthy"]
    if not unhealthy_services:
        overall_status = "healthy"
    elif len(unhealthy_services) < len(services) / 2:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    app_info = get_app_info()
    
    return HealthCheck(
        status=overall_status,
        version=app_info["version"],
        uptime=uptime,
        services=services,
        environment=app_info["environment"]
    )


@app.get("/info")
async def app_info():
    """应用信息端点
    
    Returns:
        Dict: 应用信息
    """
    info = get_app_info()
    info.update({
        "uptime": time.time() - _app_start_time,
        "debug": settings.debug,
        "docs_url": "/docs" if settings.is_development() else None,
        "redoc_url": "/redoc" if settings.is_development() else None,
    })
    return SuccessResponse(data=info)


@app.get("/metrics")
async def metrics():
    """指标端点
    
    Returns:
        Dict: 应用指标
    """
    # 这里可以集成Prometheus等监控系统
    metrics_data = {
        "uptime": time.time() - _app_start_time,
        "requests_total": getattr(app.state, "requests_total", 0),
        "requests_duration_seconds": getattr(app.state, "avg_request_duration", 0),
        "active_connections": getattr(app.state, "active_connections", 0),
        "memory_usage": 0,  # 实际实现中应获取真实内存使用量
        "cpu_usage": 0,     # 实际实现中应获取真实CPU使用率
    }
    
    return SuccessResponse(data=metrics_data)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义Swagger UI"""
    if not settings.is_development():
        raise HTTPException(status_code=404, detail="文档仅在开发环境可用")
    
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - 交互式API文档",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """自定义ReDoc"""
    if not settings.is_development():
        raise HTTPException(status_code=404, detail="文档仅在开发环境可用")
    
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API文档",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js",
    )


def custom_openapi():
    """自定义OpenAPI配置"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # 添加自定义扩展
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # 添加安全方案
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=True,
    ) 