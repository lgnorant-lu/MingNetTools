"""
---------------------------------------------------------------
File name:                  tcp.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                TCP通信相关Pydantic数据模型，包含服务器配置、客户端配置、消息传递等
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import Field, field_validator, model_validator
import time
import ipaddress

from .common import BaseModel, ConfigUpdate


class TCPServerConfig(BaseModel):
    """TCP服务器配置模型"""
    
    host: str = Field(default="0.0.0.0", description="服务器绑定地址")
    port: int = Field(..., ge=1, le=65535, description="服务器端口")
    max_connections: Optional[int] = Field(default=100, ge=1, le=10000, description="最大连接数")
    timeout: Optional[float] = Field(default=30.0, ge=1.0, le=300.0, description="连接超时(秒)")
    buffer_size: Optional[int] = Field(default=4096, ge=1024, le=65536, description="缓冲区大小(字节)")
    keep_alive: Optional[bool] = Field(default=True, description="是否启用Keep-Alive")
    reuse_address: Optional[bool] = Field(default=True, description="是否重用地址")
    ssl_enabled: Optional[bool] = Field(default=False, description="是否启用SSL")
    ssl_cert_file: Optional[str] = Field(default=None, description="SSL证书文件路径")
    ssl_key_file: Optional[str] = Field(default=None, description="SSL密钥文件路径")
    
    @field_validator("host")
    @classmethod
    def validate_host(cls, v):
        """验证服务器地址"""
        if not v.strip():
            raise ValueError("服务器地址不能为空")
        
        # 验证特殊地址
        if v in ["0.0.0.0", "127.0.0.1", "localhost", "::"]:
            return v
        
        # 验证IP地址
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        
        # 验证域名格式
        if not v.replace(".", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError("无效的IP地址或域名格式")
        
        return v
    
    @model_validator(mode='after')
    def validate_ssl_config(self):
        """验证SSL配置"""
        if self.ssl_enabled:
            if not self.ssl_cert_file:
                raise ValueError("启用SSL时必须提供证书文件")
            if not self.ssl_key_file:
                raise ValueError("启用SSL时必须提供密钥文件")
        
        return self


class TCPClientConfig(BaseModel):
    """TCP客户端配置模型"""
    
    host: str = Field(..., description="服务器地址")
    port: int = Field(..., ge=1, le=65535, description="服务器端口")
    timeout: Optional[float] = Field(default=10.0, ge=1.0, le=300.0, description="连接超时(秒)")
    buffer_size: Optional[int] = Field(default=4096, ge=1024, le=65536, description="缓冲区大小(字节)")
    keep_alive: Optional[bool] = Field(default=True, description="是否启用Keep-Alive")
    auto_reconnect: Optional[bool] = Field(default=False, description="是否自动重连")
    reconnect_interval: Optional[float] = Field(default=5.0, ge=1.0, le=60.0, description="重连间隔(秒)")
    max_reconnect_attempts: Optional[int] = Field(default=3, ge=0, le=100, description="最大重连次数")
    ssl_enabled: Optional[bool] = Field(default=False, description="是否启用SSL")
    ssl_verify: Optional[bool] = Field(default=True, description="是否验证SSL证书")
    
    @field_validator("host")
    def validate_host(cls, v):
        """验证服务器地址"""
        if not v.strip():
            raise ValueError("服务器地址不能为空")
        
        # 验证IP地址
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        
        # 验证域名格式
        if not v.replace(".", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError("无效的IP地址或域名格式")
        
        return v


class Message(BaseModel):
    """消息模型"""
    
    message_id: Optional[str] = Field(default=None, description="消息ID")
    content: str = Field(..., description="消息内容")
    message_type: str = Field(default="text", description="消息类型")
    
    # 发送者信息
    sender: Optional[str] = Field(default=None, description="发送者（兼容性字段）")
    sender_type: Optional[str] = Field(default=None, description="发送者类型(server/client)")
    sender_id: Optional[str] = Field(default=None, description="发送者ID")
    
    # 接收者信息
    recipient: Optional[str] = Field(default=None, description="接收者（兼容性字段）")
    target_id: Optional[str] = Field(default=None, description="目标ID")
    
    timestamp: float = Field(default_factory=time.time, description="消息时间戳")
    encoding: Optional[str] = Field(default="utf-8", description="消息编码")
    compression: Optional[str] = Field(default=None, description="压缩方式")
    priority: Optional[int] = Field(default=0, ge=0, le=10, description="消息优先级")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="消息元数据")
    
    @field_validator("message_type")
    @classmethod
    def validate_message_type(cls, v):
        """验证消息类型"""
        allowed_types = ["text", "binary", "json", "xml", "command", "response", "heartbeat", "broadcast", "private", "chat"]
        if v not in allowed_types:
            raise ValueError(f"消息类型必须是以下之一: {allowed_types}")
        return v
    
    @field_validator("sender_type")
    @classmethod
    def validate_sender_type(cls, v):
        """验证发送者类型"""
        if v is not None:
            allowed_types = ["server", "client", "system"]
            if v not in allowed_types:
                raise ValueError(f"发送者类型必须是以下之一: {allowed_types}")
        return v
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        """验证消息内容"""
        if not v:
            raise ValueError("消息内容不能为空")
        
        # 限制消息大小（1MB）
        if len(v.encode('utf-8')) > 1024 * 1024:
            raise ValueError("消息内容过大，最大支持1MB")
        
        return v
    
    @field_validator("encoding")
    @classmethod
    def validate_encoding(cls, v):
        """验证消息编码"""
        if v:
            allowed_encodings = ["utf-8", "ascii", "latin-1", "gbk", "gb2312"]
            if v.lower() not in allowed_encodings:
                raise ValueError(f"编码必须是以下之一: {allowed_encodings}")
        return v.lower() if v else "utf-8"


class ClientInfo(BaseModel):
    """客户端信息模型"""
    
    client_id: str = Field(..., description="客户端ID")
    address: str = Field(..., description="客户端地址")
    port: int = Field(..., description="客户端端口")
    connected_at: float = Field(default_factory=time.time, description="连接时间")
    last_activity: float = Field(default_factory=time.time, description="最后活动时间")
    status: str = Field(default="connected", description="连接状态")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    protocol_version: Optional[str] = Field(default=None, description="协议版本")
    bytes_sent: int = Field(default=0, ge=0, description="发送字节数")
    bytes_received: int = Field(default=0, ge=0, description="接收字节数")
    messages_sent: int = Field(default=0, ge=0, description="发送消息数")
    messages_received: int = Field(default=0, ge=0, description="接收消息数")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证连接状态"""
        allowed_statuses = ["connected", "disconnected", "timeout", "error"]
        if v not in allowed_statuses:
            raise ValueError(f"连接状态必须是以下之一: {allowed_statuses}")
        return v
    
    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        """验证客户端地址"""
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError("无效的IP地址格式")


