"""
---------------------------------------------------------------
File name:                  ping_tool.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                PING监控引擎，支持ICMP协议、连续监控、统计分析、网络质量评估
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建，TDD实现;
----
"""

import asyncio
import socket
import struct
import time
import random
import logging
import statistics
from typing import Dict, List, Optional, Callable, Any, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import platform

# 尝试导入ping3库作为降级方案
try:
    import ping3
    PING3_AVAILABLE = True
except ImportError:
    PING3_AVAILABLE = False
    ping3 = None

# 配置日志
logger = logging.getLogger(__name__)


class PingMethod(Enum):
    """PING实现方法枚举"""
    RAW_SOCKET = "raw_socket"
    PING3 = "ping3"
    SYSTEM_PING = "system_ping"


class PingStatus(Enum):
    """PING状态枚举"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    UNREACHABLE = "unreachable"
    NAME_RESOLUTION = "name_resolution"
    PERMISSION_DENIED = "permission_denied"
    ERROR = "error"


@dataclass
class PingResult:
    """PING结果数据类"""
    host: str
    ip_address: Optional[str] = None
    success: bool = False
    response_time: Optional[float] = None
    ttl: Optional[int] = None
    packet_size: int = 64
    sequence: int = 1
    timestamp: float = field(default_factory=time.time)
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    method: str = "unknown"


class PingStatistics:
    """PING统计信息类"""
    
    def __init__(self):
        self.packets_sent = 0
        self.packets_received = 0
        self.response_times: List[float] = []
        self.start_time = time.time()
        self.errors: List[str] = []
    
    def add_result(self, result: PingResult):
        """添加PING结果到统计"""
        self.packets_sent += 1
        
        if result.success and result.response_time is not None:
            self.packets_received += 1
            self.response_times.append(result.response_time)
        else:
            if result.error_type:
                self.errors.append(result.error_type)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息字典"""
        packet_loss = 0.0
        if self.packets_sent > 0:
            packet_loss = ((self.packets_sent - self.packets_received) / self.packets_sent) * 100
        
        stats = {
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "packet_loss": packet_loss,
            "duration": time.time() - self.start_time
        }
        
        if self.response_times:
            stats.update({
                "min_time": min(self.response_times),
                "max_time": max(self.response_times),
                "avg_time": statistics.mean(self.response_times),
                "std_dev": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0.0,
                "jitter": self._calculate_jitter()
            })
        else:
            stats.update({
                "min_time": 0.0,
                "max_time": 0.0,
                "avg_time": 0.0,
                "std_dev": 0.0,
                "jitter": 0.0
            })
        
        return stats
    
    def _calculate_jitter(self) -> float:
        """计算网络抖动（相邻响应时间差异的平均值）"""
        if len(self.response_times) < 2:
            return 0.0
        
        differences = []
        for i in range(1, len(self.response_times)):
            diff = abs(self.response_times[i] - self.response_times[i-1])
            differences.append(diff)
        
        return statistics.mean(differences) if differences else 0.0


class ICMPPacket:
    """ICMP数据包处理类"""
    
    ICMP_ECHO_REQUEST = 8
    ICMP_ECHO_REPLY = 0
    
    @staticmethod
    def create_echo_request(packet_id: int, sequence: int, payload_size: int = 56) -> bytes:
        """创建ICMP回显请求数据包"""
        # ICMP头部: type(1) + code(1) + checksum(2) + id(2) + sequence(2) = 8字节
        header = struct.pack("!BBHHH", 
                           ICMPPacket.ICMP_ECHO_REQUEST, 0, 0, packet_id, sequence)
        
        # 创建有效载荷
        payload = b'A' * payload_size
        
        # 计算校验和
        checksum = ICMPPacket._calculate_checksum(header + payload)
        
        # 重新打包带校验和的头部
        header = struct.pack("!BBHHH", 
                           ICMPPacket.ICMP_ECHO_REQUEST, 0, checksum, packet_id, sequence)
        
        return header + payload
    
    @staticmethod
    def parse_echo_reply(data: bytes) -> Optional[Dict[str, Any]]:
        """解析ICMP回显回复数据包"""
        try:
            # 跳过IP头部（通常20字节）
            ip_header_length = (data[0] & 0xF) * 4
            icmp_data = data[ip_header_length:]
            
            if len(icmp_data) < 8:
                return None
            
            # 解析ICMP头部
            icmp_type, code, checksum, packet_id, sequence = struct.unpack(
                "!BBHHH", icmp_data[:8]
            )
            
            if icmp_type != ICMPPacket.ICMP_ECHO_REPLY:
                return None
            
            # 提取TTL
            ttl = data[8]  # IP头部中的TTL字段
            
            return {
                "type": icmp_type,
                "code": code,
                "packet_id": packet_id,
                "sequence": sequence,
                "ttl": ttl
            }
        except (struct.error, IndexError):
            return None
    
    @staticmethod
    def _calculate_checksum(data: bytes) -> int:
        """计算校验和"""
        if len(data) % 2:
            data += b'\x00'
        
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
        
        # 处理进位
        checksum = (checksum >> 16) + (checksum & 0xFFFF)
        checksum += (checksum >> 16)
        
        return (~checksum) & 0xFFFF


