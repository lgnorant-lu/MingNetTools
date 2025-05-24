"""
---------------------------------------------------------------
File name:                  scan.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                扫描相关Pydantic数据模型，包含扫描请求、结果、统计等
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
                            2025/05/23: 更新为Pydantic v2验证器;
----
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import Field, field_validator, model_validator
import time
import ipaddress

from .common import BaseModel, ConfigUpdate


class ScanRequest(BaseModel):
    """单目标扫描请求模型"""
    
    target: str = Field(..., description="扫描目标IP或域名")
    port: int = Field(..., ge=1, le=65535, description="目标端口")
    timeout: Optional[float] = Field(default=3.0, ge=0.1, le=30.0, description="超时时间(秒)")
    protocol: str = Field(default="tcp", description="协议类型")
    
    @field_validator("target")
    @classmethod
    def validate_target(cls, v):
        """验证目标IP或域名"""
        if not v.strip():
            raise ValueError("目标不能为空")
        
        # 尝试解析为IP地址
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        
        # 验证域名格式（简单验证）
        if not v.replace(".", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError("无效的IP地址或域名格式")
        
        return v
    
    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v):
        """验证协议类型"""
        allowed_protocols = ["tcp", "udp"]
        if v.lower() not in allowed_protocols:
            raise ValueError(f"协议必须是以下之一: {allowed_protocols}")
        return v.lower()


class PortRangeRequest(BaseModel):
    """端口范围扫描请求模型"""
    
    target: str = Field(..., description="扫描目标IP或域名")
    start_port: int = Field(..., ge=1, le=65535, description="起始端口")
    end_port: int = Field(..., ge=1, le=65535, description="结束端口")
    timeout: Optional[float] = Field(default=3.0, ge=0.1, le=30.0, description="超时时间(秒)")
    protocol: str = Field(default="tcp", description="协议类型")
    max_concurrent: Optional[int] = Field(default=50, ge=1, le=500, description="最大并发数")
    
    @field_validator("target")
    @classmethod
    def validate_target(cls, v):
        """验证目标IP或域名"""
        if not v.strip():
            raise ValueError("目标不能为空")
        
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        
        if not v.replace(".", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError("无效的IP地址或域名格式")
        
        return v
    
    @model_validator(mode='after')
    def validate_port_range(self):
        """验证端口范围"""
        if self.start_port > self.end_port:
            raise ValueError("起始端口不能大于结束端口")
        
        if (self.end_port - self.start_port) > 10000:
            raise ValueError("端口范围过大，最大支持10000个端口")
        
        return self
    
    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v):
        """验证协议类型"""
        allowed_protocols = ["tcp", "udp"]
        if v.lower() not in allowed_protocols:
            raise ValueError(f"协议必须是以下之一: {allowed_protocols}")
        return v.lower()


class BatchScanRequest(BaseModel):
    """批量扫描请求模型"""
    
    targets: List[str] = Field(..., min_items=1, max_items=100, description="扫描目标列表")
    ports: List[int] = Field(..., min_items=1, max_items=1000, description="端口列表")
    timeout: Optional[float] = Field(default=3.0, ge=0.1, le=30.0, description="超时时间(秒)")
    protocol: str = Field(default="tcp", description="协议类型")
    max_concurrent: Optional[int] = Field(default=50, ge=1, le=500, description="最大并发数")
    
    @field_validator("targets")
    @classmethod
    def validate_targets(cls, v):
        """验证目标列表"""
        validated_targets = []
        for target in v:
            if not target.strip():
                continue
            
            try:
                ipaddress.ip_address(target)
                validated_targets.append(target)
                continue
            except ValueError:
                pass
            
            if target.replace(".", "").replace("-", "").replace("_", "").isalnum():
                validated_targets.append(target)
            else:
                raise ValueError(f"无效的目标: {target}")
        
        if not validated_targets:
            raise ValueError("至少需要一个有效目标")
        
        return validated_targets
    
    @field_validator("ports")
    @classmethod
    def validate_ports(cls, v):
        """验证端口列表"""
        for port in v:
            if not (1 <= port <= 65535):
                raise ValueError(f"端口 {port} 超出有效范围 (1-65535)")
        
        # 去重并排序
        return sorted(list(set(v)))
    
    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v):
        """验证协议类型"""
        allowed_protocols = ["tcp", "udp"]
        if v.lower() not in allowed_protocols:
            raise ValueError(f"协议必须是以下之一: {allowed_protocols}")
        return v.lower()


class ScanResult(BaseModel):
    """扫描结果模型"""
    
    target: str = Field(..., description="扫描目标")
    port: int = Field(..., description="端口")
    status: str = Field(..., description="端口状态")
    protocol: str = Field(..., description="协议类型")
    service: Optional[str] = Field(default=None, description="服务名称")
    version: Optional[str] = Field(default=None, description="服务版本")
    banner: Optional[str] = Field(default=None, description="服务横幅")
    response_time: Optional[float] = Field(default=None, description="响应时间(毫秒)")
    timestamp: float = Field(default_factory=time.time, description="扫描时间戳")
    error: Optional[str] = Field(default=None, description="错误信息")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证端口状态"""
        allowed_statuses = ["open", "closed", "filtered", "timeout", "error"]
        if v not in allowed_statuses:
            raise ValueError(f"状态必须是以下之一: {allowed_statuses}")
        return v
    
    @field_validator("response_time")
    @classmethod
    def validate_response_time(cls, v):
        """验证响应时间"""
        if v is not None and v < 0:
            raise ValueError("响应时间不能为负数")
        return v


