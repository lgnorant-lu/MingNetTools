"""
---------------------------------------------------------------
File name:                  performance.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                API性能监控和优化工具
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建性能监控模块;
----
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import weakref
from contextlib import contextmanager
import psutil
import json


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    request_count: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    error_count: int = 0
    success_count: int = 0
    concurrent_requests: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    @property
    def avg_response_time(self) -> float:
        """平均响应时间"""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.request_count == 0:
            return 0.0
        return (self.success_count / self.request_count) * 100
    
    @property
    def error_rate(self) -> float:
        """错误率"""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100


@dataclass
class RequestInfo:
    """请求信息"""
    method: str
    path: str
    start_time: float
    end_time: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    
    @property
    def response_time(self) -> float:
        """响应时间"""
        if self.end_time is None:
            return 0.0
        return self.end_time - self.start_time
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status_code is not None and 200 <= self.status_code < 400


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, 
                 max_history: int = 1000,
                 metrics_interval: float = 60.0,
                 enable_system_metrics: bool = True):
        """初始化性能监控器
        
        Args:
            max_history: 最大历史记录数
            metrics_interval: 指标收集间隔（秒）
            enable_system_metrics: 是否启用系统指标监控
        """
        self.max_history = max_history
        self.metrics_interval = metrics_interval
        self.enable_system_metrics = enable_system_metrics
        
        # 指标存储
        self.metrics_history: deque = deque(maxlen=max_history)
        self.request_history: deque = deque(maxlen=max_history)
        self.endpoint_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        
        # 实时指标
        self.current_metrics = PerformanceMetrics()
        self.active_requests: Dict[str, RequestInfo] = {}
        
        # 监控控制
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # 告警配置
        self.alert_thresholds = {
            'max_response_time': 5.0,  # 最大响应时间
            'max_error_rate': 10.0,    # 最大错误率
            'max_memory_usage': 80.0,  # 最大内存使用率
            'max_cpu_usage': 80.0      # 最大CPU使用率
        }
        
        # 告警回调
        self.alert_callbacks: List[Callable] = []
        
        logger.info("性能监控器初始化完成")
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """添加告警回调函数
        
        Args:
            callback: 告警回调函数，参数为(alert_type, data)
        """
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self):
        """启动监控"""
        if self._monitoring:
            return
        
        self._monitoring = True
        
        # 启动异步监控任务
        if asyncio.get_event_loop().is_running():
            self._monitor_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None
        
        logger.info("性能监控已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        try:
            while self._monitoring:
                await self._collect_metrics()
                await asyncio.sleep(self.metrics_interval)
        except asyncio.CancelledError:
            logger.debug("监控循环被取消")
        except Exception as e:
            logger.error(f"监控循环异常: {e}")
    
    async def _collect_metrics(self):
        """收集指标"""
        try:
            # 收集系统指标
            if self.enable_system_metrics:
                self.current_metrics.memory_usage = psutil.virtual_memory().percent
                self.current_metrics.cpu_usage = psutil.cpu_percent()
            
            # 更新并发请求数
            self.current_metrics.concurrent_requests = len(self.active_requests)
            self.current_metrics.timestamp = time.time()
            
            # 保存历史记录
            metrics_copy = PerformanceMetrics(
                request_count=self.current_metrics.request_count,
                total_response_time=self.current_metrics.total_response_time,
                min_response_time=self.current_metrics.min_response_time,
                max_response_time=self.current_metrics.max_response_time,
                error_count=self.current_metrics.error_count,
                success_count=self.current_metrics.success_count,
                concurrent_requests=self.current_metrics.concurrent_requests,
                memory_usage=self.current_metrics.memory_usage,
                cpu_usage=self.current_metrics.cpu_usage,
                timestamp=self.current_metrics.timestamp
            )
            
            self.metrics_history.append(metrics_copy)
            
            # 检查告警
            await self._check_alerts(metrics_copy)
            
        except Exception as e:
            logger.error(f"收集指标时发生错误: {e}")
    
    async def _check_alerts(self, metrics: PerformanceMetrics):
        """检查告警条件"""
        alerts = []
        
        # 检查响应时间告警
        if metrics.max_response_time > self.alert_thresholds['max_response_time']:
            alerts.append({
                'type': 'high_response_time',
                'value': metrics.max_response_time,
                'threshold': self.alert_thresholds['max_response_time'],
                'message': f"响应时间过高: {metrics.max_response_time:.2f}s"
            })
        
        # 检查错误率告警
        if metrics.error_rate > self.alert_thresholds['max_error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'value': metrics.error_rate,
                'threshold': self.alert_thresholds['max_error_rate'],
                'message': f"错误率过高: {metrics.error_rate:.2f}%"
            })
        
        # 检查内存使用率告警
        if metrics.memory_usage > self.alert_thresholds['max_memory_usage']:
            alerts.append({
                'type': 'high_memory_usage',
                'value': metrics.memory_usage,
                'threshold': self.alert_thresholds['max_memory_usage'],
                'message': f"内存使用率过高: {metrics.memory_usage:.2f}%"
            })
        
        # 检查CPU使用率告警
        if metrics.cpu_usage > self.alert_thresholds['max_cpu_usage']:
            alerts.append({
                'type': 'high_cpu_usage',
                'value': metrics.cpu_usage,
                'threshold': self.alert_thresholds['max_cpu_usage'],
                'message': f"CPU使用率过高: {metrics.cpu_usage:.2f}%"
            })
        
        # 触发告警回调
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert['type'], alert)
                except Exception as e:
                    logger.error(f"告警回调执行失败: {e}")
    
    @contextmanager
    def track_request(self, method: str, path: str):
        """跟踪请求上下文管理器
        
        Args:
            method: HTTP方法
            path: 请求路径
        """
        request_id = f"{method}:{path}:{time.time()}"
        request_info = RequestInfo(
            method=method,
            path=path,
            start_time=time.time()
        )
        
        # 添加到活跃请求
        self.active_requests[request_id] = request_info
        
        try:
            yield request_info
        except Exception as e:
            request_info.error = str(e)
            raise
        finally:
            # 完成请求
            request_info.end_time = time.time()
            
            # 从活跃请求中移除
            self.active_requests.pop(request_id, None)
            
            # 更新指标
            self._update_metrics(request_info)
            
            # 添加到历史记录
            self.request_history.append(request_info)
    
    def _update_metrics(self, request_info: RequestInfo):
        """更新指标"""
        with self._lock:
            # 更新全局指标
            self.current_metrics.request_count += 1
            
            if request_info.response_time > 0:
                self.current_metrics.total_response_time += request_info.response_time
                self.current_metrics.min_response_time = min(
                    self.current_metrics.min_response_time, 
                    request_info.response_time
                )
                self.current_metrics.max_response_time = max(
                    self.current_metrics.max_response_time, 
                    request_info.response_time
                )
            
            if request_info.is_success:
                self.current_metrics.success_count += 1
            else:
                self.current_metrics.error_count += 1
            
            # 更新端点指标
            endpoint_key = f"{request_info.method} {request_info.path}"
            endpoint_metrics = self.endpoint_metrics[endpoint_key]
            
            endpoint_metrics.request_count += 1
            
            if request_info.response_time > 0:
                endpoint_metrics.total_response_time += request_info.response_time
                endpoint_metrics.min_response_time = min(
                    endpoint_metrics.min_response_time, 
                    request_info.response_time
                )
                endpoint_metrics.max_response_time = max(
                    endpoint_metrics.max_response_time, 
                    request_info.response_time
                )
            
            if request_info.is_success:
                endpoint_metrics.success_count += 1
            else:
                endpoint_metrics.error_count += 1
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        with self._lock:
            return {
                'request_count': self.current_metrics.request_count,
                'avg_response_time': self.current_metrics.avg_response_time,
                'min_response_time': self.current_metrics.min_response_time,
                'max_response_time': self.current_metrics.max_response_time,
                'success_rate': self.current_metrics.success_rate,
                'error_rate': self.current_metrics.error_rate,
                'concurrent_requests': self.current_metrics.concurrent_requests,
                'memory_usage': self.current_metrics.memory_usage,
                'cpu_usage': self.current_metrics.cpu_usage,
                'timestamp': self.current_metrics.timestamp
            }
    
    def get_endpoint_metrics(self) -> Dict[str, Dict[str, Any]]:
        """获取端点指标"""
        with self._lock:
            result = {}
            for endpoint, metrics in self.endpoint_metrics.items():
                result[endpoint] = {
                    'request_count': metrics.request_count,
                    'avg_response_time': metrics.avg_response_time,
                    'min_response_time': metrics.min_response_time,
                    'max_response_time': metrics.max_response_time,
                    'success_rate': metrics.success_rate,
                    'error_rate': metrics.error_rate
                }
            return result
    
    def get_metrics_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取指标历史"""
        history = list(self.metrics_history)[-limit:]
        return [
            {
                'request_count': m.request_count,
                'avg_response_time': m.avg_response_time,
                'success_rate': m.success_rate,
                'error_rate': m.error_rate,
                'concurrent_requests': m.concurrent_requests,
                'memory_usage': m.memory_usage,
                'cpu_usage': m.cpu_usage,
                'timestamp': m.timestamp
            }
            for m in history
        ]
    
    def reset_metrics(self):
        """重置指标"""
        with self._lock:
            self.current_metrics = PerformanceMetrics()
            self.endpoint_metrics.clear()
            self.metrics_history.clear()
            self.request_history.clear()
        
        logger.info("性能指标已重置")


