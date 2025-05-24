"""
---------------------------------------------------------------
File name:                  __init__.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                Pydantic数据模型包初始化文件，导出所有数据模型
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

# 通用数据模型
from .common import (
    ErrorResponse,
    SuccessResponse,
    Pagination,
    HealthCheck,
    BaseModel
)

# 扫描相关数据模型  
from .scan import (
    ScanRequest,
    PortRangeRequest,
    BatchScanRequest,
    ScanResult,
    ScanStatistics,
    ScanTaskStatus,
    ScanConfigUpdate
)

# PING相关数据模型
from .ping import (
    PingRequest,
    ContinuousPingRequest,
    BatchPingRequest,
    PingResult,
    PingStatistics,
    NetworkQuality,
    PingConfigUpdate
)

# TCP通信数据模型
from .tcp import (
    TCPServerConfig,
    TCPClientConfig,
    Message,
    ClientInfo,
    ServerStatistics,
    ConnectionInfo,
    TCPConfigUpdate
)

__all__ = [
    # Common
    "ErrorResponse",
    "SuccessResponse", 
    "Pagination",
    "HealthCheck",
    "BaseModel",
    
    # Scan
    "ScanRequest",
    "PortRangeRequest",
    "BatchScanRequest", 
    "ScanResult",
    "ScanStatistics",
    "ScanTaskStatus",
    "ScanConfigUpdate",
    
    # Ping
    "PingRequest",
    "ContinuousPingRequest",
    "BatchPingRequest",
    "PingResult", 
    "PingStatistics",
    "NetworkQuality",
    "PingConfigUpdate",
    
    # TCP
    "TCPServerConfig",
    "TCPClientConfig",
    "Message",
    "ClientInfo", 
    "ServerStatistics",
    "ConnectionInfo",
    "TCPConfigUpdate",
] 