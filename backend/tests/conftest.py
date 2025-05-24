"""
---------------------------------------------------------------
File name:                  conftest.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                pytest测试配置文件，定义共享的fixture和测试设置
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
                            2025/05/23: 添加FastAPI TestClient fixtures;
----
"""

import asyncio
import os
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient


# 设置测试环境变量
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

# 配置pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

# 修复pytest-asyncio配置
def pytest_configure(config):
    """pytest配置函数
    
    在pytest启动时进行配置设置。
    
    Args:
        config: pytest配置对象
    """
    # 设置asyncio默认fixture循环范围
    config.option.asyncio_default_fixture_loop_scope = "function"
    
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "slow: 标记运行较慢的测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "unit: 标记单元测试"
    )
    config.addinivalue_line(
        "markers", "network: 标记需要网络访问的测试"
    )
    config.addinivalue_line(
        "markers", "privileged: 标记需要特殊权限的测试"
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建用于整个测试会话的事件循环
    
    这个fixture确保所有异步测试都使用同一个事件循环，
    避免在测试过程中出现事件循环相关的问题。
    
    Yields:
        asyncio.AbstractEventLoop: 测试会话的事件循环
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_socket():
    """模拟socket对象的fixture
    
    创建一个mock socket对象，用于测试网络相关功能
    而不实际进行网络连接。
    
    Returns:
        Mock: 模拟的socket对象
    """
    mock_sock = Mock()
    mock_sock.connect = Mock()
    mock_sock.settimeout = Mock()
    mock_sock.close = Mock()
    mock_sock.getsockname = Mock(return_value=("127.0.0.1", 12345))
    mock_sock.getpeername = Mock(return_value=("127.0.0.1", 80))
    return mock_sock


@pytest.fixture
async def mock_asyncio_open_connection():
    """模拟asyncio.open_connection的fixture
    
    创建模拟的异步连接，用于测试异步网络操作
    而不进行实际的网络连接。
    
    Returns:
        tuple: (mock_reader, mock_writer)的元组
    """
    mock_reader = AsyncMock()
    mock_writer = Mock()
    mock_writer.write = Mock()
    mock_writer.drain = AsyncMock()
    mock_writer.close = Mock()
    mock_writer.wait_closed = AsyncMock()
    
    return mock_reader, mock_writer


@pytest.fixture
def sample_hosts():
    """提供测试用的主机列表
    
    Returns:
        list: 测试主机地址列表
    """
    return [
        "127.0.0.1",
        "localhost", 
        "192.168.1.1",
        "8.8.8.8"
    ]


@pytest.fixture
def sample_ports():
    """提供测试用的端口列表
    
    Returns:
        list: 测试端口列表
    """
    return [22, 23, 25, 53, 80, 110, 443, 993, 995]


@pytest.fixture
def sample_port_ranges():
    """提供测试用的端口范围列表
    
    Returns:
        list: 端口范围字典列表
    """
    return [
        {"start": 80, "end": 80},
        {"start": 443, "end": 443},
        {"start": 22, "end": 25},
        {"start": 8000, "end": 8010}
    ]


@pytest.fixture
def mock_ping_response():
    """模拟PING响应的fixture
    
    Returns:
        dict: 模拟的PING响应数据
    """
    return {
        "host": "8.8.8.8",
        "success": True,
        "response_time": 23.5,
        "ttl": 64,
        "packet_size": 64,
        "sequence": 1
    }


@pytest.fixture
def mock_scan_result():
    """模拟扫描结果的fixture
    
    Returns:
        dict: 模拟的扫描结果数据
    """
    return {
        "host": "192.168.1.1",
        "port": 80,
        "protocol": "tcp",
        "status": "open",
        "service_name": "http",
        "response_time": 0.025,
        "banner": "Apache/2.4.41"
    }


@pytest.fixture
async def mock_tcp_server():
    """模拟TCP服务器的fixture
    
    创建一个模拟的TCP服务器实例，用于测试客户端连接功能。
    
    Returns:
        Mock: 模拟的TCP服务器对象
    """
    server = Mock()
    server.start = AsyncMock()
    server.stop = AsyncMock()
    server.clients = {}
    server.host = "127.0.0.1"
    server.port = 8888
    return server


@pytest.fixture
def timeout_config():
    """提供超时配置的fixture
    
    Returns:
        dict: 超时配置字典
    """
    return {
        "connect_timeout": 3.0,
        "read_timeout": 5.0,
        "ping_timeout": 5.0,
        "scan_timeout": 3.0
    }


@pytest.fixture(scope="function")
def sync_client() -> Generator[TestClient, None, None]:
    """同步测试客户端fixture
    
    创建一个TestClient实例，用于测试HTTP API端点。
    
    Yields:
        TestClient: FastAPI测试客户端
    """
    from app.main import app
    
    # 使用真实的FastAPI应用
    with TestClient(app) as client:
        yield client


# @pytest.fixture
# async def async_client() -> AsyncGenerator[AsyncClient, None]:
#     """异步测试客户端fixture
#     
#     创建一个异步HTTP客户端，用于测试异步API功能。
#     
#     Yields:
#         AsyncClient: 异步HTTP客户端
#     """
#     from app.main import app
#     
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client


@pytest.fixture
def performance_test_config():
    """性能测试配置fixture
    
    Returns:
        dict: 性能测试配置
    """
    return {
        "concurrent_requests": 10,
        "timeout_threshold": 1.0,
        "success_rate_threshold": 0.95,
        "max_response_time": 0.5
    }


def pytest_collection_modifyitems(config, items):
    """修改测试项目收集
    
    根据测试环境自动跳过某些测试。
    
    Args:
        config: pytest配置对象
        items: 收集到的测试项目列表
    """
    # 在CI环境中跳过需要特殊权限的测试
    if os.environ.get("CI"):
        skip_privileged = pytest.mark.skip(
            reason="跳过需要特殊权限的测试 (CI环境)"
        )
        for item in items:
            if "privileged" in item.keywords:
                item.add_marker(skip_privileged)
    
    # 如果没有网络连接，跳过网络测试
    # TODO: 添加网络连接检查逻辑 