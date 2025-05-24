"""
---------------------------------------------------------------
File name:                  conftest.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                API测试配置文件，定义共享的fixtures和测试设置
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
----
"""

import pytest
import asyncio
from typing import Dict, Any, AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建用于整个测试会话的事件循环"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def app():
    """创建FastAPI应用实例
    
    注意：此时应用尚未实现，这是TDD红阶段
    """
    # TDD红阶段：这将导致ImportError，因为我们还没有实现main.py
    try:
        from backend.app.main import app
        return app
    except ImportError:
        pytest.skip("FastAPI应用尚未实现")


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """创建异步HTTP测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sync_client(app) -> TestClient:
    """创建同步HTTP测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_scan_request() -> Dict[str, Any]:
    """提供测试用的扫描请求数据"""
    return {
        "target": "127.0.0.1",
        "ports": [80, 443, 22],
        "protocol": "tcp",
        "timeout": 3.0,
        "max_concurrent": 10
    }


@pytest.fixture
def sample_port_range_request() -> Dict[str, Any]:
    """提供测试用的端口范围扫描请求"""
    return {
        "target": "192.168.1.1",
        "start_port": 80,
        "end_port": 85,
        "protocol": "tcp",
        "timeout": 3.0
    }


@pytest.fixture
def sample_batch_scan_request() -> Dict[str, Any]:
    """提供测试用的批量扫描请求"""
    return {
        "targets": [
            {
                "host": "127.0.0.1",
                "ports": [80, 443],
                "protocol": "tcp"
            },
            {
                "host": "192.168.1.1", 
                "ports": [22, 23],
                "protocol": "tcp"
            }
        ],
        "timeout": 3.0,
        "max_concurrent": 20
    }


@pytest.fixture
def sample_ping_request() -> Dict[str, Any]:
    """提供测试用的PING请求数据"""
    return {
        "target": "8.8.8.8",
        "count": 4,
        "timeout": 5.0,
        "packet_size": 64
    }


@pytest.fixture
def sample_continuous_ping_request() -> Dict[str, Any]:
    """提供测试用的连续PING请求"""
    return {
        "target": "127.0.0.1",
        "duration": 10,
        "interval": 1.0,
        "timeout": 5.0
    }


@pytest.fixture
def sample_tcp_server_config() -> Dict[str, Any]:
    """提供测试用的TCP服务器配置"""
    return {
        "host": "127.0.0.1",
        "port": 0,  # 自动分配端口
        "max_connections": 100,
        "timeout": 300.0
    }


@pytest.fixture
def sample_tcp_client_config() -> Dict[str, Any]:
    """提供测试用的TCP客户端配置"""
    return {
        "server_host": "127.0.0.1",
        "server_port": 8888,
        "auto_reconnect": True,
        "heartbeat_interval": 30.0
    }


@pytest.fixture
def sample_message() -> Dict[str, Any]:
    """提供测试用的消息数据"""
    return {
        "type": "chat",
        "content": "Hello, this is a test message!",
        "target": None
    }


@pytest.fixture
def websocket_test_data() -> Dict[str, Any]:
    """提供WebSocket测试数据"""
    return {
        "connection_id": "test_connection_001",
        "message": {
            "type": "ping",
            "data": {"target": "127.0.0.1"}
        }
    }


@pytest.fixture
def api_error_scenarios():
    """提供API错误场景测试数据"""
    return {
        "invalid_ip": {
            "target": "invalid.ip.address",
            "ports": [80]
        },
        "invalid_port": {
            "target": "127.0.0.1",
            "ports": [99999]  # 无效端口
        },
        "missing_required": {
            "ports": [80]  # 缺少target字段
        },
        "invalid_protocol": {
            "target": "127.0.0.1",
            "ports": [80],
            "protocol": "invalid"
        }
    }


@pytest.fixture
def mock_scan_result():
    """提供模拟的扫描结果"""
    return {
        "host": "127.0.0.1",
        "port": 80,
        "protocol": "tcp",
        "status": "open",
        "response_time": 0.025,
        "service_name": "http",
        "banner": None
    }


@pytest.fixture
def mock_ping_result():
    """提供模拟的PING结果"""
    return {
        "host": "8.8.8.8",
        "ip_address": "8.8.8.8",
        "success": True,
        "response_time": 23.5,
        "ttl": 64,
        "packet_size": 64,
        "sequence": 1
    }


@pytest.fixture
def performance_test_config():
    """提供性能测试配置"""
    return {
        "concurrent_requests": 10,
        "request_count": 100,
        "timeout_threshold": 5.0,
        "success_rate_threshold": 0.95
    }


# pytest配置
def pytest_configure(config):
    """pytest配置函数"""
    config.addinivalue_line(
        "markers", "api: 标记API测试"
    )
    config.addinivalue_line(
        "markers", "websocket: 标记WebSocket测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "performance: 标记性能测试"
    ) 