class ServerStatistics(BaseModel):
    """服务器统计模型"""
    
    server_id: str = Field(..., description="服务器ID")
    status: str = Field(..., description="服务器状态")
    start_time: float = Field(default_factory=time.time, description="启动时间")
    uptime: Optional[float] = Field(default=None, description="运行时间(秒)")
    current_connections: int = Field(default=0, ge=0, description="当前连接数")
    max_connections: int = Field(..., description="最大连接数")
    total_connections: int = Field(default=0, ge=0, description="总连接数")
    rejected_connections: int = Field(default=0, ge=0, description="拒绝连接数")
    bytes_sent: int = Field(default=0, ge=0, description="总发送字节数")
    bytes_received: int = Field(default=0, ge=0, description="总接收字节数")
    messages_sent: int = Field(default=0, ge=0, description="总发送消息数")
    messages_received: int = Field(default=0, ge=0, description="总接收消息数")
    error_count: int = Field(default=0, ge=0, description="错误次数")
    last_error: Optional[str] = Field(default=None, description="最后错误")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证服务器状态"""
        allowed_statuses = ["starting", "running", "stopping", "stopped", "error"]
        if v not in allowed_statuses:
            raise ValueError(f"服务器状态必须是以下之一: {allowed_statuses}")
        return v


class ConnectionInfo(BaseModel):
    """连接信息模型"""
    
    connection_id: str = Field(..., description="连接ID")
    client_address: str = Field(..., description="客户端地址")
    client_port: int = Field(..., description="客户端端口")
    server_address: str = Field(..., description="服务器地址")
    server_port: int = Field(..., description="服务器端口")
    protocol: str = Field(default="tcp", description="协议类型")
    ssl_enabled: bool = Field(default=False, description="是否启用SSL")
    established_at: float = Field(default_factory=time.time, description="建立时间")
    last_activity: float = Field(default_factory=time.time, description="最后活动时间")
    status: str = Field(default="established", description="连接状态")
    bytes_sent: int = Field(default=0, ge=0, description="发送字节数")
    bytes_received: int = Field(default=0, ge=0, description="接收字节数")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证连接状态"""
        allowed_statuses = ["establishing", "established", "closing", "closed", "timeout", "error"]
        if v not in allowed_statuses:
            raise ValueError(f"连接状态必须是以下之一: {allowed_statuses}")
        return v
    
    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v):
        """验证协议类型"""
        allowed_protocols = ["tcp", "udp", "ssl", "tls"]
        if v.lower() not in allowed_protocols:
            raise ValueError(f"协议类型必须是以下之一: {allowed_protocols}")
        return v.lower()


