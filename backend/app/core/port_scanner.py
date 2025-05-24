"""
---------------------------------------------------------------
File name:                  port_scanner.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                异步端口扫描引擎，支持TCP/UDP扫描、并发控制、服务识别
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建，TDD实现;
----
"""

import asyncio
import socket
import time
import logging
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json


# 配置日志
logger = logging.getLogger(__name__)


class ScanStatus(Enum):
    """扫描状态枚举"""
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    TIMEOUT = "timeout"
    ERROR = "error"


class ScanProtocol(Enum):
    """扫描协议枚举"""
    TCP = "tcp"
    UDP = "udp"


@dataclass
class ScanResult:
    """扫描结果数据类"""
    host: str
    port: int
    protocol: str
    status: str
    response_time: Optional[float] = None
    service_name: Optional[str] = None
    service_version: Optional[str] = None
    banner: Optional[str] = None
    confidence_level: float = 1.0
    detected_at: float = field(default_factory=time.time)
    error_message: Optional[str] = None


@dataclass
class ScanTarget:
    """扫描目标数据类"""
    host: str
    ports: List[int]
    protocol: str = "tcp"


class ScanStatistics:
    """扫描统计信息类"""
    
    def __init__(self):
        self.total_scans = 0
        self.open_ports = 0
        self.closed_ports = 0
        self.filtered_ports = 0
        self.error_count = 0
        self.response_times: List[float] = []
        self.start_time = time.time()
    
    def add_result(self, result: ScanResult):
        """添加扫描结果到统计"""
        self.total_scans += 1
        
        if result.status == ScanStatus.OPEN.value:
            self.open_ports += 1
        elif result.status == ScanStatus.CLOSED.value:
            self.closed_ports += 1
        elif result.status == ScanStatus.FILTERED.value:
            self.filtered_ports += 1
        elif result.status == ScanStatus.ERROR.value:
            self.error_count += 1
        
        if result.response_time is not None:
            self.response_times.append(result.response_time)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息字典"""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0.0
        )
        
        return {
            "total_scans": self.total_scans,
            "open_ports": self.open_ports,
            "closed_ports": self.closed_ports,
            "filtered_ports": self.filtered_ports,
            "error_count": self.error_count,
            "average_response_time": avg_response_time,
            "scan_duration": time.time() - self.start_time
        }


class ServiceDetector:
    """服务检测器"""
    
    # 常见端口服务映射
    COMMON_PORTS = {
        22: "ssh",
        23: "telnet",
        25: "smtp",
        53: "dns",
        80: "http",
        110: "pop3",
        143: "imap",
        443: "https",
        993: "imaps",
        995: "pop3s",
        3389: "rdp",
        5432: "postgresql",
        3306: "mysql",
        6379: "redis",
        27017: "mongodb"
    }
    
    @classmethod
    def detect_service(cls, port: int, banner: Optional[str] = None) -> Optional[str]:
        """检测端口服务"""
        # 基于端口号的基础检测
        service = cls.COMMON_PORTS.get(port)
        
        # TODO: 基于banner的高级检测
        if banner and service:
            # 这里可以添加更复杂的banner分析逻辑
            pass
        
        return service


class PortScannerEngine:
    """异步端口扫描引擎
    
    特性:
    - 支持TCP/UDP协议扫描
    - 自适应并发控制
    - 智能服务识别
    - 实时进度回调
    - 统计信息收集
    """
    
    def __init__(self, 
                 max_concurrent: int = 100,
                 timeout: float = 3.0,
                 retry_count: int = 1,
                 service_detection: bool = False,
                 banner_grabbing: bool = False):
        """初始化端口扫描引擎
        
        Args:
            max_concurrent: 最大并发连接数
            timeout: 连接超时时间（秒）
            retry_count: 重试次数
            service_detection: 是否启用服务检测
            banner_grabbing: 是否启用banner抓取
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.retry_count = retry_count
        self.service_detection = service_detection
        self.banner_grabbing = banner_grabbing
        
        # 并发控制
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # 统计信息
        self.statistics = ScanStatistics()
        
        # 进度回调
        self.progress_callback: Optional[Callable] = None
        
        logger.info(
            f"端口扫描引擎初始化: 并发={max_concurrent}, "
            f"超时={timeout}s, 重试={retry_count}"
        )
    
    def set_progress_callback(self, callback: Callable[[int, int, str, int], None]):
        """设置进度回调函数
        
        Args:
            callback: 回调函数，参数为(current, total, host, port)
        """
        self.progress_callback = callback
    
    async def scan_port(self, 
                       host: str, 
                       port: int, 
                       protocol: str = "tcp") -> Dict[str, Any]:
        """扫描单个端口
        
        Args:
            host: 目标主机
            port: 目标端口
            protocol: 扫描协议 (tcp/udp/syn)
            
        Returns:
            扫描结果字典
        """
        # 验证输入参数
        if not self._validate_inputs(host, port, protocol):
            return self._create_error_result(host, port, protocol, "无效的输入参数")
        
        async with self.semaphore:
            start_time = time.time()
            
            try:
                if protocol.lower() == "tcp":
                    result = await self._scan_tcp_port(host, port)
                elif protocol.lower() == "udp":
                    result = await self._scan_udp_port(host, port)
                elif protocol.lower() == "syn":
                    result = await self._scan_syn_port(host, port)
                else:
                    return self._create_error_result(host, port, protocol, "不支持的协议")
                
                # 计算响应时间
                if result["status"] == ScanStatus.OPEN.value:
                    result["response_time"] = (time.time() - start_time) * 1000  # 转换为毫秒
                
                # 服务检测
                if self.service_detection and result["status"] == ScanStatus.OPEN.value:
                    result["service_name"] = ServiceDetector.detect_service(
                        port, result.get("banner")
                    )
                
                # 更新统计信息
                scan_result = ScanResult(**result)
                self.statistics.add_result(scan_result)
                
                return result
                
            except Exception as e:
                logger.error(f"扫描端口 {host}:{port} 时发生错误: {e}")
                return self._create_error_result(host, port, protocol, str(e))
    
    async def _scan_tcp_port(self, host: str, port: int) -> Dict[str, Any]:
        """扫描TCP端口"""
        for attempt in range(self.retry_count + 1):
            try:
                # 尝试连接
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=self.timeout
                )
                
                # 成功连接，端口开放
                result = {
                    "host": host,
                    "port": port,
                    "protocol": "tcp",
                    "status": ScanStatus.OPEN.value,
                    "banner": None
                }
                
                # Banner抓取
                if self.banner_grabbing:
                    try:
                        # 等待banner数据
                        banner_data = await asyncio.wait_for(
                            reader.read(1024), 
                            timeout=2.0
                        )
                        if banner_data:
                            result["banner"] = banner_data.decode('utf-8', errors='ignore').strip()
                    except asyncio.TimeoutError:
                        pass  # 没有banner数据
                    except Exception as e:
                        logger.debug(f"Banner抓取失败: {e}")
                
                # 关闭连接
                writer.close()
                await writer.wait_closed()
                
                return result
                
            except asyncio.TimeoutError:
                if attempt == self.retry_count:
                    return {
                        "host": host,
                        "port": port,
                        "protocol": "tcp",
                        "status": ScanStatus.TIMEOUT.value
                    }
            except ConnectionRefusedError:
                return {
                    "host": host,
                    "port": port,
                    "protocol": "tcp",
                    "status": ScanStatus.CLOSED.value
                }
            except Exception as e:
                if attempt == self.retry_count:
                    return {
                        "host": host,
                        "port": port,
                        "protocol": "tcp",
                        "status": ScanStatus.ERROR.value,
                        "error_message": str(e)
                    }
                # 重试
                await asyncio.sleep(0.1)
        
        # 不应该到达这里
        return {
            "host": host,
            "port": port,
            "protocol": "tcp",
            "status": ScanStatus.ERROR.value
        }
    
    async def _scan_udp_port(self, host: str, port: int) -> Dict[str, Any]:
        """扫描UDP端口（异步实现）"""
        try:
            # 使用asyncio在线程池中执行UDP扫描，避免阻塞事件循环
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._sync_udp_scan, 
                host, 
                port
            )
            return result
            
        except Exception as e:
            return {
                "host": host,
                "port": port,
                "protocol": "udp",
                "status": ScanStatus.ERROR.value,
                "error_message": str(e)
            }
    
    def _sync_udp_scan(self, host: str, port: int) -> Dict[str, Any]:
        """同步UDP扫描（在线程池中执行）"""
        try:
            # 创建UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            # 发送探测数据
            test_data = b"test"
            sock.sendto(test_data, (host, port))
            
            # 尝试接收响应
            try:
                data, addr = sock.recvfrom(1024)
                status = ScanStatus.OPEN.value
            except socket.timeout:
                # UDP端口可能开放但不响应
                status = ScanStatus.FILTERED.value
            
            sock.close()
            
            return {
                "host": host,
                "port": port,
                "protocol": "udp",
                "status": status
            }
            
        except Exception as e:
            return {
                "host": host,
                "port": port,
                "protocol": "udp",
                "status": ScanStatus.ERROR.value,
                "error_message": str(e)
            }
    
    async def _scan_syn_port(self, host: str, port: int) -> Dict[str, Any]:
        """扫描SYN端口（简化为TCP连接探测）"""
        try:
            # SYN扫描需要原始socket权限，这里简化为快速TCP连接探测
            # 在实际生产环境中，可以集成nmap或其他专业工具
            
            # 使用更短的超时进行快速连接尝试
            quick_timeout = min(self.timeout, 1.0)  # 最多1秒
            
            try:
                # 尝试快速连接
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=quick_timeout
                )
                
                # 立即关闭连接（模拟SYN扫描的行为）
                writer.close()
                await writer.wait_closed()
                
                return {
                    "host": host,
                    "port": port,
                    "protocol": "syn",
                    "status": ScanStatus.OPEN.value
                }
                
            except asyncio.TimeoutError:
                return {
                    "host": host,
                    "port": port,
                    "protocol": "syn",
                    "status": ScanStatus.FILTERED.value
                }
            except ConnectionRefusedError:
                return {
                    "host": host,
                    "port": port,
                    "protocol": "syn",
                    "status": ScanStatus.CLOSED.value
                }
            
        except Exception as e:
            return {
                "host": host,
                "port": port,
                "protocol": "syn",
                "status": ScanStatus.ERROR.value,
                "error_message": str(e)
            }
    
    async def scan_port_range(self, 
                             host: str, 
                             start_port: int, 
                             end_port: int,
                             protocol: str = "tcp") -> List[Dict[str, Any]]:
        """扫描端口范围
        
        Args:
            host: 目标主机
            start_port: 起始端口
            end_port: 结束端口
            protocol: 扫描协议
            
        Returns:
            扫描结果列表
        """
        if start_port > end_port:
            raise ValueError("起始端口不能大于结束端口")
        
        ports = list(range(start_port, end_port + 1))
        total_ports = len(ports)
        
        logger.info(f"开始扫描 {host} 的端口范围 {start_port}-{end_port}")
        
        # 创建扫描任务
        tasks = []
        for i, port in enumerate(ports):
            task = self._scan_with_progress(host, port, protocol, i, total_ports)
            tasks.append(task)
        
        # 并发执行扫描
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                logger.error(f"扫描任务异常: {result}")
        
        logger.info(f"端口范围扫描完成，共扫描 {len(valid_results)} 个端口")
        return valid_results
    
    async def batch_scan(self, targets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """批量扫描多个目标
        
        Args:
            targets: 目标列表，每个目标包含host和ports字段
            
        Returns:
            按主机分组的扫描结果字典
        """
        results = {}
        
        for target in targets:
            host = target["host"]
            ports = target.get("ports", [])
            protocol = target.get("protocol", "tcp")
            
            logger.info(f"开始扫描主机 {host}，端口数量: {len(ports)}")
            
            # 为每个主机创建扫描任务
            tasks = []
            for port in ports:
                task = self.scan_port(host, port, protocol)
                tasks.append(task)
            
            # 执行扫描
            host_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤有效结果
            valid_results = []
            for result in host_results:
                if isinstance(result, dict):
                    valid_results.append(result)
            
            results[host] = valid_results
        
        return results
    
    async def _scan_with_progress(self, 
                                 host: str, 
                                 port: int, 
                                 protocol: str,
                                 current: int, 
                                 total: int) -> Dict[str, Any]:
        """带进度回调的扫描"""
        result = await self.scan_port(host, port, protocol)
        
        # 调用进度回调
        if self.progress_callback:
            try:
                self.progress_callback(current + 1, total, host, port)
            except Exception as e:
                logger.error(f"进度回调执行失败: {e}")
        
        return result
    
    def _validate_inputs(self, host: str, port: int, protocol: str) -> bool:
        """验证输入参数"""
        if not host or not host.strip():
            return False
        
        if not (1 <= port <= 65535):
            return False
        
        if protocol.lower() not in ["tcp", "udp", "syn"]:
            return False
        
        return True
    
    def _create_error_result(self, 
                           host: str, 
                           port: int, 
                           protocol: str, 
                           error_message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            "host": host,
            "port": port,
            "protocol": protocol,
            "status": ScanStatus.ERROR.value,
            "error_message": error_message,
            "response_time": None,
            "service_name": None,
            "banner": None
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取扫描统计信息"""
        return self.statistics.get_statistics() 