class PingEngine:
    """PING监控引擎
    
    特性:
    - 支持ICMP协议实现
    - 连续监控支持
    - 统计分析功能
    - 自动降级策略
    - 网络质量评估
    """
    
    def __init__(self,
                 packet_size: int = 64,
                 timeout: float = 5.0,
                 interval: float = 1.0,
                 use_raw_socket: bool = False,
                 use_ping3_fallback: bool = True,
                 include_geolocation: bool = False):
        """初始化PING引擎
        
        Args:
            packet_size: 数据包大小（字节）
            timeout: 超时时间（秒）
            interval: PING间隔（秒）
            use_raw_socket: 是否使用原生socket
            use_ping3_fallback: 是否使用ping3降级
            include_geolocation: 是否包含地理位置信息
        """
        self.packet_size = packet_size
        self.timeout = timeout
        self.interval = interval
        self.use_raw_socket = use_raw_socket
        self.use_ping3_fallback = use_ping3_fallback and PING3_AVAILABLE
        self.include_geolocation = include_geolocation
        
        # 统计信息
        self.statistics = PingStatistics()
        
        # 进度回调
        self.progress_callback: Optional[Callable] = None
        
        # PING历史记录
        self.ping_history: Dict[str, List[PingResult]] = {}
        
        logger.info(
            f"PING引擎初始化: 包大小={packet_size}, "
            f"超时={timeout}s, 间隔={interval}s"
        )
    
    def set_progress_callback(self, callback: Callable[[int, int, PingResult], None]):
        """设置进度回调函数
        
        Args:
            callback: 回调函数，参数为(current, total, result)
        """
        self.progress_callback = callback
    
    async def ping_host(self, 
                       host: str, 
                       count: Optional[int] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """PING指定主机
        
        Args:
            host: 目标主机
            count: PING次数，None表示单次PING
            
        Returns:
            单次PING返回结果字典，多次PING返回结果列表
        """
        # 解析主机名
        try:
            ip_address = await self._resolve_hostname(host)
        except Exception as e:
            return self._create_error_result(
                host, None, PingStatus.NAME_RESOLUTION, str(e)
            )
        
        if count is None:
            # 单次PING
            result = await self._ping_once(host, ip_address, 1)
            return result.__dict__
        else:
            # 多次PING
            results = []
            for i in range(count):
                result = await self._ping_once(host, ip_address, i + 1)
                results.append(result.__dict__)
                
                # 进度回调
                if self.progress_callback:
                    try:
                        self.progress_callback(i + 1, count, result)
                    except Exception as e:
                        logger.error(f"进度回调执行失败: {e}")
                
                # 等待间隔（除了最后一次）
                if i < count - 1:
                    await asyncio.sleep(self.interval)
            
            return results
    
    async def continuous_ping(self, 
                             host: str, 
                             duration: Optional[int] = None,
                             stop_signal: Optional[asyncio.Event] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """连续PING监控
        
        Args:
            host: 目标主机
            duration: 监控持续时间（秒），None表示无限制
            stop_signal: 停止信号事件
            
        Yields:
            PING结果字典
        """
        logger.info(f"开始连续PING: {host}, 持续时间: {duration}s, 间隔: {self.interval}s")
        
        # 根据目标主机调整超时设置
        original_timeout = self.timeout
        if any(domain in host.lower() for domain in ['google', 'youtube', 'facebook', 'twitter']):
            self.timeout = 8.0  # 外网主机使用8秒超时
            logger.info(f"外网主机 {host} 使用扩展超时: {self.timeout}s")
        
        # 解析主机名
        try:
            ip_address = await self._resolve_hostname(host)
        except Exception as e:
            logger.error(f"解析主机名 {host} 失败: {e}")
            error_result = self._create_error_result(
                host, None, PingStatus.NAME_RESOLUTION, str(e)
            )
            yield error_result.__dict__
            # 恢复原始超时设置
            self.timeout = original_timeout
            return
        
        start_time = time.time()
        sequence = 1
        
        try:
            while True:
                # 检查停止信号
                if stop_signal and stop_signal.is_set():
                    logger.info(f"收到停止信号，终止连续PING {host}")
                    break
                    
                # 检查是否达到持续时间
                if duration is not None and (time.time() - start_time) >= duration:
                    logger.info(f"连续PING完成，总时长: {time.time() - start_time:.2f}s")
                    break
                
                # 执行PING
                ping_start = time.time()
                result = await self._ping_once(host, ip_address, sequence)
                ping_duration = time.time() - ping_start
                
                logger.debug(f"PING {host} ({sequence}): 成功={result.success}, 响应时间={result.response_time}ms, 耗时={ping_duration:.3f}s")
                
                yield result.__dict__
                
                sequence += 1
                
                # 等待间隔 - 在等待期间也检查停止信号
                if self.interval > 0:
                    for _ in range(int(self.interval * 10)):  # 分成0.1秒的小段
                        if stop_signal and stop_signal.is_set():
                            logger.info(f"等待期间收到停止信号，终止连续PING {host}")
                            return
                        await asyncio.sleep(0.1)
                
        finally:
            # 恢复原始超时设置
            self.timeout = original_timeout
            logger.debug(f"连续PING {host} 结束，恢复超时设置: {self.timeout}s")
    
    async def _ping_once(self, host: str, ip_address: Optional[str], sequence: int) -> PingResult:
        """执行单次PING"""
        start_time = time.time()
        
        # 如果没有提供IP地址，先解析主机名
        if ip_address is None:
            try:
                ip_address = await self._resolve_hostname(host)
            except Exception as e:
                return self._create_error_result(
                    host, None, PingStatus.NAME_RESOLUTION, str(e)
                )
        
        # 尝试不同的PING方法 - 优先使用系统PING命令获取TTL
        result = None
        
        # 首先尝试系统ping命令（能提供TTL）
        try:
            result = await self._ping_system_command(host, ip_address, sequence)
            result.method = PingMethod.SYSTEM_PING.value
        except Exception as e:
            logger.debug(f"系统PING命令失败: {e}")
            result = None
        
        # 降级到ping3
        if result is None and self.use_ping3_fallback:
            try:
                result = await self._ping_with_ping3(host, ip_address, sequence)
                result.method = PingMethod.PING3.value
            except Exception as e:
                logger.debug(f"ping3 PING失败: {e}")
                result = None
        
        # 最后尝试原生socket
        if result is None and self.use_raw_socket:
            try:
                result = await self._ping_raw_socket(host, ip_address, sequence)
                result.method = PingMethod.RAW_SOCKET.value
            except PermissionError:
                logger.debug("原生socket PING需要管理员权限")
                result = self._create_error_result(
                    host, ip_address, PingStatus.PERMISSION_DENIED,
                    "需要管理员权限进行原生socket PING"
                )
                result.method = PingMethod.RAW_SOCKET.value
            except Exception as e:
                logger.debug(f"原生socket PING失败: {e}")
                result = None
        
        # 如果所有方法都失败，创建一个通用错误结果
        if result is None:
            result = self._create_error_result(
                host, ip_address, PingStatus.ERROR, "所有PING方法都失败"
            )
            result.method = "all_failed"
        
        # 更新统计信息
        self.statistics.add_result(result)
        
        # 添加到历史记录
        if host not in self.ping_history:
            self.ping_history[host] = []
        self.ping_history[host].append(result)
        
        return result
    
    async def _ping_raw_socket(self, host: str, ip_address: Optional[str], sequence: int) -> PingResult:
        """使用原生socket进行PING"""
        # 创建原生ICMP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.settimeout(self.timeout)
        
        try:
            # 生成数据包ID
            packet_id = random.randint(1, 65535)
            
            # 创建ICMP数据包
            packet = ICMPPacket.create_echo_request(
                packet_id, sequence, self.packet_size - 8  # 减去ICMP头部8字节
            )
            
            # 发送数据包
            start_time = time.time()
            sock.sendto(packet, (ip_address, 0))
            
            # 等待回复
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    receive_time = time.time()
                    
                    # 解析ICMP回复
                    reply = ICMPPacket.parse_echo_reply(data)
                    if reply and reply["packet_id"] == packet_id and reply["sequence"] == sequence:
                        response_time = (receive_time - start_time) * 1000  # 转换为毫秒
                        
                        return PingResult(
                            host=host,
                            ip_address=ip_address,
                            success=True,
                            response_time=response_time,
                            ttl=reply["ttl"],
                            packet_size=self.packet_size,
                            sequence=sequence,
                            timestamp=receive_time
                        )
                
                except socket.timeout:
                    break
                except Exception:
                    continue
            
            # 超时
            return self._create_error_result(
                host, ip_address, PingStatus.TIMEOUT, "请求超时"
            )
        
        finally:
            sock.close()
    
    async def _ping_with_ping3(self, host: str, ip_address: Optional[str], sequence: int) -> PingResult:
        """使用ping3库进行PING"""
        if not PING3_AVAILABLE:
            raise ImportError("ping3库不可用")
        
        start_time = time.time()
        
        # 在线程池中执行ping3（因为它是同步的）
        loop = asyncio.get_event_loop()
        response_time = await loop.run_in_executor(
            None, ping3.ping, ip_address, self.timeout
        )
        
        receive_time = time.time()
        
        if response_time is not None:
            return PingResult(
                host=host,
                ip_address=ip_address,
                success=True,
                response_time=response_time * 1000,  # ping3返回秒，转换为毫秒
                ttl=None,  # ping3不提供TTL信息
                packet_size=self.packet_size,
                sequence=sequence,
                timestamp=receive_time
            )
        else:
            return self._create_error_result(
                host, ip_address, PingStatus.TIMEOUT, "请求超时"
            )
    
    async def _ping_system_command(self, host: str, ip_address: Optional[str], sequence: int) -> PingResult:
        """使用系统ping命令"""
        import subprocess
        import re
        
        try:
            # 如果没有提供IP地址，先解析主机名
            if ip_address is None:
                ip_address = await self._resolve_hostname(host)
            
            # 根据操作系统构建不同的ping命令
            system = platform.system().lower()
            
            if system == "windows":
                # Windows: ping -n 1 -w 1000 host
                cmd = ["ping", "-n", "1", "-w", str(int(self.timeout * 1000)), ip_address]
                # 简化的正则表达式，直接匹配数字+ms模式
                time_pattern = r'(\d+)ms'
                ttl_pattern = r'TTL=(\d+)'
            else:
                # Linux/macOS: ping -c 1 -W 1000 host  
                cmd = ["ping", "-c", "1", "-W", str(int(self.timeout * 1000)), ip_address]
                time_pattern = r'time=(\d+\.?\d*)'
                ttl_pattern = r'ttl=(\d+)'
            
            start_time = time.time()
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            receive_time = time.time()
            
            if process.returncode == 0:
                # 尝试多种编码方式解析输出，优先使用中文编码
                output = None
                for encoding in ['gbk', 'cp936', 'utf-8', 'ascii']:
                    try:
                        output = stdout.decode(encoding, errors='ignore')
                        break
                    except:
                        continue
                
                if not output:
                    output = stdout.decode('utf-8', errors='ignore')
                
                # 提取响应时间 - 使用更宽松的匹配
                time_matches = re.findall(time_pattern, output)
                response_time = None
                if time_matches:
                    # 取第一个匹配的数字作为响应时间
                    response_time = float(time_matches[0])
                
                # 提取TTL - 使用增强的TTL匹配模式
                ttl = None
                ttl_patterns = [
                    r'TTL=(\d+)',
                    r'ttl=(\d+)', 
                    r'TTL\s*=\s*(\d+)',
                    r'ttl\s*=\s*(\d+)',
                    r'生存时间=(\d+)',
                    r'(?:TTL|ttl|生存时间)[:=\s]*(\d+)'
                ]
                
                for ttl_pattern in ttl_patterns:
                    ttl_match = re.search(ttl_pattern, output, re.IGNORECASE)
                    if ttl_match:
                        ttl = int(ttl_match.group(1))
                        break
                
                # 判断PING是否成功 - 增强成功检测
                success = False
                if response_time is not None:
                    success = True
                elif any(indicator in output for indicator in [
                    "0%", "丢失 = 0", "已接收 = 1", "loss = 0", "received = 1",
                    "ѽ = 1", "ʧ = 0", "0% ʧ", "0% 丢失"  # 添加中文乱码版本
                ]):
                    success = True
                    # 如果没有解析到响应时间但显示成功，使用估算值
                    if response_time is None:
                        response_time = (receive_time - start_time) * 1000  # 转换为毫秒
                
                if success:
                    return PingResult(
                        host=host,
                        ip_address=ip_address,
                        success=True,
                        response_time=response_time,
                        ttl=ttl,
                        packet_size=self.packet_size,
                        sequence=sequence,
                        timestamp=receive_time
                    )
                else:
                    return self._create_error_result(
                        host, ip_address, PingStatus.TIMEOUT, "PING超时或无响应"
                    )
            else:
                error_msg = stderr.decode('utf-8', errors='ignore').strip() or "PING失败"
                return self._create_error_result(
                    host, ip_address, PingStatus.UNREACHABLE, error_msg
                )
        
        except Exception as e:
            return self._create_error_result(
                host, ip_address, PingStatus.ERROR, str(e)
            )
    
    async def _resolve_hostname(self, host: str) -> str:
        """解析主机名为IP地址"""
        try:
            # 检查是否已经是IP地址
            ipaddress.ip_address(host)
            return host
        except ValueError:
            # 需要解析主机名
            try:
                loop = asyncio.get_event_loop()
                addr_info = await loop.getaddrinfo(
                    host, None, family=socket.AF_INET
                )
                return addr_info[0][4][0]
            except socket.gaierror as e:
                raise Exception(f"主机名解析失败: {e}")
    
    def _create_error_result(self, 
                           host: str, 
                           ip_address: Optional[str], 
                           error_type: PingStatus, 
                           error_message: str) -> PingResult:
        """创建错误结果"""
        return PingResult(
            host=host,
            ip_address=ip_address,
            success=False,
            response_time=None,
            ttl=None,
            packet_size=self.packet_size,
            sequence=1,
            timestamp=time.time(),
            error_type=error_type.value,
            error_message=error_message
        )
    
    def calculate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算PING统计信息"""
        stats = PingStatistics()
        
        for result_dict in results:
            # 将字典转换为PingResult对象
            result = PingResult(**{k: v for k, v in result_dict.items() 
                                 if k in PingResult.__dataclass_fields__})
            stats.add_result(result)
        
        return stats.get_statistics()
    
    def calculate_jitter(self, response_times: List[float]) -> float:
        """计算网络抖动"""
        if len(response_times) < 2:
            return 0.0
        
        differences = []
        for i in range(1, len(response_times)):
            diff = abs(response_times[i] - response_times[i-1])
            differences.append(diff)
        
        return statistics.mean(differences) if differences else 0.0
    
    def get_ping_history(self, host: str) -> List[Dict[str, Any]]:
        """获取指定主机的PING历史记录"""
        if host in self.ping_history:
            return [result.__dict__ for result in self.ping_history[host]]
        return []
    
    def assess_connection_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估网络连接质量"""
        if not results:
            return {"rating": "unknown", "score": 0}
        
        stats = self.calculate_statistics(results)
        
        # 计算质量分数（0-100）
        score = 100
        
        # 根据丢包率扣分
        packet_loss = stats.get("packet_loss", 0)
        score -= packet_loss * 2  # 每1%丢包扣2分
        
        # 根据平均响应时间扣分
        avg_time = stats.get("avg_time", 0)
        if avg_time > 100:  # 超过100ms
            score -= (avg_time - 100) / 10  # 每10ms扣1分
        
        # 根据抖动扣分
        jitter = stats.get("jitter", 0)
        score -= jitter / 5  # 每5ms抖动扣1分
        
        # 确保分数在0-100范围内
        score = max(0, min(100, score))
        
        # 确定评级
        if score >= 90:
            rating = "excellent"
        elif score >= 75:
            rating = "good"
        elif score >= 60:
            rating = "fair"
        elif score >= 30:
            rating = "poor"
        else:
            rating = "bad"
        
        return {
            "rating": rating,
            "score": score,
            "packet_loss": packet_loss,
            "avg_response_time": avg_time,
            "jitter": jitter
        }
    
    def analyze_network_path(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析网络路径"""
        if not results:
            return {"route_stability": "unknown"}
        
        # 提取TTL值
        ttl_values = [r.get("ttl") for r in results if r.get("ttl") is not None]
        
        if not ttl_values:
            return {"route_stability": "unknown", "ttl_variations": []}
        
        # 分析TTL变化
        unique_ttls = set(ttl_values)
        ttl_changes = len(unique_ttls) > 1
        
        # 路径稳定性评估
        if not ttl_changes:
            stability = "stable"
        elif len(unique_ttls) <= 3:
            stability = "minor_variations"
        else:
            stability = "unstable"
        
        return {
            "route_stability": stability,
            "ttl_variations": list(unique_ttls),
            "potential_routing_changes": ttl_changes
        } 