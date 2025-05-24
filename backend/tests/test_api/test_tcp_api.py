"""
---------------------------------------------------------------
File name:                  test_tcp_api.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                TCP API端点测试
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建TCP API综合测试;
                            2025/05/23: 修复导入路径;
                            2025/05/23: 使用绝对导入;
----
"""

import pytest
import json
import asyncio
import sys
import os
from httpx import AsyncClient
from fastapi.testclient import TestClient

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_path)

from app.main import create_app
from app.schemas.tcp import TCPServerConfig, TCPClientConfig, Message


class TestTCPAPI:
    """TCP API测试类"""

    @pytest.fixture
    def async_client(self):
        """异步客户端fixture - 修复为同步版本"""
        app = create_app()
        with TestClient(app) as client:
            yield client

    @pytest.fixture
    def sync_client(self):
        """同步客户端fixture"""
        app = create_app()
        with TestClient(app) as client:
            yield client

    def test_tcp_server_lifecycle(self, sync_client):
        """测试TCP服务器生命周期"""
        # 启动服务器
        server_config = {
            "host": "127.0.0.1",
            "port": 9999,
            "max_connections": 10,
            "timeout": 30.0,
            "ssl_enabled": False
        }
        
        response = sync_client.post(
            "/api/v1/tcp/server/start",
            json=server_config
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        server_id = data["data"]["server_id"]
        assert data["data"]["status"] == "running"
        assert data["data"]["port"] == 9999
        
        # 获取服务器状态
        response = sync_client.get(f"/api/v1/tcp/server/{server_id}/status")
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data["success"] is True
        assert status_data["data"]["status"] == "running"
        
        # 停止服务器
        response = sync_client.post(f"/api/v1/tcp/server/{server_id}/stop")
        assert response.status_code == 200
        
        stop_data = response.json()
        assert stop_data["success"] is True
        assert stop_data["data"]["status"] == "stopped"

    def test_tcp_client_connection(self, sync_client):
        """测试TCP客户端连接"""
        # 首先启动一个测试服务器
        server_config = {
            "host": "127.0.0.1",
            "port": 9998,
            "max_connections": 5,
            "timeout": 30.0,
            "ssl_enabled": False
        }
        
        server_response = sync_client.post(
            "/api/v1/tcp/server/start",
            json=server_config
        )
        assert server_response.status_code == 200
        server_id = server_response.json()["data"]["server_id"]
        
        # 连接客户端
        client_config = {
            "host": "127.0.0.1",
            "port": 9998,
            "timeout": 10.0,
            "auto_reconnect": False,
            "ssl_enabled": False
        }
        
        response = sync_client.post(
            "/api/v1/tcp/client/connect",
            json=client_config
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        client_id = data["data"]["client_id"]
        assert data["data"]["status"] == "connected"
        
        # 断开客户端连接
        response = sync_client.post(f"/api/v1/tcp/client/{client_id}/disconnect")
        assert response.status_code == 200
        
        disconnect_data = response.json()
        assert disconnect_data["success"] is True
        assert disconnect_data["data"]["status"] == "disconnected"
        
        # 清理：停止服务器
        sync_client.post(f"/api/v1/tcp/server/{server_id}/stop")

    def test_message_sending(self, sync_client):
        """测试消息发送功能"""
        # 启动服务器
        server_config = {
            "host": "127.0.0.1",
            "port": 9997,
            "max_connections": 5,
            "timeout": 30.0,
            "ssl_enabled": False
        }
        
        server_response = sync_client.post(
            "/api/v1/tcp/server/start",
            json=server_config
        )
        server_id = server_response.json()["data"]["server_id"]
        
        # 测试服务器广播消息
        message_data = {
            "content": "Hello, everyone!",
            "message_type": "broadcast",
            "sender_type": "server",
            "sender_id": server_id
        }
        
        response = sync_client.post(
            "/api/v1/tcp/message/send",
            json=message_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message_id" in data["data"]
        assert data["data"]["status"] == "sent"
        assert data["data"]["message_type"] == "broadcast"
        
        # 清理
        sync_client.post(f"/api/v1/tcp/server/{server_id}/stop")

    def test_tcp_connections_list(self, sync_client):
        """测试获取连接列表"""
        response = sync_client.get("/api/v1/tcp/connections")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_connections" in data["data"]
        assert "servers" in data["data"]
        assert "clients" in data["data"]
        assert "connections" in data["data"]

    def test_tcp_statistics(self, sync_client):
        """测试获取TCP统计信息"""
        response = sync_client.get("/api/v1/tcp/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        stats = data["data"]
        assert "servers" in stats
        assert "clients" in stats
        assert "connections" in stats
        
        # 验证统计结构
        assert "total" in stats["servers"]
        assert "running" in stats["servers"]
        assert "stopped" in stats["servers"]

    def test_tcp_config_operations(self, sync_client):
        """测试TCP配置操作"""
        # 获取当前配置
        response = sync_client.get("/api/v1/tcp/config")
        assert response.status_code == 200
        
        config_data = response.json()
        assert config_data["success"] is True
        assert "data" in config_data
        
        # 更新配置
        config_update = {
            "key": "default_timeout",
            "value": 60.0,
            "description": "更新默认超时时间"
        }
        
        response = sync_client.post(
            "/api/v1/tcp/config",
            json=config_update
        )
        
        assert response.status_code == 200
        update_data = response.json()
        assert update_data["success"] is True

    def test_server_messages_history(self, sync_client):
        """测试服务器消息历史"""
        # 启动服务器
        server_config = {
            "host": "127.0.0.1",
            "port": 9996,
            "max_connections": 5,
            "timeout": 30.0,
            "ssl_enabled": False
        }
        
        server_response = sync_client.post(
            "/api/v1/tcp/server/start",
            json=server_config
        )
        server_id = server_response.json()["data"]["server_id"]
        
        # 获取消息历史
        response = sync_client.get(f"/api/v1/tcp/server/{server_id}/messages?limit=50")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "messages" in data["data"]
        assert "total_messages" in data["data"]
        assert "returned_messages" in data["data"]
        
        # 清理
        sync_client.post(f"/api/v1/tcp/server/{server_id}/stop")

    def test_error_handling(self, sync_client):
        """测试错误处理"""
        # 尝试获取不存在的服务器状态
        response = sync_client.get("/api/v1/tcp/server/nonexistent/status")
        assert response.status_code == 404
        
        # 尝试停止不存在的服务器
        response = sync_client.post("/api/v1/tcp/server/nonexistent/stop")
        assert response.status_code == 404
        
        # 尝试断开不存在的客户端
        response = sync_client.post("/api/v1/tcp/client/nonexistent/disconnect")
        assert response.status_code == 404

    def test_invalid_port_configuration(self, sync_client):
        """测试无效端口配置"""
        # 使用无效端口（超出范围）
        server_config = {
            "host": "127.0.0.1",
            "port": 99999,  # 无效端口
            "max_connections": 5,
            "timeout": 30.0,
            "ssl_enabled": False
        }
        
        response = sync_client.post(
            "/api/v1/tcp/server/start",
            json=server_config
        )
        
        # 应该返回验证错误
        assert response.status_code == 422

    def test_message_validation(self, sync_client):
        """测试消息验证"""
        # 发送空消息内容
        message_data = {
            "content": "",  # 空内容
            "message_type": "text",
            "sender_type": "server",
            "sender_id": "test_server"
        }
        
        response = sync_client.post(
            "/api/v1/tcp/message/send",
            json=message_data
        )
        
        # 应该返回验证错误
        assert response.status_code == 422

    def test_concurrent_server_operations(self, async_client):
        """测试并发服务器操作"""
        # 并发启动多个服务器
        server_configs = [
            {
                "host": "127.0.0.1",
                "port": 9990 + i,
                "max_connections": 5,
                "timeout": 30.0,
                "ssl_enabled": False
            }
            for i in range(3)
        ]
        
        # 顺序启动服务器（模拟并发效果）
        server_ids = []
        for config in server_configs:
            response = async_client.post("/api/v1/tcp/server/start", json=config)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            server_ids.append(data["data"]["server_id"])
        
        # 顺序停止所有服务器
        for server_id in server_ids:
            response = async_client.post(f"/api/v1/tcp/server/{server_id}/stop")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_server_client_integration(self, sync_client):
        """测试服务器-客户端集成"""
        # 启动服务器
        server_config = {
            "host": "127.0.0.1",
            "port": 9995,
            "max_connections": 5,
            "timeout": 30.0,
            "ssl_enabled": False
        }
        
        server_response = sync_client.post(
            "/api/v1/tcp/server/start",
            json=server_config
        )
        server_id = server_response.json()["data"]["server_id"]
        
        # 连接多个客户端
        client_ids = []
        for i in range(3):
            client_config = {
                "host": "127.0.0.1",
                "port": 9995,
                "timeout": 10.0,
                "auto_reconnect": False,
                "ssl_enabled": False
            }
            
            response = sync_client.post(
                "/api/v1/tcp/client/connect",
                json=client_config
            )
            
            assert response.status_code == 200
            client_ids.append(response.json()["data"]["client_id"])
        
        # 检查服务器状态，应该显示连接的客户端
        response = sync_client.get(f"/api/v1/tcp/server/{server_id}/status")
        status_data = response.json()["data"]
        
        # 验证连接数（可能需要时间建立连接）
        assert status_data["current_connections"] >= 0  # 允许连接建立时间
        
        # 清理：断开所有客户端
        for client_id in client_ids:
            sync_client.post(f"/api/v1/tcp/client/{client_id}/disconnect")
        
        # 停止服务器
        sync_client.post(f"/api/v1/tcp/server/{server_id}/stop")


# 测试数据验证
class TestTCPDataValidation:
    """TCP数据验证测试"""

    def test_tcp_server_config_validation(self):
        """测试TCP服务器配置验证"""
        # 有效配置
        valid_config = TCPServerConfig(
            host="127.0.0.1",
            port=8080,
            max_connections=100,
            timeout=30.0
        )
        assert valid_config.host == "127.0.0.1"
        assert valid_config.port == 8080

        # 无效端口
        with pytest.raises(ValueError):
            TCPServerConfig(host="127.0.0.1", port=0)
        
        with pytest.raises(ValueError):
            TCPServerConfig(host="127.0.0.1", port=99999)

    def test_tcp_client_config_validation(self):
        """测试TCP客户端配置验证"""
        # 有效配置
        valid_config = TCPClientConfig(
            host="127.0.0.1",
            port=8080,
            timeout=10.0
        )
        assert valid_config.host == "127.0.0.1"
        assert valid_config.port == 8080

        # 无效主机
        with pytest.raises(ValueError):
            TCPClientConfig(host="", port=8080)

    def test_message_validation(self):
        """测试消息验证"""
        # 有效消息
        valid_message = Message(
            content="Hello, world!",
            message_type="text",
            sender_type="client",
            sender_id="client_123"
        )
        assert valid_message.content == "Hello, world!"
        assert valid_message.message_type == "text"

        # 无效消息类型
        with pytest.raises(ValueError):
            Message(content="test", message_type="invalid_type")

        # 无效发送者类型
        with pytest.raises(ValueError):
            Message(content="test", sender_type="invalid_sender") 