class TCPConfigUpdate(ConfigUpdate):
    """TCP配置更新模型"""
    
    section: str = Field(default="tcp", description="配置节")
    
    @field_validator("key")
    @classmethod
    def validate_tcp_config_key(cls, v):
        """验证TCP配置键"""
        allowed_keys = [
            "default_timeout",
            "max_connections",
            "buffer_size",
            "keep_alive",
            "auto_reconnect",
            "reconnect_interval",
            "max_reconnect_attempts",
            "ssl_enabled",
            "message_queue_size",
            "heartbeat_interval"
        ]
        if v not in allowed_keys:
            raise ValueError(f"TCP配置键必须是以下之一: {allowed_keys}")
        return v


class TCPServerCommand(BaseModel):
    """TCP服务器命令模型"""
    
    command: str = Field(..., description="命令类型")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="命令参数")
    target_client: Optional[str] = Field(default=None, description="目标客户端ID")
    timestamp: float = Field(default_factory=time.time, description="命令时间戳")
    
    @field_validator("command")
    @classmethod
    def validate_command(cls, v):
        """验证命令类型"""
        allowed_commands = [
            "start", "stop", "restart", "status", "kick_client", 
            "broadcast", "send_message", "get_clients", "get_stats"
        ]
        if v not in allowed_commands:
            raise ValueError(f"命令必须是以下之一: {allowed_commands}")
        return v


class TCPClientCommand(BaseModel):
    """TCP客户端命令模型"""
    
    command: str = Field(..., description="命令类型")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="命令参数")
    timestamp: float = Field(default_factory=time.time, description="命令时间戳")
    
    @field_validator("command")
    @classmethod
    def validate_command(cls, v):
        """验证命令类型"""
        allowed_commands = [
            "connect", "disconnect", "send_message", "send_file", 
            "ping", "status", "reconnect"
        ]
        if v not in allowed_commands:
            raise ValueError(f"命令必须是以下之一: {allowed_commands}")
        return v


class FileTransfer(BaseModel):
    """文件传输模型"""
    
    transfer_id: str = Field(..., description="传输ID")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., ge=0, description="文件大小(字节)")
    content_type: Optional[str] = Field(default="application/octet-stream", description="文件类型")
    checksum: Optional[str] = Field(default=None, description="文件校验和")
    sender: str = Field(..., description="发送者")
    recipient: str = Field(..., description="接收者")
    start_time: float = Field(default_factory=time.time, description="开始时间")
    end_time: Optional[float] = Field(default=None, description="结束时间")
    status: str = Field(default="pending", description="传输状态")
    progress: float = Field(default=0.0, ge=0, le=100, description="传输进度(%)")
    transfer_speed: Optional[float] = Field(default=None, description="传输速度(字节/秒)")
    error: Optional[str] = Field(default=None, description="错误信息")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证传输状态"""
        allowed_statuses = ["pending", "transferring", "completed", "failed", "cancelled"]
        if v not in allowed_statuses:
            raise ValueError(f"传输状态必须是以下之一: {allowed_statuses}")
        return v
    
    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v):
        """验证文件名"""
        if not v.strip():
            raise ValueError("文件名不能为空")
        
        # 检查非法字符
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in illegal_chars:
            if char in v:
                raise ValueError(f"文件名不能包含字符: {char}")
        
        return v.strip()


class HeartbeatMessage(BaseModel):
    """心跳消息模型"""
    
    sender: str = Field(..., description="发送者ID")
    timestamp: float = Field(default_factory=time.time, description="时间戳")
    sequence: int = Field(..., ge=0, description="序列号")
    status: str = Field(default="alive", description="状态")
    data: Optional[Dict[str, Any]] = Field(default=None, description="附加数据")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        allowed_statuses = ["alive", "busy", "idle", "warning", "error"]
        if v not in allowed_statuses:
            raise ValueError(f"状态必须是以下之一: {allowed_statuses}")
        return v


class TCPProfile(BaseModel):
    """TCP配置模板模型"""
    
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(default=None, description="模板描述")
    server_config: Optional[TCPServerConfig] = Field(default=None, description="服务器配置")
    client_config: Optional[TCPClientConfig] = Field(default=None, description="客户端配置")
    message_settings: Optional[Dict[str, Any]] = Field(default=None, description="消息设置")
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