class ConnectionPool:
    """连接池管理器"""
    
    def __init__(self, 
                 max_connections: int = 100,
                 max_idle_time: float = 300.0,
                 cleanup_interval: float = 60.0):
        """初始化连接池
        
        Args:
            max_connections: 最大连接数
            max_idle_time: 最大空闲时间
            cleanup_interval: 清理间隔
        """
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.cleanup_interval = cleanup_interval
        
        # 连接存储
        self.connections: Dict[str, Any] = {}
        self.connection_info: Dict[str, Dict] = {}
        
        # 控制
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._active = False
        
        logger.info(f"连接池初始化: max_connections={max_connections}")
    
    async def start(self):
        """启动连接池"""
        if self._active:
            return
        
        self._active = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("连接池已启动")
    
    async def stop(self):
        """停止连接池"""
        if not self._active:
            return
        
        self._active = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None
        
        # 关闭所有连接
        async with self._lock:
            for connection_id, connection in self.connections.items():
                try:
                    if hasattr(connection, 'close'):
                        await connection.close()
                except Exception as e:
                    logger.error(f"关闭连接失败: {e}")
            
            self.connections.clear()
            self.connection_info.clear()
        
        logger.info("连接池已停止")
    
    async def _cleanup_loop(self):
        """清理循环"""
        try:
            while self._active:
                await self._cleanup_idle_connections()
                await asyncio.sleep(self.cleanup_interval)
        except asyncio.CancelledError:
            logger.debug("连接池清理循环被取消")
        except Exception as e:
            logger.error(f"连接池清理循环异常: {e}")
    
    async def _cleanup_idle_connections(self):
        """清理空闲连接"""
        current_time = time.time()
        to_remove = []
        
        async with self._lock:
            for connection_id, info in self.connection_info.items():
                if current_time - info['last_used'] > self.max_idle_time:
                    to_remove.append(connection_id)
            
            for connection_id in to_remove:
                connection = self.connections.pop(connection_id, None)
                self.connection_info.pop(connection_id, None)
                
                if connection:
                    try:
                        if hasattr(connection, 'close'):
                            await connection.close()
                    except Exception as e:
                        logger.error(f"关闭空闲连接失败: {e}")
        
        if to_remove:
            logger.debug(f"清理了 {len(to_remove)} 个空闲连接")
    
    async def get_connection(self, connection_id: str) -> Optional[Any]:
        """获取连接"""
        async with self._lock:
            if connection_id in self.connections:
                # 更新最后使用时间
                self.connection_info[connection_id]['last_used'] = time.time()
                return self.connections[connection_id]
        
        return None
    
    async def add_connection(self, connection_id: str, connection: Any) -> bool:
        """添加连接"""
        async with self._lock:
            if len(self.connections) >= self.max_connections:
                logger.warning("连接池已满，无法添加新连接")
                return False
            
            self.connections[connection_id] = connection
            self.connection_info[connection_id] = {
                'created_at': time.time(),
                'last_used': time.time()
            }
            
            return True
    
    async def remove_connection(self, connection_id: str) -> bool:
        """移除连接"""
        async with self._lock:
            connection = self.connections.pop(connection_id, None)
            self.connection_info.pop(connection_id, None)
            
            if connection:
                try:
                    if hasattr(connection, 'close'):
                        await connection.close()
                except Exception as e:
                    logger.error(f"关闭连接失败: {e}")
                
                return True
        
        return False
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计"""
        return {
            'total_connections': len(self.connections),
            'max_connections': self.max_connections,
            'active': self._active,
            'connection_ids': list(self.connections.keys())
        }


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()

# 全局连接池实例
connection_pool = ConnectionPool() 