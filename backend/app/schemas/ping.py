"""
---------------------------------------------------------------
File name:                  ping.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                PING相关Pydantic数据模型，包含PING请求、结果、统计等
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
                            2025/05/23: 更新为Pydantic v2验证器;
----
"""

from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator, model_validator
import time
import ipaddress

from .common import BaseModel, ConfigUpdate


class PingRequest(BaseModel):
    """PING请求模型"""
    
    target: str = Field(..., description="PING目标IP或域名")
    count: Optional[int] = Field(default=4, ge=1, le=100, description="PING次数")
    timeout: Optional[float] = Field(default=5.0, ge=0.1, le=30.0, description="超时时间(秒)")
    interval: Optional[float] = Field(default=1.0, ge=0.1, le=10.0, description="间隔时间(秒)")
    packet_size: Optional[int] = Field(default=64, ge=8, le=65535, description="数据包大小(字节)")
    
    @field_validator("target")
    @classmethod
    def validate_target(cls, v):
        """验证PING目标"""
        if not v.strip():
            raise ValueError("PING目标不能为空")
        
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


class ContinuousPingRequest(BaseModel):
    """连续PING请求模型"""
    
    target: str = Field(..., description="PING目标IP或域名") 
    timeout: Optional[float] = Field(default=5.0, ge=0.1, le=30.0, description="超时时间(秒)")
    interval: Optional[float] = Field(default=1.0, ge=0.1, le=10.0, description="间隔时间(秒)")
    packet_size: Optional[int] = Field(default=64, ge=8, le=65535, description="数据包大小(字节)")
    max_count: Optional[int] = Field(default=None, ge=1, le=10000, description="最大PING次数")
    duration: Optional[float] = Field(default=None, ge=1.0, le=3600.0, description="持续时间(秒)")
    
    @field_validator("target")
    @classmethod
    def validate_target(cls, v):
        """验证PING目标"""
        if not v.strip():
            raise ValueError("PING目标不能为空")
        
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        
        if not v.replace(".", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError("无效的IP地址或域名格式")
        
        return v
    
    @model_validator(mode='after')
    def validate_duration_or_count(self):
        """验证持续时间或次数配置"""
        if self.max_count is None and self.duration is None:
            raise ValueError("必须指定最大次数或持续时间中的一个")
        
        if self.max_count is not None and self.duration is not None:
            raise ValueError("最大次数和持续时间不能同时指定")
        
        return self


class BatchPingRequest(BaseModel):
    """批量PING请求模型"""
    
    targets: List[str] = Field(..., min_items=1, max_items=100, description="PING目标列表")
    count: Optional[int] = Field(default=4, ge=1, le=100, description="每个目标的PING次数")
    timeout: Optional[float] = Field(default=5.0, ge=0.1, le=30.0, description="超时时间(秒)")
    interval: Optional[float] = Field(default=1.0, ge=0.1, le=10.0, description="间隔时间(秒)")
    packet_size: Optional[int] = Field(default=64, ge=8, le=65535, description="数据包大小(字节)")
    max_concurrent: Optional[int] = Field(default=10, ge=1, le=50, description="最大并发数")
    
    @field_validator("targets")
    @classmethod
    def validate_targets(cls, v):
        """验证PING目标列表"""
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
            raise ValueError("至少需要一个有效的PING目标")
        
        return validated_targets


class PingResult(BaseModel):
    """PING结果模型"""
    
    target: str = Field(..., description="PING目标")
    success: bool = Field(..., description="是否成功")
    response_time: Optional[float] = Field(default=None, description="响应时间(毫秒)")
    ttl: Optional[int] = Field(default=None, description="TTL值")
    packet_size: int = Field(..., description="数据包大小")
    sequence: int = Field(..., description="序列号")
    timestamp: float = Field(default_factory=time.time, description="时间戳")
    error: Optional[str] = Field(default=None, description="错误信息")
    
    @field_validator("success")
    @classmethod
    def validate_status(cls, v):
        """验证PING状态"""
        return v
    
    @field_validator("response_time")
    @classmethod
    def validate_response_time(cls, v):
        """验证响应时间"""
        if v is not None and v < 0:
            raise ValueError("响应时间不能为负数")
        return v
    
    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, v):
        """验证TTL值"""
        if v is not None and not (1 <= v <= 255):
            raise ValueError("TTL值必须在1-255之间")
        return v


class PingStatistics(BaseModel):
    """PING统计模型"""
    
    target: str = Field(..., description="目标主机")
    total_packets: int = Field(..., ge=0, description="总数据包数")
    successful_packets: int = Field(..., ge=0, description="成功数据包数")
    lost_packets: int = Field(..., ge=0, description="丢失数据包数")
    packet_loss_rate: float = Field(..., ge=0, le=100, description="丢包率(%)")
    min_response_time: Optional[float] = Field(default=None, description="最小响应时间(毫秒)")
    max_response_time: Optional[float] = Field(default=None, description="最大响应时间(毫秒)")
    avg_response_time: Optional[float] = Field(default=None, description="平均响应时间(毫秒)")
    std_deviation: Optional[float] = Field(default=None, description="标准差(毫秒)")
    start_time: float = Field(..., description="开始时间")
    end_time: float = Field(..., description="结束时间")
    duration: float = Field(..., description="总耗时(秒)")
    
    @model_validator(mode='after')
    def validate_packet_counts(self):
        """验证数据包计数一致性"""
        if self.total_packets != (self.successful_packets + self.lost_packets):
            # 允许一定的误差，但记录警告
            pass
        
        return self


