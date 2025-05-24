"""
---------------------------------------------------------------
File name:                  tcp_server.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                高性能异步TCP服务器，支持多客户端连接、消息广播、连接管理
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
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import weakref


# 配置日志
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型枚举"""
    CHAT = "chat"
    BROADCAST = "broadcast"
    PRIVATE = "private"
    SYSTEM = "system"
    HEARTBEAT = "heartbeat"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ERROR = "error"


class ClientStatus(Enum):
    """客户端状态枚举"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class ClientInfo:
    """客户端信息数据类"""
    client_id: str
    address: tuple
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    status: str = ClientStatus.CONNECTED.value
    username: Optional[str] = None
    user_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """消息数据类"""
    type: str
    content: str
    sender: Optional[str] = None
    target: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)


class ServerStatistics:
    """服务器统计信息类"""
    
    def __init__(self):
        self.start_time = time.time()
        self.total_connections = 0
        self.current_connections = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.errors = 0
    
    def update_connection(self, connected: bool):
        """更新连接统计"""
        if connected:
            self.total_connections += 1
            self.current_connections += 1
        else:
            self.current_connections = max(0, self.current_connections - 1)
    
    def update_message(self, sent: bool, size: int):
        """更新消息统计"""
        if sent:
            self.messages_sent += 1
            self.bytes_sent += size
        else:
            self.messages_received += 1
            self.bytes_received += size
    
    def update_error(self):
        """更新错误统计"""
        self.errors += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息字典"""
        uptime = time.time() - self.start_time
        
        return {
            "uptime": uptime,
            "total_connections": self.total_connections,
            "current_connections": self.current_connections,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "bytes_transferred": self.bytes_sent + self.bytes_received,
            "errors": self.errors,
            "messages_per_second": (self.messages_sent + self.messages_received) / max(uptime, 1),
            "bytes_per_second": (self.bytes_sent + self.bytes_received) / max(uptime, 1)
        }


class MessageValidator:
    """消息验证器"""
    
    REQUIRED_FIELDS = {"type", "content"}
    MAX_MESSAGE_SIZE = 64 * 1024  # 64KB
    VALID_MESSAGE_TYPES = {t.value for t in MessageType}
    
    @classmethod
    def validate_message(cls, message_data: Dict[str, Any]) -> bool:
        """验证消息格式"""
        try:
            # 检查必需字段
            if not cls.REQUIRED_FIELDS.issubset(message_data.keys()):
                return False
            
            # 检查消息类型
            if message_data.get("type") not in cls.VALID_MESSAGE_TYPES:
                return False
            
            # 检查内容长度
            content = message_data.get("content", "")
            if len(content) > cls.MAX_MESSAGE_SIZE:
                return False
            
            return True
        except Exception:
            return False