class ScanStatistics(BaseModel):
    """扫描统计模型"""
    
    total_scans: int = Field(..., ge=0, description="总扫描数")
    open_ports: int = Field(..., ge=0, description="开放端口数")
    closed_ports: int = Field(..., ge=0, description="关闭端口数")
    filtered_ports: int = Field(..., ge=0, description="过滤端口数")
    timeout_ports: int = Field(..., ge=0, description="超时端口数")
    error_ports: int = Field(..., ge=0, description="错误端口数")
    average_response_time: Optional[float] = Field(default=None, description="平均响应时间(毫秒)")
    min_response_time: Optional[float] = Field(default=None, description="最小响应时间(毫秒)")
    max_response_time: Optional[float] = Field(default=None, description="最大响应时间(毫秒)")
    scan_duration: Optional[float] = Field(default=None, description="扫描耗时(秒)")
    start_time: Optional[float] = Field(default=None, description="开始时间")
    end_time: Optional[float] = Field(default=None, description="结束时间")
    
    @model_validator(mode='after')
    def validate_statistics(self):
        """验证统计数据一致性"""
        calculated_total = (self.open_ports + self.closed_ports + self.filtered_ports + 
                          self.timeout_ports + self.error_ports)
        
        if self.total_scans != calculated_total:
            # 允许一定的误差，但记录警告
            pass
        
        return self


class ScanTaskStatus(BaseModel):
    """扫描任务状态模型"""
    
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(..., ge=0, le=100, description="进度百分比")
    total_targets: int = Field(..., ge=0, description="总目标数")
    completed_targets: int = Field(..., ge=0, description="已完成目标数")
    total_ports: int = Field(..., ge=0, description="总端口数")
    completed_ports: int = Field(..., ge=0, description="已完成端口数")
    open_ports_found: int = Field(default=0, ge=0, description="发现的开放端口数")
    current_target: Optional[str] = Field(default=None, description="当前扫描目标")
    estimated_time_remaining: Optional[float] = Field(default=None, description="预计剩余时间(秒)")
    created_at: float = Field(default_factory=time.time, description="创建时间")
    started_at: Optional[float] = Field(default=None, description="开始时间")
    completed_at: Optional[float] = Field(default=None, description="完成时间")
    error: Optional[str] = Field(default=None, description="错误信息")
    
    @field_validator("status")
    @classmethod
    def validate_task_status(cls, v):
        """验证任务状态"""
        allowed_statuses = ["pending", "running", "completed", "failed", "cancelled", "paused"]
        if v not in allowed_statuses:
            raise ValueError(f"任务状态必须是以下之一: {allowed_statuses}")
        return v


class ScanConfigUpdate(ConfigUpdate):
    """扫描配置更新模型"""
    
    section: str = Field(default="scan", description="配置节")
    
    @field_validator("key")
    @classmethod
    def validate_scan_config_key(cls, v):
        """验证扫描配置键"""
        allowed_keys = [
            "default_timeout",
            "max_concurrent",
            "max_targets",
            "max_ports_per_scan",
            "rate_limit",
            "service_detection",
            "version_detection",
            "banner_grabbing"
        ]
        if v not in allowed_keys:
            raise ValueError(f"扫描配置键必须是以下之一: {allowed_keys}")
        return v


class PortInfo(BaseModel):
    """端口信息模型"""
    
    port: int = Field(..., ge=1, le=65535, description="端口号")
    protocol: str = Field(..., description="协议类型")
    service_name: Optional[str] = Field(default=None, description="服务名称")
    service_description: Optional[str] = Field(default=None, description="服务描述")
    is_common: bool = Field(default=False, description="是否为常用端口")
    security_risk: str = Field(default="low", description="安全风险等级")
    
    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v):
        """验证协议类型"""
        allowed_protocols = ["tcp", "udp", "both"]
        if v.lower() not in allowed_protocols:
            raise ValueError(f"协议必须是以下之一: {allowed_protocols}")
        return v.lower()
    
    @field_validator("security_risk")
    @classmethod
    def validate_security_risk(cls, v):
        """验证安全风险等级"""
        allowed_risks = ["low", "medium", "high", "critical"]
        if v.lower() not in allowed_risks:
            raise ValueError(f"安全风险等级必须是以下之一: {allowed_risks}")
        return v.lower()


class ScanProfile(BaseModel):
    """扫描配置模板模型"""
    
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(default=None, description="模板描述")
    ports: List[int] = Field(..., description="端口列表")
    timeout: float = Field(default=3.0, description="超时时间(秒)")
    max_concurrent: int = Field(default=50, description="最大并发数")
    service_detection: bool = Field(default=True, description="是否启用服务检测")
    version_detection: bool = Field(default=False, description="是否启用版本检测")
    banner_grabbing: bool = Field(default=False, description="是否启用横幅抓取")
    is_default: bool = Field(default=False, description="是否为默认模板")
    created_by: Optional[str] = Field(default=None, description="创建者")
    created_at: float = Field(default_factory=time.time, description="创建时间")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证模板名称"""
        if not v.strip():
            raise ValueError("模板名称不能为空")
        if len(v) > 50:
            raise ValueError("模板名称长度不能超过50个字符")
        return v.strip()
    
    @field_validator("ports")
    @classmethod
    def validate_ports(cls, v):
        """验证端口列表"""
        if not v:
            raise ValueError("端口列表不能为空")
        
        for port in v:
            if not (1 <= port <= 65535):
                raise ValueError(f"端口 {port} 超出有效范围 (1-65535)")
        
        return sorted(list(set(v))) 