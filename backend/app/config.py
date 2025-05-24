"""
---------------------------------------------------------------
File name:                  config.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                应用配置管理系统，包含环境变量处理和各种配置设置
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

import os
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置设置类
    
    使用Pydantic BaseSettings自动处理环境变量
    """
    
    # 应用基本信息
    app_name: str = Field(default="网络安全工具平台", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    app_description: str = Field(
        default="基于FastAPI的网络安全工具平台，提供端口扫描、PING监控和TCP通信功能",
        description="应用描述"
    )
    
    # 运行环境配置
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=True, description="调试模式")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    reload: bool = Field(default=True, description="自动重载")
    
    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./network_security.db",
        description="数据库连接URL"
    )
    database_echo: bool = Field(default=False, description="数据库SQL日志")
    
    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    redis_host: str = Field(default="localhost", description="Redis主机")
    redis_port: int = Field(default=6379, description="Redis端口")
    redis_db: int = Field(default=0, description="Redis数据库")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")
    
    # 安全配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="应用密钥"
    )
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    
    # CORS配置
    cors_origins: List[str] = Field(
        default=["*"], 
        description="允许的CORS源"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="允许的HTTP方法"
    )
    cors_headers: List[str] = Field(
        default=["*"],
        description="允许的请求头"
    )
    
    # 网络工具配置
    default_scan_timeout: float = Field(default=3.0, description="默认扫描超时(秒)")
    max_scan_concurrent: int = Field(default=500, description="最大扫描并发数")
    default_ping_timeout: float = Field(default=5.0, description="默认PING超时(秒)")
    default_ping_count: int = Field(default=4, description="默认PING次数")
    max_tcp_connections: int = Field(default=1000, description="最大TCP连接数")
    
    # API限制配置
    rate_limit_requests: int = Field(default=100, description="速率限制请求数")
    rate_limit_window: int = Field(default=60, description="速率限制时间窗口(秒)")
    max_request_size: int = Field(default=1024*1024, description="最大请求大小(字节)")
    
    # 任务配置
    task_timeout: int = Field(default=300, description="任务超时时间(秒)")
    max_task_queue_size: int = Field(default=1000, description="最大任务队列大小")
    task_cleanup_interval: int = Field(default=3600, description="任务清理间隔(秒)")
    
    # WebSocket配置
    websocket_timeout: int = Field(default=60, description="WebSocket超时(秒)")
    websocket_heartbeat_interval: int = Field(default=30, description="WebSocket心跳间隔(秒)")
    max_websocket_connections: int = Field(default=100, description="最大WebSocket连接数")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """验证运行环境"""
        allowed_envs = ["development", "testing", "production"]
        if v not in allowed_envs:
            raise ValueError(f"环境必须是以下之一: {allowed_envs}")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """验证日志级别"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"日志级别必须是以下之一: {allowed_levels}")
        return v.upper()
    
    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v):
        """验证CORS源配置"""
        if not v:
            return ["*"]  # 如果为空，允许所有源
        return v
    
    def get_database_settings(self) -> Dict[str, Any]:
        """获取数据库配置字典
        
        Returns:
            Dict[str, Any]: 数据库配置
        """
        return {
            "url": self.database_url,
            "echo": self.database_echo,
        }
    
    def get_redis_settings(self) -> Dict[str, Any]:
        """获取Redis配置字典
        
        Returns:
            Dict[str, Any]: Redis配置
        """
        return {
            "host": self.redis_host,
            "port": self.redis_port,
            "db": self.redis_db,
            "password": self.redis_password,
            "decode_responses": True,
        }
    
    def get_cors_settings(self) -> Dict[str, Any]:
        """获取CORS配置字典
        
        Returns:
            Dict[str, Any]: CORS配置
        """
        return {
            "allow_origins": self.cors_origins,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers,
            "allow_credentials": True,
        }
    
    def get_network_tool_settings(self) -> Dict[str, Any]:
        """获取网络工具配置字典
        
        Returns:
            Dict[str, Any]: 网络工具配置
        """
        return {
            "scan_timeout": self.default_scan_timeout,
            "max_scan_concurrent": self.max_scan_concurrent,
            "ping_timeout": self.default_ping_timeout,
            "ping_count": self.default_ping_count,
            "max_tcp_connections": self.max_tcp_connections,
        }
    
    def is_development(self) -> bool:
        """检查是否为开发环境
        
        Returns:
            bool: 是否为开发环境
        """
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """检查是否为生产环境
        
        Returns:
            bool: 是否为生产环境
        """
        return self.environment == "production"
    
    def is_testing(self) -> bool:
        """检查是否为测试环境
        
        Returns:
            bool: 是否为测试环境
        """
        return self.environment == "testing"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DevelopmentSettings(Settings):
    """开发环境配置"""
    environment: str = "development"
    debug: bool = True
    reload: bool = False  # 禁用自动重载，防止WebSocket连接断开
    log_level: str = "DEBUG"
    database_echo: bool = True


class ProductionSettings(Settings):
    """生产环境配置"""
    environment: str = "production"
    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"
    database_echo: bool = False
    
    # 生产环境安全配置
    secret_key: str = Field(..., description="生产环境必须设置密钥")
    cors_origins: List[str] = Field(default=[], description="生产环境限制CORS源")


class TestingSettings(Settings):
    """测试环境配置"""
    environment: str = "testing"
    debug: bool = True
    database_url: str = "sqlite:///:memory:"
    redis_db: int = 15  # 使用不同的Redis数据库
    log_level: str = "WARNING"


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置实例
    
    使用lru_cache确保配置单例，提高性能
    
    Returns:
        Settings: 配置实例
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# 全局配置实例
settings = get_settings()


def reload_settings():
    """重新加载配置"""
    global settings
    get_settings.cache_clear()
    settings = get_settings()


def get_app_info() -> Dict[str, str]:
    """获取应用信息
    
    Returns:
        Dict[str, str]: 包含应用名称、版本、描述的字典
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "environment": settings.environment,
    } 