class TCPServer:
    """高性能异步TCP服务器
    
    特性:
    - 异步多客户端支持
    - 消息广播和私聊
    - 连接管理和超时检测
    - 消息历史记录
    - 统计信息收集
    - 可配置的连接限制
    """
    
    def __init__(self,
                 host: str = "127.0.0.1",
                 port: int = 8888,
                 max_connections: int = 1000,
                 message_buffer_size: int = 8192,
                 client_timeout: float = 300.0,  # 5分钟
                 keep_message_history: bool = True,
                 max_history_size: int = 1000):
        """初始化TCP服务器
        
        Args:
            host: 绑定主机地址
            port: 绑定端口
            max_connections: 最大连接数
            message_buffer_size: 消息缓冲区大小
            client_timeout: 客户端超时时间（秒）
            keep_message_history: 是否保留消息历史
            max_history_size: 最大历史记录数
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.message_buffer_size = message_buffer_size
        self.client_timeout = client_timeout
        self.keep_message_history = keep_message_history
        self.max_history_size = max_history_size
        
        # 服务器状态
        self.is_running = False
        self.server: Optional[asyncio.Server] = None
        self.actual_port: Optional[int] = None
        
        # 客户端管理
        self.clients: Dict[str, ClientInfo] = {}
        self.client_usernames: Dict[str, str] = {}  # username -> client_id映射
        
        # 消息历史
        self.message_history: List[Message] = []
        
        # 统计信息
        self.statistics = ServerStatistics()
        
        # 任务管理
        self.background_tasks: Set[asyncio.Task] = set()
        
        logger.info(f"TCP服务器初始化: {host}:{port}, 最大连接数: {max_connections}")
    
    async def start(self):
        """启动服务器"""
        if self.is_running:
            logger.warning("服务器已经在运行")
            return
        
        try:
            # 创建服务器
            self.server = await asyncio.start_server(
                self._handle_client_connection,
                self.host,
                self.port
            )
            
            # 获取实际端口（当指定端口为0时）
            self.actual_port = self.server.sockets[0].getsockname()[1]
            self.is_running = True
            
            # 启动后台任务
            self._start_background_tasks()
            
            logger.info(f"TCP服务器启动成功: {self.host}:{self.actual_port}")
            
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止服务器"""
        if not self.is_running:
            logger.warning("服务器未在运行")
            return
        
        logger.info("正在停止TCP服务器...")
        self.is_running = False
        
        # 停止接受新连接
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # 断开所有客户端连接
        disconnect_tasks = []
        for client_id in list(self.clients.keys()):
            task = asyncio.create_task(self.handle_client_disconnect(client_id))
            disconnect_tasks.append(task)
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        # 取消后台任务
        for task in self.background_tasks:
            task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        self.background_tasks.clear()
        
        logger.info("TCP服务器已停止")
    
    async def _handle_client_connection(self, 
                                       reader: asyncio.StreamReader, 
                                       writer: asyncio.StreamWriter):
        """处理新的客户端连接"""
        client_address = writer.get_extra_info('peername')
        logger.info(f"新客户端连接: {client_address}")
        
        # 检查连接数限制
        if len(self.clients) >= self.max_connections:
            logger.warning(f"达到最大连接数限制 ({self.max_connections})，拒绝连接: {client_address}")
            writer.close()
            await writer.wait_closed()
            return
        
        client_id = await self.handle_new_connection(reader, writer)
        if client_id:
            try:
                await self._client_message_loop(client_id)
            except Exception as e:
                logger.error(f"客户端 {client_id} 消息处理异常: {e}")
            finally:
                await self.handle_client_disconnect(client_id)
    
    async def handle_new_connection(self, 
                                   reader: asyncio.StreamReader, 
                                   writer: asyncio.StreamWriter) -> Optional[str]:
        """处理新连接并返回客户端ID"""
        try:
            client_address = writer.get_extra_info('peername')
            client_id = str(uuid.uuid4())
            
            # 创建客户端信息
            client_info = ClientInfo(
                client_id=client_id,
                address=client_address,
                reader=reader,
                writer=writer
            )
            
            # 添加到客户端字典
            self.clients[client_id] = client_info
            
            # 更新统计信息
            self.statistics.update_connection(True)
            
            # 发送连接确认消息
            welcome_message = Message(
                type=MessageType.SYSTEM.value,
                content=f"欢迎连接到服务器，您的ID是: {client_id}",
                sender="server"
            )
            await self._send_message_to_client(client_id, welcome_message)
            
            logger.info(f"客户端 {client_id} 连接成功: {client_address}")
            return client_id
            
        except Exception as e:
            logger.error(f"处理新连接时发生错误: {e}")
            return None
    
    async def handle_client_disconnect(self, client_id: str):
        """处理客户端断开连接"""
        if client_id not in self.clients:
            return
        
        try:
            client_info = self.clients[client_id]
            
            # 更新客户端状态
            client_info.status = ClientStatus.DISCONNECTING.value
            
            # 关闭连接
            if not client_info.writer.is_closing():
                client_info.writer.close()
                await client_info.writer.wait_closed()
            
            # 从客户端字典中移除
            del self.clients[client_id]
            
            # 从用户名映射中移除
            if client_info.username and client_info.username in self.client_usernames:
                del self.client_usernames[client_info.username]
            
            # 更新统计信息
            self.statistics.update_connection(False)
            
            logger.info(f"客户端 {client_id} 已断开连接")
            
        except Exception as e:
            logger.error(f"处理客户端 {client_id} 断开连接时发生错误: {e}")
    
    async def _client_message_loop(self, client_id: str):
        """客户端消息处理循环"""
        client_info = self.clients.get(client_id)
        if not client_info:
            return
        
        try:
            while client_id in self.clients and self.is_running:
                # 读取消息
                message_data = await self._read_message_from_client(client_id)
                if message_data is None:
                    break
                
                # 更新最后活动时间
                client_info.last_activity = time.time()
                
                # 处理消息
                await self._process_client_message(client_id, message_data)
                
        except asyncio.CancelledError:
            logger.info(f"客户端 {client_id} 消息循环被取消")
        except Exception as e:
            logger.error(f"客户端 {client_id} 消息循环异常: {e}")
    
    async def _read_message_from_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """从客户端读取消息"""
        client_info = self.clients.get(client_id)
        if not client_info:
            return None
        
        try:
            # 读取消息长度（4字节）
            length_data = await client_info.reader.readexactly(4)
            message_length = int.from_bytes(length_data, byteorder='big')
            
            if message_length > self.message_buffer_size:
                logger.warning(f"客户端 {client_id} 发送的消息过大: {message_length}")
                return None
            
            # 读取消息内容
            message_data = await client_info.reader.readexactly(message_length)
            message_json = message_data.decode('utf-8')
            
            # 解析JSON
            message_dict = json.loads(message_json)
            
            # 更新统计信息
            self.statistics.update_message(False, len(message_data))
            
            return message_dict
            
        except asyncio.IncompleteReadError:
            logger.info(f"客户端 {client_id} 连接断开")
            return None
        except json.JSONDecodeError:
            logger.warning(f"客户端 {client_id} 发送了无效的JSON消息")
            self.statistics.update_error()
            return None
        except Exception as e:
            logger.error(f"从客户端 {client_id} 读取消息时发生错误: {e}")
            self.statistics.update_error()
            return None
    
    async def _process_client_message(self, client_id: str, message_data: Dict[str, Any]):
        """处理客户端消息"""
        # 验证消息
        parsed_message = self.parse_message(json.dumps(message_data).encode())
        if parsed_message is None:
            logger.warning(f"客户端 {client_id} 发送了无效消息: {message_data}")
            return
        
        message = Message(**parsed_message)
        message.sender = client_id
        
        # 添加到消息历史
        if self.keep_message_history:
            self.add_to_message_history(message.__dict__)
        
        # 根据消息类型处理
        if message.type == MessageType.BROADCAST.value:
            await self.broadcast_message(message.__dict__)
        elif message.type == MessageType.PRIVATE.value:
            target_client = message.target
            if target_client:
                await self.send_private_message(target_client, message.__dict__)
        elif message.type == MessageType.CHAT.value:
            # 聊天消息默认广播
            await self.broadcast_message(message.__dict__)
        elif message.type == MessageType.HEARTBEAT.value:
            # 心跳消息，更新活动时间即可
            pass
        else:
            logger.warning(f"未知消息类型: {message.type}")
    
    def parse_message(self, message_bytes: bytes) -> Optional[Dict[str, Any]]:
        """解析和验证消息"""
        try:
            # 解析JSON
            message_str = message_bytes.decode('utf-8')
            message_data = json.loads(message_str)
            
            # 验证消息格式
            if not MessageValidator.validate_message(message_data):
                return None
            
            return message_data
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        except Exception:
            return None
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """广播消息到所有客户端"""
        if not self.clients:
            return
        
        logger.debug(f"广播消息到 {len(self.clients)} 个客户端")
        
        # 创建广播任务
        tasks = []
        for client_id in list(self.clients.keys()):
            task = asyncio.create_task(
                self._send_message_to_client(client_id, Message(**message))
            )
            tasks.append(task)
        
        # 并发发送
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 检查发送结果
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"广播消息时发生错误: {result}")
    
    async def send_private_message(self, target_client_id: str, message: Dict[str, Any]) -> bool:
        """发送私有消息"""
        if target_client_id not in self.clients:
            logger.warning(f"目标客户端 {target_client_id} 不存在")
            return False
        
        try:
            await self._send_message_to_client(target_client_id, Message(**message))
            return True
        except Exception as e:
            logger.error(f"发送私有消息失败: {e}")
            return False
    
    async def _send_message_to_client(self, client_id: str, message: Message):
        """向指定客户端发送消息"""
        client_info = self.clients.get(client_id)
        if not client_info or client_info.writer.is_closing():
            return
        
        try:
            # 序列化消息
            message_json = json.dumps(message.__dict__)
            message_bytes = message_json.encode('utf-8')
            
            # 发送消息长度（4字节）+ 消息内容
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            
            client_info.writer.write(length_bytes + message_bytes)
            await client_info.writer.drain()
            
            # 更新统计信息
            self.statistics.update_message(True, len(message_bytes))
            
        except Exception as e:
            logger.error(f"向客户端 {client_id} 发送消息失败: {e}")
            # 客户端可能已断开，从列表中移除
            await self.handle_client_disconnect(client_id)
    
    def add_to_message_history(self, message: Dict[str, Any]):
        """添加消息到历史记录"""
        if not self.keep_message_history:
            return
        
        # 转换为Message对象
        msg = Message(**{k: v for k, v in message.items() if k in Message.__dataclass_fields__})
        self.message_history.append(msg)
        
        # 限制历史记录大小
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """获取消息历史记录"""
        return [msg.__dict__ for msg in self.message_history]
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 客户端超时检查任务
        timeout_task = asyncio.create_task(self._timeout_check_loop())
        self.background_tasks.add(timeout_task)
        timeout_task.add_done_callback(self.background_tasks.discard)
    
    async def _timeout_check_loop(self):
        """客户端超时检查循环"""
        while self.is_running:
            try:
                await self.check_client_timeouts()
                await asyncio.sleep(30)  # 每30秒检查一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"超时检查循环异常: {e}")
                await asyncio.sleep(30)
    
    async def check_client_timeouts(self):
        """检查客户端超时"""
        current_time = time.time()
        timeout_clients = []
        
        for client_id, client_info in self.clients.items():
            if current_time - client_info.last_activity > self.client_timeout:
                timeout_clients.append(client_id)
        
        # 断开超时的客户端
        for client_id in timeout_clients:
            logger.info(f"客户端 {client_id} 超时，断开连接")
            await self.handle_client_disconnect(client_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        return self.statistics.get_statistics() 