"""
---------------------------------------------------------------
File name:                  tcp.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                TCP API路由控制器，提供TCP通信相关的API端点
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
                            2025/05/23: 集成真实TCPServer和TCPClient模块;
----
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any
import uuid
import time
import asyncio

from ...schemas.tcp import (
    TCPServerConfig, TCPClientConfig, Message, ClientInfo,
    ServerStatistics, ConnectionInfo, TCPConfigUpdate, TCPServerCommand,
    TCPClientCommand, FileTransfer, HeartbeatMessage, TCPProfile
)
from ...schemas.common import SuccessResponse, ErrorResponse, Pagination
from ...core.tcp_server import TCPServer
from ...core.tcp_client import TCPClient

router = APIRouter()

# 全局TCP服务器和客户端管理
_tcp_servers: Dict[str, TCPServer] = {}
_tcp_clients: Dict[str, TCPClient] = {}
_server_tasks: Dict[str, asyncio.Task] = {}


@router.post("/server/start", response_model=SuccessResponse)
async def start_tcp_server(config: TCPServerConfig, background_tasks: BackgroundTasks):
    """启动TCP服务器
    
    Args:
        config: 服务器配置
        background_tasks: 后台任务管理器
        
    Returns:
        SuccessResponse: 服务器信息
    """
    try:
        server_id = str(uuid.uuid4())
        
        # 创建真实的TCP服务器实例
        tcp_server = TCPServer(
            host=config.host,
            port=config.port,
            max_connections=config.max_connections,
            message_buffer_size=getattr(config, 'buffer_size', 8192),
            client_timeout=config.timeout
        )
        
        # 启动服务器
        await tcp_server.start()
        
        # 存储服务器实例
        _tcp_servers[server_id] = tcp_server
        
        # 获取实际端口（防止端口冲突时自动分配）
        actual_port = tcp_server.actual_port or config.port
        
        server_info = {
            "server_id": server_id,
            "host": config.host,
            "port": actual_port,
            "status": "running",
            "start_time": time.time(),
            "max_connections": config.max_connections,
            "current_connections": len(tcp_server.clients),
            "ssl_enabled": config.ssl_enabled
        }
        
        return SuccessResponse(
            message="TCP服务器启动成功",
            data=server_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器启动失败: {str(e)}"
        )


@router.post("/server/{server_id}/stop", response_model=SuccessResponse)
async def stop_tcp_server(server_id: str):
    """停止TCP服务器
    
    Args:
        server_id: 服务器ID
        
    Returns:
        SuccessResponse: 停止结果
    """
    if server_id not in _tcp_servers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务器不存在"
        )
    
    try:
        tcp_server = _tcp_servers[server_id]
        
        # 停止服务器
        await tcp_server.stop()
        
        # 从管理字典中移除
        del _tcp_servers[server_id]
        
        return SuccessResponse(
            message="TCP服务器已停止",
            data={"server_id": server_id, "status": "stopped"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止服务器失败: {str(e)}"
        )


@router.get("/server/{server_id}/status", response_model=SuccessResponse)
async def get_server_status(server_id: str):
    """获取TCP服务器状态
    
    Args:
        server_id: 服务器ID
        
    Returns:
        SuccessResponse: 服务器状态
    """
    if server_id not in _tcp_servers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务器不存在"
        )
    
    try:
        tcp_server = _tcp_servers[server_id]
        
        # 获取服务器统计信息
        stats = tcp_server.get_statistics()
        
        server_status = {
            "server_id": server_id,
            "host": tcp_server.host,
            "port": tcp_server.actual_port,
            "status": "running" if tcp_server.is_running else "stopped",
            "statistics": stats,
            "current_connections": len(tcp_server.clients),
            "client_list": [
                {
                    "client_id": client_id,
                    "address": f"{client_info.address[0]}:{client_info.address[1]}",
                    "connected_at": client_info.connected_at,
                    "last_activity": client_info.last_activity,
                    "username": client_info.username
                }
                for client_id, client_info in tcp_server.clients.items()
            ]
        }
        
        return SuccessResponse(
            message="服务器状态获取成功",
            data=server_status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务器状态失败: {str(e)}"
        )


@router.post("/client/connect", response_model=SuccessResponse)
async def connect_tcp_client(config: TCPClientConfig):
    """连接TCP客户端
    
    Args:
        config: 客户端配置
        
    Returns:
        SuccessResponse: 连接信息
    """
    try:
        client_id = str(uuid.uuid4())
        
        # 创建真实的TCP客户端实例
        tcp_client = TCPClient(
            server_host=config.host,
            server_port=config.port,
            connect_timeout=config.timeout,
            auto_reconnect=config.auto_reconnect,
            reconnect_interval=getattr(config, 'reconnect_interval', 5.0),
            heartbeat_interval=getattr(config, 'heartbeat_interval', 30.0),
            enable_message_buffering=getattr(config, 'enable_message_buffering', True),
            max_buffer_size=getattr(config, 'max_buffer_size', 1000)
        )
        
        # 连接到服务器
        await tcp_client.connect()
        
        # 存储客户端实例
        _tcp_clients[client_id] = tcp_client
        
        connection_info = {
            "client_id": client_id,
            "server_host": config.host,
            "server_port": config.port,
            "status": "connected",
            "connected_at": time.time(),
            "auto_reconnect": config.auto_reconnect,
            "ssl_enabled": config.ssl_enabled
        }
        
        return SuccessResponse(
            message="TCP客户端连接成功",
            data=connection_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"客户端连接失败: {str(e)}"
        )


@router.post("/client/{client_id}/disconnect", response_model=SuccessResponse)
async def disconnect_tcp_client(client_id: str):
    """断开TCP客户端连接
    
    Args:
        client_id: 客户端ID
        
    Returns:
        SuccessResponse: 断开结果
    """
    if client_id not in _tcp_clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户端不存在"
        )
    
    try:
        tcp_client = _tcp_clients[client_id]
        
        # 断开客户端连接
        await tcp_client.disconnect()
        
        # 从管理字典中移除
        del _tcp_clients[client_id]
        
        return SuccessResponse(
            message="TCP客户端已断开连接",
            data={"client_id": client_id, "status": "disconnected"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"断开客户端连接失败: {str(e)}"
        )


@router.post("/message/send", response_model=SuccessResponse)
async def send_message(message: Message):
    """发送消息
    
    Args:
        message: 消息内容
        
    Returns:
        SuccessResponse: 发送结果
    """
    try:
        message_id = str(uuid.uuid4())
        
        if message.sender_type == "server":
            # 通过服务器发送消息
            if message.sender_id not in _tcp_servers:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="服务器不存在"
                )
            
            tcp_server = _tcp_servers[message.sender_id]
            
            if message.message_type == "broadcast":
                # 广播消息
                broadcast_message = {
                    "type": "broadcast",
                    "content": message.content,
                    "sender": "server",
                    "timestamp": time.time(),
                    "message_id": message_id
                }
                await tcp_server.broadcast_message(broadcast_message)
            elif message.message_type == "private" and message.target_id:
                # 私聊消息
                private_message = {
                    "type": "private",
                    "content": message.content,
                    "sender": "server",
                    "target": message.target_id,
                    "timestamp": time.time(),
                    "message_id": message_id
                }
                success = await tcp_server.send_private_message(message.target_id, private_message)
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="目标客户端不存在"
                    )
        
        elif message.sender_type == "client":
            # 通过客户端发送消息
            if message.sender_id not in _tcp_clients:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="客户端不存在"
                )
            
            tcp_client = _tcp_clients[message.sender_id]
            
            client_message = {
                "type": message.message_type,
                "content": message.content,
                "timestamp": time.time(),
                "message_id": message_id
            }
            
            await tcp_client.send_message(client_message)
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的发送者类型"
            )
        
        result = {
            "message_id": message_id,
            "status": "sent",
            "timestamp": time.time(),
            "sender_type": message.sender_type,
            "sender_id": message.sender_id,
            "message_type": message.message_type,
            "content_preview": message.content[:50] + "..." if len(message.content) > 50 else message.content
        }
        
        return SuccessResponse(
            message="消息发送成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"消息发送失败: {str(e)}"
        )


@router.get("/connections", response_model=SuccessResponse)
async def list_connections():
    """获取连接列表
    
    Returns:
        SuccessResponse: 连接列表
    """
    connections = []
    
    # 添加服务器连接
    for server_id, tcp_server in _tcp_servers.items():
        server_info = {
            "id": server_id,
            "type": "server",
            "status": "running" if tcp_server.is_running else "stopped",
            "host": tcp_server.host,
            "port": tcp_server.actual_port,
            "current_connections": len(tcp_server.clients),
            "max_connections": tcp_server.max_connections,
            "start_time": tcp_server.statistics.start_time
        }
        connections.append(server_info)
    
    # 添加客户端连接
    for client_id, tcp_client in _tcp_clients.items():
        client_info = {
            "id": client_id,
            "type": "client",
            "status": "connected" if tcp_client.is_connected else "disconnected",
            "server_host": tcp_client.server_host,
            "server_port": tcp_client.server_port,
            "auto_reconnect": tcp_client.config.auto_reconnect,
            "connected_at": tcp_client.statistics.connection_time
        }
        connections.append(client_info)
    
    return SuccessResponse(
        message="连接列表获取成功",
        data={
            "total_connections": len(connections),
            "servers": len(_tcp_servers),
            "clients": len(_tcp_clients),
            "connections": connections
        }
    )


@router.get("/statistics", response_model=SuccessResponse)
async def get_tcp_statistics():
    """获取TCP统计信息
    
    Returns:
        SuccessResponse: 统计信息
    """
    try:
        total_stats = {
            "servers": {
                "total": len(_tcp_servers),
                "running": len([s for s in _tcp_servers.values() if s.is_running]),
                "stopped": len([s for s in _tcp_servers.values() if not s.is_running])
            },
            "clients": {
                "total": len(_tcp_clients),
                "connected": len([c for c in _tcp_clients.values() if c.is_connected]),
                "disconnected": len([c for c in _tcp_clients.values() if not c.is_connected])
            },
            "connections": {
                "total_server_connections": sum(len(s.clients) for s in _tcp_servers.values()),
                "messages_sent": sum(s.statistics.messages_sent for s in _tcp_servers.values()),
                "messages_received": sum(s.statistics.messages_received for s in _tcp_servers.values()),
                "bytes_transferred": sum(s.statistics.bytes_sent + s.statistics.bytes_received for s in _tcp_servers.values())
            }
        }
        
        return SuccessResponse(
            message="TCP统计信息获取成功",
            data=total_stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/server/{server_id}/messages", response_model=SuccessResponse)
async def get_server_messages(server_id: str, limit: int = 100):
    """获取服务器消息历史
    
    Args:
        server_id: 服务器ID
        limit: 返回消息数量限制
        
    Returns:
        SuccessResponse: 消息历史
    """
    if server_id not in _tcp_servers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务器不存在"
        )
    
    try:
        tcp_server = _tcp_servers[server_id]
        messages = tcp_server.get_message_history()
        
        # 限制返回数量
        limited_messages = messages[-limit:] if len(messages) > limit else messages
        
        return SuccessResponse(
            message="服务器消息历史获取成功",
            data={
                "server_id": server_id,
                "total_messages": len(messages),
                "returned_messages": len(limited_messages),
                "messages": limited_messages
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息历史失败: {str(e)}"
        )


@router.post("/config", response_model=SuccessResponse)
async def update_tcp_config(config: TCPConfigUpdate):
    """更新TCP配置
    
    Args:
        config: 配置更新请求
        
    Returns:
        SuccessResponse: 更新结果
    """
    # 这里可以更新全局TCP配置
    # 暂时返回配置信息
    return SuccessResponse(
        message="TCP配置已更新",
        data=config.dict()
    )


@router.get("/config", response_model=SuccessResponse)
async def get_tcp_config():
    """获取当前TCP配置
    
    Returns:
        SuccessResponse: 配置信息
    """
    config = {
        "default_timeout": 30.0,
        "max_connections": 1000,
        "buffer_size": 8192,
        "keep_alive": True,
        "auto_reconnect": False,
        "ssl_enabled": False,
        "heartbeat_interval": 60.0,
        "message_history_size": 1000
    }
    
    return SuccessResponse(
        message="TCP配置获取成功",
        data=config
    ) 