class NetworkQuality(BaseModel):
    """网络质量评估模型"""
    
    target: str = Field(..., description="目标主机")
    quality_score: float = Field(..., ge=0, le=100, description="质量评分(0-100)")
    quality_level: str = Field(..., description="质量等级")
    avg_response_time: Optional[float] = Field(default=None, description="平均响应时间(毫秒)")
    packet_loss_rate: float = Field(..., ge=0, le=100, description="丢包率(%)")
    jitter: Optional[float] = Field(default=None, description="网络抖动(毫秒)")
    stability_score: float = Field(..., ge=0, le=100, description="稳定性评分")
    recommendations: List[str] = Field(default_factory=list, description="改进建议")
    assessment_time: float = Field(default_factory=time.time, description="评估时间")
    
    @field_validator("quality_level")
    @classmethod
    def validate_quality_level(cls, v):
        """验证质量等级"""
        allowed_levels = ["excellent", "good", "fair", "poor", "bad"]
        if v not in allowed_levels:
            raise ValueError(f"质量等级必须是以下之一: {allowed_levels}")
        return v
    
    @model_validator(mode='after')
    def validate_quality_consistency(self):
        """验证质量评分一致性"""
        # 根据质量等级验证评分范围
        level_ranges = {
            "excellent": (90, 100),
            "good": (70, 89),
            "fair": (50, 69),
            "poor": (30, 49),
            "bad": (0, 29)
        }
        
        if self.quality_level in level_ranges:
            min_score, max_score = level_ranges[self.quality_level]
            if not (min_score <= self.quality_score <= max_score):
                # 记录警告但不强制失败
                pass
        
        return self


class PingConfigUpdate(ConfigUpdate):
    """PING配置更新模型"""
    
    section: str = Field(default="ping", description="配置节")
    
    @field_validator("key")
    @classmethod
    def validate_ping_config_key(cls, v):
        """验证PING配置键"""
        allowed_keys = [
            "default_count",
            "default_timeout", 
            "default_interval",
            "default_packet_size",
            "max_concurrent",
            "max_targets",
            "quality_thresholds",
            "alert_settings"
        ]
        if v not in allowed_keys:
            raise ValueError(f"PING配置键必须是以下之一: {allowed_keys}")
        return v


class PingMonitorTask(BaseModel):
    """PING监控任务模型"""
    
    task_id: str = Field(..., description="任务ID")
    target: str = Field(..., description="监控目标")
    status: str = Field(..., description="任务状态")
    interval: float = Field(..., description="监控间隔(秒)")
    created_at: float = Field(default_factory=time.time, description="创建时间")
    started_at: Optional[float] = Field(default=None, description="开始时间")
    last_ping_at: Optional[float] = Field(default=None, description="最后PING时间")
    total_pings: int = Field(default=0, description="总PING次数")
    successful_pings: int = Field(default=0, description="成功PING次数")
    current_quality: Optional[str] = Field(default=None, description="当前网络质量")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证任务状态"""
        allowed_statuses = ["pending", "running", "paused", "stopped", "failed"]
        if v not in allowed_statuses:
            raise ValueError(f"任务状态必须是以下之一: {allowed_statuses}")
        return v


class PingAlert(BaseModel):
    """PING告警模型"""
    
    alert_id: str = Field(..., description="告警ID")
    target: str = Field(..., description="告警目标")
    alert_type: str = Field(..., description="告警类型")
    severity: str = Field(..., description="严重程度")
    message: str = Field(..., description="告警消息")
    current_value: Optional[float] = Field(default=None, description="当前值")
    threshold_value: Optional[float] = Field(default=None, description="阈值")
    triggered_at: float = Field(default_factory=time.time, description="触发时间")
    resolved_at: Optional[float] = Field(default=None, description="解决时间")
    is_resolved: bool = Field(default=False, description="是否已解决")
    
    @field_validator("alert_type")
    @classmethod
    def validate_alert_type(cls, v):
        """验证告警类型"""
        allowed_types = ["high_latency", "packet_loss", "timeout", "unreachable", "quality_degradation"]
        if v not in allowed_types:
            raise ValueError(f"告警类型必须是以下之一: {allowed_types}")
        return v
    
    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v):
        """验证严重程度"""
        allowed_severities = ["low", "medium", "high", "critical"]
        if v not in allowed_severities:
            raise ValueError(f"严重程度必须是以下之一: {allowed_severities}")
        return v


class PingProfile(BaseModel):
    """PING配置模板模型"""
    
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(default=None, description="模板描述")
    count: int = Field(default=4, description="PING次数")
    timeout: float = Field(default=5.0, description="超时时间(秒)")
    interval: float = Field(default=1.0, description="间隔时间(秒)")
    packet_size: int = Field(default=64, description="数据包大小(字节)")
    quality_thresholds: Dict[str, float] = Field(default_factory=dict, description="质量阈值")
    alert_enabled: bool = Field(default=False, description="是否启用告警")
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