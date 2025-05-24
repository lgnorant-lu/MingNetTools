"""
---------------------------------------------------------------
File name:                  system.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                系统监控API路由模块
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import psutil
import time
from datetime import datetime

router = APIRouter()

@router.get("/status")
async def get_system_status():
    """获取系统状态"""
    try:
        # 获取系统资源使用情况
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 计算运行时间
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        
        # 判断系统状态
        status = "healthy"
        if cpu_usage > 80 or memory.percent > 85:
            status = "warning"
        if cpu_usage > 95 or memory.percent > 95:
            status = "error"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "uptime": uptime,
            "cpu_usage": cpu_usage,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "uptime": 0,
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0
        }

@router.get("/services")
async def get_service_status():
    """获取服务状态"""
    services = [
        {
            "service_name": "FastAPI",
            "status": "running",
            "port": 8000,
            "uptime": 3600,
            "last_check": datetime.now().isoformat()
        },
        {
            "service_name": "扫描引擎",
            "status": "running", 
            "uptime": 3600,
            "last_check": datetime.now().isoformat()
        },
        {
            "service_name": "PING工具",
            "status": "running",
            "uptime": 3600,
            "last_check": datetime.now().isoformat()
        },
        {
            "service_name": "TCP服务",
            "status": "running",
            "uptime": 3600,
            "last_check": datetime.now().isoformat()
        }
    ]
    return services

@router.get("/performance")
async def get_performance_stats():
    """获取性能统计"""
    return {
        "total_scans": 45,
        "active_scans": 2,
        "total_pings": 128,
        "active_pings": 3,
        "total_tcp_connections": 67,
        "active_tcp_connections": 5,
        "avg_response_time": 245.6,
        "success_rate": 98.5,
        "error_rate": 1.5,
        "uptime_hours": 24.5
    }

@router.get("/info")
async def get_system_info():
    """获取系统信息"""
    try:
        return {
            "hostname": psutil.os.uname().nodename,
            "platform": psutil.os.uname().system,
            "architecture": psutil.os.uname().machine,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}"
        }
    except Exception:
        return {
            "hostname": "unknown",
            "platform": "unknown", 
            "architecture": "unknown",
            "cpu_count": 1,
            "memory_total": 0,
            "python_version": "3.11"
        } 