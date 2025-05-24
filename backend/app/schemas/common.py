"""
---------------------------------------------------------------
File name:                  common.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                通用Pydantic数据模型，包含错误响应、分页、健康检查等
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
                            2025/05/23: 更新为Pydantic v2验证器;
----
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel, Field, field_validator, computed_field
import time
import math


class BaseModel(PydanticBaseModel):
    """基础模型类
    
    为所有模型提供通用配置和方法
    """
    
    class Config:
        # 启用JSON模式
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        
        # 允许字段别名
        populate_by_name = True
        
        # 验证赋值
        validate_assignment = True
        
        # 使用枚举值
        use_enum_values = True


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    timestamp: float = Field(default_factory=time.time, description="错误时间戳")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    
    @field_validator("error")
    @classmethod
    def validate_error(cls, v):
        """验证错误类型"""
        if not v.strip():
            raise ValueError("错误类型不能为空")
        return v.strip()


class SuccessResponse(BaseModel):
    """成功响应模型"""
    
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")
    timestamp: float = Field(default_factory=time.time, description="响应时间戳")
    request_id: Optional[str] = Field(default=None, description="请求ID")


class Pagination(BaseModel):
    """分页模型"""
    
    page: int = Field(..., ge=1, description="当前页码")
    size: int = Field(..., ge=1, le=100, description="每页大小")
    total: int = Field(..., ge=0, description="总记录数")
    
    @computed_field
    @property
    def total_pages(self) -> int:
        """计算总页数"""
        return math.ceil(self.total / self.size) if self.size > 0 else 0
    
    @computed_field
    @property
    def has_next(self) -> bool:
        """计算是否有下一页"""
        return self.page < self.total_pages
    
    @computed_field
    @property
    def has_previous(self) -> bool:
        """计算是否有上一页"""
        return self.page > 1


class HealthCheck(BaseModel):
    """健康检查模型"""
    
    status: str = Field(..., description="系统状态")
    version: str = Field(..., description="应用版本")
    uptime: float = Field(..., description="运行时间(秒)")
    services: Dict[str, str] = Field(default_factory=dict, description="服务状态")
    environment: str = Field(..., description="运行环境")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证系统状态"""
        allowed_statuses = ["healthy", "degraded", "unhealthy"]
        if v not in allowed_statuses:
            raise ValueError(f"系统状态必须是以下之一: {allowed_statuses}")
        return v


class TaskStatus(BaseModel):
    """任务状态模型"""
    
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(default=0.0, ge=0, le=100, description="进度百分比")
    message: Optional[str] = Field(default=None, description="状态消息")
    result: Optional[Dict[str, Any]] = Field(default=None, description="任务结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    created_at: float = Field(default_factory=time.time, description="创建时间")
    started_at: Optional[float] = Field(default=None, description="开始时间")
    completed_at: Optional[float] = Field(default=None, description="完成时间")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证任务状态"""
        allowed_statuses = ["pending", "running", "completed", "failed", "cancelled"]
        if v not in allowed_statuses:
            raise ValueError(f"任务状态必须是以下之一: {allowed_statuses}")
        return v


class FileUpload(BaseModel):
    """文件上传模型"""
    
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    size: int = Field(..., ge=0, description="文件大小(字节)")
    checksum: Optional[str] = Field(default=None, description="文件校验和")
    upload_time: float = Field(default_factory=time.time, description="上传时间")


class APIKey(BaseModel):
    """API密钥模型"""
    
    key_id: str = Field(..., description="密钥ID")
    name: str = Field(..., description="密钥名称") 
    key_preview: str = Field(..., description="密钥预览")
    permissions: List[str] = Field(default_factory=list, description="权限列表")
    created_at: float = Field(default_factory=time.time, description="创建时间")
    expires_at: Optional[float] = Field(default=None, description="过期时间")
    last_used: Optional[float] = Field(default=None, description="最后使用时间")
    is_active: bool = Field(default=True, description="是否活跃")


class SystemInfo(BaseModel):
    """系统信息模型"""
    
    hostname: str = Field(..., description="主机名")
    platform: str = Field(..., description="平台")
    architecture: str = Field(..., description="架构")
    cpu_count: int = Field(..., description="CPU核心数")
    memory_total: int = Field(..., description="总内存(字节)")
    memory_available: int = Field(..., description="可用内存(字节)")
    disk_total: int = Field(..., description="总磁盘空间(字节)")
    disk_free: int = Field(..., description="可用磁盘空间(字节)")
    python_version: str = Field(..., description="Python版本")
    load_average: Optional[List[float]] = Field(default=None, description="负载平均值")


class LogEntry(BaseModel):
    """日志条目模型"""
    
    timestamp: float = Field(default_factory=time.time, description="时间戳")
    level: str = Field(..., description="日志级别")
    logger: str = Field(..., description="记录器名称")
    message: str = Field(..., description="日志消息")
    module: Optional[str] = Field(default=None, description="模块名")
    function: Optional[str] = Field(default=None, description="函数名")
    line_number: Optional[int] = Field(default=None, description="行号")
    extra: Optional[Dict[str, Any]] = Field(default=None, description="额外信息")


class MetricPoint(BaseModel):
    """指标数据点模型"""
    
    timestamp: float = Field(default_factory=time.time, description="时间戳")
    metric_name: str = Field(..., description="指标名称")
    value: Union[int, float] = Field(..., description="指标值")
    tags: Optional[Dict[str, str]] = Field(default=None, description="标签")
    unit: Optional[str] = Field(default=None, description="单位")


class ConfigUpdate(BaseModel):
    """配置更新模型"""
    
    section: str = Field(..., description="配置节")
    key: str = Field(..., description="配置键")
    value: Any = Field(..., description="配置值")
    previous_value: Optional[Any] = Field(default=None, description="之前的值")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    updated_at: float = Field(default_factory=time.time, description="更新时间")
    
    @field_validator("section")
    @classmethod
    def validate_section(cls, v):
        """验证配置节"""
        allowed_sections = [
            "scan", "ping", "tcp", "websocket", 
            "security", "logging", "database", "redis"
        ]
        if v not in allowed_sections:
            raise ValueError(f"配置节必须是以下之一: {allowed_sections}")
        return v 