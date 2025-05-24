"""
---------------------------------------------------------------
File name:                  tcp_client.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                异步TCP客户端，支持自动重连、心跳保活、消息缓冲
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建，TDD实现;
----
"""

import asyncio
import json
import time
import logging
import uuid
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import weakref


# 配置日志
logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """连接状态枚举"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class MessagePriority(Enum):
    """消息优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class ClientMessage:
    """客户端消息数据类"""
    type: str
    content: str
    target: Optional[str] = None
    priority: int = MessagePriority.NORMAL.value
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ConnectionConfig:
    """连接配置数据类"""
    server_host: str = "127.0.0.1"
    server_port: int = 8888
    connect_timeout: float = 10.0
    auto_reconnect: bool = True
    reconnect_interval: float = 5.0
    max_reconnect_attempts: int = -1  # -1表示无限重试
    heartbeat_interval: float = 30.0
    enable_message_buffering: bool = True
    max_buffer_size: int = 1000


class ClientStatistics:
    """客户端统计信息类"""
    
    def __init__(self):
        self.start_time = time.time()
        self.connection_time: Optional[float] = None
        self.total_connections = 0
        self.reconnection_count = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.heartbeat_sent_count = 0
        self.errors = 0
    
    def update_connection(self, connected: bool):
        """更新连接统计"""
        if connected:
            self.total_connections += 1
            self.connection_time = time.time()
        else:
            self.connection_time = None
    
    def update_reconnection(self):
        """更新重连统计"""
        self.reconnection_count += 1
    
    def update_message(self, sent: bool, size: int):
        """更新消息统计"""
        if sent:
            self.messages_sent += 1
            self.bytes_sent += size
        else:
            self.messages_received += 1
            self.bytes_received += size
    
    def update_heartbeat(self):
        """更新心跳统计"""
        self.heartbeat_sent_count += 1
    
    def update_error(self):
        """更新错误统计"""
        self.errors += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息字典"""
        uptime = time.time() - self.start_time
        connection_duration = (
            time.time() - self.connection_time 
            if self.connection_time else 0.0
        )
        
        return {
            "uptime": uptime,
            "connection_time": self.connection_time,
            "connection_duration": connection_duration,
            "total_connections": self.total_connections,
            "reconnection_count": self.reconnection_count,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "heartbeat_sent_count": self.heartbeat_sent_count,
            "errors": self.errors
        }


class TCPClient:
    """异步TCP客户端
    
    特性:
    - 自动重连机制
    - 心跳保活
    - 消息缓冲
    - 连接状态回调
    - 统计信息收集
    - 优先级消息队列
    """
    
    def __init__(self,
                 server_host: str = "127.0.0.1",
                 server_port: int = 8888,
                 connect_timeout: float = 10.0,
                 auto_reconnect: bool = True,
                 reconnect_interval: float = 5.0,
                 heartbeat_interval: float = 30.0,
                 enable_message_buffering: bool = True,
                 max_buffer_size: int = 1000):
        """初始化TCP客户端
        
        Args:
            server_host: 服务器主机
            server_port: 服务器端口
            connect_timeout: 连接超时时间
            auto_reconnect: 是否自动重连
            reconnect_interval: 重连间隔
            heartbeat_interval: 心跳间隔
            enable_message_buffering: 是否启用消息缓冲
            max_buffer_size: 最大缓冲区大小
        """
        # 连接配置
        self.config = ConnectionConfig(
            server_host=server_host,
            server_port=server_port,
            connect_timeout=connect_timeout,
            auto_reconnect=auto_reconnect,
            reconnect_interval=reconnect_interval,
            heartbeat_interval=heartbeat_interval,
            enable_message_buffering=enable_message_buffering,
            max_buffer_size=max_buffer_size
        )
        
        # 连接状态
        self.is_connected = False
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.connection_id: Optional[str] = None
        
        # 网络连接
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        
        # 消息缓冲
        self.message_buffer: List[ClientMessage] = []
        
        # 回调函数
        self.message_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        # 统计信息
        self.statistics = ClientStatistics()
        
        # 任务管理
        self.background_tasks: set = set()
        self.reconnect_attempts = 0
        
        # 控制标志
        self._should_reconnect = True
        self._stop_event = asyncio.Event()
        
        logger.info(f"TCP客户端初始化: {server_host}:{server_port}")
    
    @property
    def server_host(self) -> str:
        """获取服务器主机"""
        return self.config.server_host
    
    @property
    def server_port(self) -> int:
        """获取服务器端口"""
        return self.config.server_port
    
    def set_message_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """设置消息接收回调函数
        
        Args:
            callback: 回调函数，参数为消息字典
        """
        self.message_callback = callback
    
    def set_status_callback(self, callback: Callable[[str, Optional[str]], None]):
        """设置状态变化回调函数
        
        Args:
            callback: 回调函数，参数为(status, client_id)
        """
        self.status_callback = callback
    
    async def connect(self) -> bool:
        """连接到服务器"""
        if self.is_connected:
            logger.warning("客户端已经连接")
            return True
        
        self._update_status(ConnectionStatus.CONNECTING)
        
        try:
            # 尝试连接
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(
                    self.config.server_host,
                    self.config.server_port
                ),
                timeout=self.config.connect_timeout
            )
            
            # 连接成功
            self.is_connected = True
            self.connection_id = str(uuid.uuid4())
            self.reconnect_attempts = 0
            
            # 更新统计信息
            self.statistics.update_connection(True)
            
            # 更新状态
            self._update_status(ConnectionStatus.CONNECTED)
            
            # 启动后台任务
            self._start_background_tasks()
            
            # 发送缓冲的消息
            if self.config.enable_message_buffering:
                await self._send_buffered_messages()
            
            logger.info(f"成功连接到服务器: {self.config.server_host}:{self.config.server_port}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"连接超时: {self.config.server_host}:{self.config.server_port}")
            self._update_status(ConnectionStatus.ERROR)
            self.statistics.update_error()
            return False
        except Exception as e:
            logger.error(f"连接失败: {e}")
            self._update_status(ConnectionStatus.ERROR)
            self.statistics.update_error()
            return False
    
    async def disconnect(self):
        """断开连接"""
        if not self.is_connected:
            logger.warning("客户端未连接")
            return
        
        logger.info("断开与服务器的连接")
        
        # 停止自动重连
        self._should_reconnect = False
        self._stop_event.set()
        
        # 更新状态
        self._update_status(ConnectionStatus.DISCONNECTED)
        
        # 关闭连接
        if self.writer and not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()
        
        # 取消后台任务
        for task in self.background_tasks:
            task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        self.background_tasks.clear()
        
        # 清理状态
        self.is_connected = False
        self.reader = None
        self.writer = None
        self.connection_id = None
        
        # 更新统计信息
        self.statistics.update_connection(False)
        
        logger.info("已断开连接")
    
    async def send_message(self, message: Union[Dict[str, Any], ClientMessage]) -> bool:
        """发送消息
        
        Args:
            message: 消息字典或ClientMessage对象
            
        Returns:
            是否发送成功
        """
        # 转换为ClientMessage对象
        if isinstance(message, dict):
            client_message = ClientMessage(
                type=message.get("type", "chat"),
                content=message.get("content", ""),
                target=message.get("target"),
                priority=message.get("priority", MessagePriority.NORMAL.value)
            )
        else:
            client_message = message
        
        # 如果未连接且启用缓冲，将消息加入缓冲区
        if not self.is_connected and self.config.enable_message_buffering:
            if len(self.message_buffer) < self.config.max_buffer_size:
                self.message_buffer.append(client_message)
                # 按优先级排序
                self.message_buffer.sort(key=lambda x: x.priority, reverse=True)
                logger.debug(f"消息已缓冲: {client_message.message_id}")
                return True
            else:
                logger.warning("消息缓冲区已满，丢弃消息")
                return False
        
        # 直接发送消息
        return await self._send_message_direct(client_message)
    
    async def _send_message_direct(self, message: ClientMessage) -> bool:
        """直接发送消息"""
        if not self.is_connected or not self.writer:
            return False
        
        try:
            # 序列化消息
            message_dict = {
                "type": message.type,
                "content": message.content,
                "target": message.target,
                "timestamp": message.timestamp,
                "message_id": message.message_id
            }
            
            message_json = json.dumps(message_dict)
            message_bytes = message_json.encode('utf-8')
            
            # 发送消息长度（4字节）+ 消息内容
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            
            self.writer.write(length_bytes + message_bytes)
            await self.writer.drain()
            
            # 更新统计信息
            self.statistics.update_message(True, len(message_bytes))
            
            logger.debug(f"消息发送成功: {message.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self.statistics.update_error()
            
            # 如果连接断开，触发重连
            if self.config.auto_reconnect:
                await self._handle_connection_loss()
            
            return False
    
    async def _send_buffered_messages(self):
        """发送缓冲的消息"""
        if not self.message_buffer:
            return
        
        logger.info(f"发送 {len(self.message_buffer)} 条缓冲消息")
        
        # 复制缓冲区并清空
        messages_to_send = self.message_buffer.copy()
        self.message_buffer.clear()
        
        # 发送消息
        for message in messages_to_send:
            success = await self._send_message_direct(message)
            if not success:
                # 如果发送失败，重新加入缓冲区
                if message.retry_count < message.max_retries:
                    message.retry_count += 1
                    self.message_buffer.append(message)
                else:
                    logger.warning(f"消息 {message.message_id} 重试次数过多，丢弃")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 消息接收任务
        receive_task = asyncio.create_task(self._message_receive_loop())
        self.background_tasks.add(receive_task)
        receive_task.add_done_callback(self.background_tasks.discard)
        
        # 心跳任务
        if self.config.heartbeat_interval > 0:
            heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self.background_tasks.add(heartbeat_task)
            heartbeat_task.add_done_callback(self.background_tasks.discard)
        
        # 自动重连任务
        if self.config.auto_reconnect:
            reconnect_task = asyncio.create_task(self._auto_reconnect_loop())
            self.background_tasks.add(reconnect_task)
            reconnect_task.add_done_callback(self.background_tasks.discard)
    
    async def _message_receive_loop(self):
        """消息接收循环"""
        try:
            while self.is_connected and not self._stop_event.is_set():
                message = await self._receive_message()
                if message is None:
                    break
                
                # 调用消息回调
                if self.message_callback:
                    try:
                        self.message_callback(message)
                    except Exception as e:
                        logger.error(f"消息回调执行失败: {e}")
        
        except asyncio.CancelledError:
            logger.debug("消息接收循环被取消")
        except Exception as e:
            logger.error(f"消息接收循环异常: {e}")
            if self.config.auto_reconnect:
                await self._handle_connection_loss()
    
    async def _receive_message(self) -> Optional[Dict[str, Any]]:
        """接收消息"""
        if not self.reader:
            return None
        
        try:
            # 读取消息长度（4字节）
            length_data = await self.reader.readexactly(4)
            message_length = int.from_bytes(length_data, byteorder='big')
            
            # 读取消息内容
            message_data = await self.reader.readexactly(message_length)
            message_json = message_data.decode('utf-8')
            
            # 解析JSON
            message_dict = json.loads(message_json)
            
            # 更新统计信息
            self.statistics.update_message(False, len(message_data))
            
            return message_dict
            
        except asyncio.IncompleteReadError:
            logger.info("服务器连接断开")
            return None
        except json.JSONDecodeError:
            logger.warning("收到无效的JSON消息")
            self.statistics.update_error()
            return None
        except Exception as e:
            logger.error(f"接收消息时发生错误: {e}")
            self.statistics.update_error()
            return None
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        try:
            while self.is_connected and not self._stop_event.is_set():
                await asyncio.sleep(self.config.heartbeat_interval)
                
                if not self.is_connected:
                    break
                
                # 发送心跳消息
                heartbeat_message = ClientMessage(
                    type="heartbeat",
                    content="ping"
                )
                
                success = await self._send_message_direct(heartbeat_message)
                if success:
                    self.statistics.update_heartbeat()
                else:
                    logger.warning("心跳发送失败")
        
        except asyncio.CancelledError:
            logger.debug("心跳循环被取消")
        except Exception as e:
            logger.error(f"心跳循环异常: {e}")
    
    async def _auto_reconnect_loop(self):
        """自动重连循环"""
        try:
            while self._should_reconnect and not self._stop_event.is_set():
                await self._stop_event.wait()
                
                if not self._should_reconnect:
                    break
                
                # 检查是否需要重连
                if not self.is_connected and self._should_reconnect:
                    await self._attempt_reconnect()
        
        except asyncio.CancelledError:
            logger.debug("自动重连循环被取消")
        except Exception as e:
            logger.error(f"自动重连循环异常: {e}")
    
    async def _handle_connection_loss(self):
        """处理连接丢失"""
        if not self.is_connected:
            return
        
        logger.warning("检测到连接丢失")
        
        # 更新状态
        self.is_connected = False
        self._update_status(ConnectionStatus.ERROR)
        
        # 清理连接
        if self.writer and not self.writer.is_closing():
            self.writer.close()
        
        self.reader = None
        self.writer = None
        
        # 更新统计信息
        self.statistics.update_connection(False)
        
        # 触发重连
        if self.config.auto_reconnect and self._should_reconnect:
            self._stop_event.set()
    
    async def _attempt_reconnect(self):
        """尝试重连"""
        if (self.config.max_reconnect_attempts > 0 and 
            self.reconnect_attempts >= self.config.max_reconnect_attempts):
            logger.error("达到最大重连次数，停止重连")
            self._should_reconnect = False
            return
        
        self.reconnect_attempts += 1
        self.statistics.update_reconnection()
        
        logger.info(f"尝试重连 (第 {self.reconnect_attempts} 次)")
        self._update_status(ConnectionStatus.RECONNECTING)
        
        # 等待重连间隔
        await asyncio.sleep(self.config.reconnect_interval)
        
        # 尝试连接
        success = await self.connect()
        
        if not success:
            # 重连失败，继续尝试
            self._stop_event.clear()
            self._stop_event.set()
        else:
            # 重连成功
            self._stop_event.clear()
    
    async def _simulate_connection_loss(self):
        """模拟连接丢失（用于测试）"""
        logger.debug("模拟连接丢失")
        await self._handle_connection_loss()
    
    def _update_status(self, status: ConnectionStatus):
        """更新连接状态"""
        old_status = self.connection_status
        self.connection_status = status
        
        # 调用状态回调
        if self.status_callback and old_status != status:
            try:
                self.status_callback(status.value, self.connection_id)
            except Exception as e:
                logger.error(f"状态回调执行失败: {e}")
        
        logger.debug(f"连接状态变更: {old_status.value} -> {status.value}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取客户端统计信息"""
        return self.statistics.get_statistics() 