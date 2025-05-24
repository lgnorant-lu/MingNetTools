"""
---------------------------------------------------------------
File name:                  network_utils.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                网络工具函数库，提供通用的网络工具函数和辅助功能
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建，TDD实现;
----
"""

import socket
import struct
import ipaddress
import subprocess
import platform
import re
import time
from typing import List, Dict, Optional, Union, Tuple, Any
import asyncio
import logging

# 配置日志
logger = logging.getLogger(__name__)


class NetworkUtils:
    """网络工具函数库"""
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """验证IP地址格式
        
        Args:
            ip: IP地址字符串
            
        Returns:
            是否为有效的IP地址
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: Union[int, str]) -> bool:
        """验证端口号
        
        Args:
            port: 端口号
            
        Returns:
            是否为有效的端口号
        """
        try:
            port_int = int(port)
            return 1 <= port_int <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_hostname(hostname: str) -> bool:
        """验证主机名格式
        
        Args:
            hostname: 主机名
            
        Returns:
            是否为有效的主机名
        """
        if not hostname or len(hostname) > 253:
            return False
        
        # 检查是否为IP地址
        if NetworkUtils.validate_ip_address(hostname):
            return True
        
        # 检查主机名格式
        hostname_pattern = re.compile(
            r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$'
        )
        return bool(hostname_pattern.match(hostname))
    
    @staticmethod
    async def resolve_hostname(hostname: str) -> Optional[str]:
        """异步解析主机名到IP地址
        
        Args:
            hostname: 主机名
            
        Returns:
            解析后的IP地址，失败返回None
        """
        try:
            # 检查是否已经是IP地址
            if NetworkUtils.validate_ip_address(hostname):
                return hostname
            
            # 异步DNS解析
            loop = asyncio.get_event_loop()
            addr_info = await loop.getaddrinfo(
                hostname, None, family=socket.AF_INET
            )
            return addr_info[0][4][0]
        except Exception as e:
            logger.error(f"主机名解析失败 {hostname}: {e}")
            return None
    
    @staticmethod
    def get_local_ip() -> str:
        """获取本机IP地址
        
        Returns:
            本机IP地址
        """
        try:
            # 连接到外部地址以获取本机IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def get_network_interfaces() -> List[Dict[str, str]]:
        """获取网络接口信息
        
        Returns:
            网络接口信息列表
        """
        interfaces = []
        
        try:
            import psutil
            
            # 获取网络接口信息
            for interface_name, addresses in psutil.net_if_addrs().items():
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        interfaces.append({
                            "name": interface_name,
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast
                        })
        except ImportError:
            # 如果psutil不可用，使用基础方法
            interfaces.append({
                "name": "default",
                "address": NetworkUtils.get_local_ip(),
                "netmask": "255.255.255.0",
                "broadcast": None
            })
        except Exception as e:
            logger.error(f"获取网络接口信息失败: {e}")
        
        return interfaces
    
    @staticmethod
    def parse_port_range(port_range: str) -> List[int]:
        """解析端口范围字符串
        
        Args:
            port_range: 端口范围字符串，如 "80", "80-85", "80,443,8080"
            
        Returns:
            端口号列表
        """
        ports = []
        
        try:
            # 分割逗号分隔的部分
            parts = port_range.split(',')
            
            for part in parts:
                part = part.strip()
                
                if '-' in part:
                    # 处理范围，如 "80-85"
                    start, end = part.split('-', 1)
                    start_port = int(start.strip())
                    end_port = int(end.strip())
                    
                    if (NetworkUtils.validate_port(start_port) and 
                        NetworkUtils.validate_port(end_port) and 
                        start_port <= end_port):
                        ports.extend(range(start_port, end_port + 1))
                else:
                    # 处理单个端口
                    port = int(part)
                    if NetworkUtils.validate_port(port):
                        ports.append(port)
        
        except ValueError:
            logger.error(f"无效的端口范围格式: {port_range}")
        
        return sorted(list(set(ports)))  # 去重并排序
    
    @staticmethod
    def calculate_subnet_range(network: str) -> List[str]:
        """计算子网IP范围
        
        Args:
            network: 网络地址，如 "192.168.1.0/24"
            
        Returns:
            IP地址列表
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
            return [str(ip) for ip in net.hosts()]
        except ValueError as e:
            logger.error(f"无效的网络地址 {network}: {e}")
            return []
    
    @staticmethod
    def is_port_in_use(host: str, port: int, timeout: float = 3.0) -> bool:
        """检查端口是否被占用
        
        Args:
            host: 主机地址
            port: 端口号
            timeout: 超时时间
            
        Returns:
            端口是否被占用
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    @staticmethod
    def get_available_port(start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
        """获取可用端口
        
        Args:
            start_port: 起始端口
            max_attempts: 最大尝试次数
            
        Returns:
            可用端口号，找不到返回None
        """
        for i in range(max_attempts):
            port = start_port + i
            if NetworkUtils.validate_port(port):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.bind(("", port))
                        return port
                except OSError:
                    continue
        return None
    
    @staticmethod
    def format_bytes(bytes_count: int) -> str:
        """格式化字节数为人类可读格式
        
        Args:
            bytes_count: 字节数
            
        Returns:
            格式化后的字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024
        return f"{bytes_count:.1f} PB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化时间长度为人类可读格式
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化后的字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}小时"
        else:
            days = seconds / 86400
            return f"{days:.1f}天"
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """获取系统网络信息
        
        Returns:
            系统信息字典
        """
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "hostname": socket.gethostname(),
            "local_ip": NetworkUtils.get_local_ip(),
            "interfaces": NetworkUtils.get_network_interfaces()
        }
        
        try:
            # 获取默认网关
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["route", "print", "0.0.0.0"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    # 解析Windows路由表输出
                    for line in result.stdout.split('\n'):
                        if '0.0.0.0' in line and 'gateway' in line.lower():
                            parts = line.split()
                            if len(parts) >= 3:
                                info["default_gateway"] = parts[2]
                                break
            else:
                # Linux/macOS
                result = subprocess.run(
                    ["ip", "route", "show", "default"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    # 解析Linux路由输出
                    match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if match:
                        info["default_gateway"] = match.group(1)
                else:
                    # 尝试route命令
                    result = subprocess.run(
                        ["route", "-n", "get", "default"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        match = re.search(r'gateway:\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                        if match:
                            info["default_gateway"] = match.group(1)
        
        except Exception as e:
            logger.debug(f"获取网关信息失败: {e}")
            info["default_gateway"] = None
        
        return info
    
    @staticmethod
    def calculate_network_latency(host: str, port: int, timeout: float = 5.0) -> Optional[float]:
        """计算网络延迟
        
        Args:
            host: 主机地址
            port: 端口号
            timeout: 超时时间
            
        Returns:
            延迟时间（毫秒），失败返回None
        """
        try:
            start_time = time.time()
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                
                end_time = time.time()
                
                if result == 0:
                    return (end_time - start_time) * 1000  # 转换为毫秒
                else:
                    return None
        
        except Exception:
            return None
    
    @staticmethod
    def parse_cidr_notation(cidr: str) -> Tuple[str, int]:
        """解析CIDR表示法
        
        Args:
            cidr: CIDR格式的网络地址，如 "192.168.1.0/24"
            
        Returns:
            (网络地址, 子网掩码位数)
        """
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            return str(network.network_address), network.prefixlen
        except ValueError:
            raise ValueError(f"无效的CIDR格式: {cidr}")
    
    @staticmethod
    def cidr_to_subnet_mask(prefix_len: int) -> str:
        """将CIDR前缀长度转换为子网掩码
        
        Args:
            prefix_len: 前缀长度（0-32）
            
        Returns:
            子网掩码字符串
        """
        if not (0 <= prefix_len <= 32):
            raise ValueError("前缀长度必须在0-32之间")
        
        # 创建掩码
        mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF
        
        # 转换为点分十进制
        return socket.inet_ntoa(struct.pack('>I', mask))
    
    @staticmethod
    def subnet_mask_to_cidr(subnet_mask: str) -> int:
        """将子网掩码转换为CIDR前缀长度
        
        Args:
            subnet_mask: 子网掩码字符串
            
        Returns:
            CIDR前缀长度
        """
        try:
            # 转换为32位整数
            mask_int = struct.unpack('>I', socket.inet_aton(subnet_mask))[0]
            
            # 计算前缀长度
            return bin(mask_int).count('1')
        except Exception:
            raise ValueError(f"无效的子网掩码: {subnet_mask}")
    
    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """检查是否为私有IP地址
        
        Args:
            ip: IP地址字符串
            
        Returns:
            是否为私有IP
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    @staticmethod
    def is_loopback_ip(ip: str) -> bool:
        """检查是否为回环IP地址
        
        Args:
            ip: IP地址字符串
            
        Returns:
            是否为回环IP
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_loopback
        except ValueError:
            return False
    
    @staticmethod
    def generate_ip_range(start_ip: str, end_ip: str) -> List[str]:
        """生成IP地址范围
        
        Args:
            start_ip: 起始IP地址
            end_ip: 结束IP地址
            
        Returns:
            IP地址列表
        """
        try:
            start = ipaddress.ip_address(start_ip)
            end = ipaddress.ip_address(end_ip)
            
            if start > end:
                start, end = end, start
            
            ip_list = []
            current = start
            while current <= end:
                ip_list.append(str(current))
                current += 1
            
            return ip_list
        
        except ValueError as e:
            logger.error(f"生成IP范围失败: {e}")
            return []
    
    @staticmethod
    def get_common_ports() -> Dict[str, List[int]]:
        """获取常见端口分类
        
        Returns:
            按服务分类的端口字典
        """
        return {
            "web": [80, 443, 8080, 8443, 8000, 8888],
            "database": [3306, 5432, 1433, 1521, 27017, 6379],
            "mail": [25, 110, 143, 993, 995, 587],
            "file": [21, 22, 23, 873, 69],
            "network": [53, 67, 68, 161, 162],
            "remote": [22, 23, 3389, 5900, 5901],
            "other": [123, 137, 138, 139, 445, 514, 515]
        } 