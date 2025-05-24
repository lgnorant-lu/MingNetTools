"""
---------------------------------------------------------------
File name:                  performance.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                性能监控API路由控制器，提供系统性能监控相关的API端点
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建性能监控API;
----
"""

from fastapi import APIRouter, status
from typing import Dict, Any, Optional

from ...schemas.common import SuccessResponse, ErrorResponse
from ...core.performance import performance_monitor, connection_pool

router = APIRouter()


@router.get("/metrics", response_model=SuccessResponse)
async def get_current_metrics():
    """获取当前性能指标
    
    Returns:
        SuccessResponse: 当前性能指标
    """
    metrics = performance_monitor.get_current_metrics()
    
    return SuccessResponse(
        message="当前性能指标获取成功",
        data=metrics
    )


@router.get("/metrics/endpoints", response_model=SuccessResponse)
async def get_endpoint_metrics():
    """获取端点性能指标
    
    Returns:
        SuccessResponse: 端点性能指标
    """
    endpoint_metrics = performance_monitor.get_endpoint_metrics()
    
    return SuccessResponse(
        message="端点性能指标获取成功",
        data={
            "total_endpoints": len(endpoint_metrics),
            "endpoints": endpoint_metrics
        }
    )


@router.get("/metrics/history", response_model=SuccessResponse)
async def get_metrics_history(limit: int = 100):
    """获取性能指标历史
    
    Args:
        limit: 返回记录数限制
        
    Returns:
        SuccessResponse: 性能指标历史
    """
    history = performance_monitor.get_metrics_history(limit=limit)
    
    return SuccessResponse(
        message="性能指标历史获取成功",
        data={
            "total_records": len(history),
            "limit": limit,
            "history": history
        }
    )


@router.post("/metrics/reset", response_model=SuccessResponse)
async def reset_metrics():
    """重置性能指标
    
    Returns:
        SuccessResponse: 重置结果
    """
    performance_monitor.reset_metrics()
    
    return SuccessResponse(
        message="性能指标已重置",
        data={"reset_time": performance_monitor.current_metrics.timestamp}
    )


@router.get("/pool/stats", response_model=SuccessResponse)
async def get_connection_pool_stats():
    """获取连接池统计信息
    
    Returns:
        SuccessResponse: 连接池统计
    """
    stats = connection_pool.get_pool_stats()
    
    return SuccessResponse(
        message="连接池统计信息获取成功",
        data=stats
    )


@router.post("/monitoring/start", response_model=SuccessResponse)
async def start_monitoring():
    """启动性能监控
    
    Returns:
        SuccessResponse: 启动结果
    """
    performance_monitor.start_monitoring()
    
    return SuccessResponse(
        message="性能监控已启动",
        data={"monitoring": True}
    )


@router.post("/monitoring/stop", response_model=SuccessResponse)
async def stop_monitoring():
    """停止性能监控
    
    Returns:
        SuccessResponse: 停止结果
    """
    performance_monitor.stop_monitoring()
    
    return SuccessResponse(
        message="性能监控已停止",
        data={"monitoring": False}
    )


@router.get("/health", response_model=SuccessResponse)
async def get_performance_health():
    """获取性能健康状况
    
    Returns:
        SuccessResponse: 性能健康状况
    """
    metrics = performance_monitor.get_current_metrics()
    
    # 简单的健康评估
    health_score = 100
    alerts = []
    
    # 评估响应时间
    if metrics['avg_response_time'] > 2.0:
        health_score -= 20
        alerts.append("平均响应时间过高")
    
    # 评估错误率
    if metrics['error_rate'] > 5.0:
        health_score -= 30
        alerts.append("错误率过高")
    
    # 评估系统资源
    if metrics['memory_usage'] > 80.0:
        health_score -= 25
        alerts.append("内存使用率过高")
    
    if metrics['cpu_usage'] > 80.0:
        health_score -= 25
        alerts.append("CPU使用率过高")
    
    # 确定健康状态
    if health_score >= 80:
        health_status = "excellent"
    elif health_score >= 60:
        health_status = "good"
    elif health_score >= 40:
        health_status = "fair"
    elif health_score >= 20:
        health_status = "poor"
    else:
        health_status = "critical"
    
    return SuccessResponse(
        message="性能健康状况获取成功",
        data={
            "health_status": health_status,
            "health_score": max(0, health_score),
            "alerts": alerts,
            "metrics_summary": {
                "avg_response_time": metrics['avg_response_time'],
                "error_rate": metrics['error_rate'],
                "memory_usage": metrics['memory_usage'],
                "cpu_usage": metrics['cpu_usage'],
                "concurrent_requests": metrics['concurrent_requests']
            }
        }
    )


@router.get("/summary", response_model=SuccessResponse)
async def get_performance_summary():
    """获取性能摘要
    
    Returns:
        SuccessResponse: 性能摘要
    """
    current_metrics = performance_monitor.get_current_metrics()
    endpoint_metrics = performance_monitor.get_endpoint_metrics()
    pool_stats = connection_pool.get_pool_stats()
    
    # 找出最慢的端点
    slowest_endpoints = []
    if endpoint_metrics:
        sorted_endpoints = sorted(
            endpoint_metrics.items(),
            key=lambda x: x[1]['avg_response_time'],
            reverse=True
        )
        slowest_endpoints = [
            {
                "endpoint": endpoint,
                "avg_response_time": metrics['avg_response_time'],
                "request_count": metrics['request_count']
            }
            for endpoint, metrics in sorted_endpoints[:5]
        ]
    
    # 找出最繁忙的端点
    busiest_endpoints = []
    if endpoint_metrics:
        sorted_endpoints = sorted(
            endpoint_metrics.items(),
            key=lambda x: x[1]['request_count'],
            reverse=True
        )
        busiest_endpoints = [
            {
                "endpoint": endpoint,
                "request_count": metrics['request_count'],
                "avg_response_time": metrics['avg_response_time']
            }
            for endpoint, metrics in sorted_endpoints[:5]
        ]
    
    return SuccessResponse(
        message="性能摘要获取成功",
        data={
            "overview": {
                "total_requests": current_metrics['request_count'],
                "avg_response_time": current_metrics['avg_response_time'],
                "success_rate": current_metrics['success_rate'],
                "error_rate": current_metrics['error_rate'],
                "concurrent_requests": current_metrics['concurrent_requests']
            },
            "system": {
                "memory_usage": current_metrics['memory_usage'],
                "cpu_usage": current_metrics['cpu_usage']
            },
            "endpoints": {
                "total_endpoints": len(endpoint_metrics),
                "slowest": slowest_endpoints,
                "busiest": busiest_endpoints
            },
            "connections": {
                "pool_connections": pool_stats['total_connections'],
                "max_connections": pool_stats['max_connections'],
                "pool_active": pool_stats['active']
            }
        }
    ) 