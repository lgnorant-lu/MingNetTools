"""
TCP API调试测试
"""

import pytest
import asyncio
import time
import sys
import os
from fastapi.testclient import TestClient

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_path)

from app.main import create_app


def test_tcp_server_only():
    """仅测试TCP服务器启动和停止"""
    app = create_app()
    with TestClient(app) as client:
        # 启动服务器
        server_config = {
            "host": "127.0.0.1",
            "port": 9998,
            "max_connections": 5,
            "timeout": 30.0,
            "ssl_enabled": False
        }
        
        response = client.post("/api/v1/tcp/server/start", json=server_config)
        print(f"Server start response: {response.status_code}")
        print(f"Server start data: {response.json()}")
        
        assert response.status_code == 200
        server_id = response.json()["data"]["server_id"]
        
        # 等待服务器完全启动
        time.sleep(1)
        
        # 检查服务器状态
        status_response = client.get(f"/api/v1/tcp/server/{server_id}/status")
        print(f"Server status response: {status_response.status_code}")
        print(f"Server status data: {status_response.json()}")
        
        # 停止服务器
        stop_response = client.post(f"/api/v1/tcp/server/{server_id}/stop")
        print(f"Server stop response: {stop_response.status_code}")
        print(f"Server stop data: {stop_response.json()}")


def test_tcp_client_connection_debug():
    """调试TCP客户端连接"""
    app = create_app()
    with TestClient(app) as client:
        # 启动服务器
        server_config = {
            "host": "127.0.0.1",
            "port": 9997,
            "max_connections": 5,
            "timeout": 30.0,
            "ssl_enabled": False
        }
        
        server_response = client.post("/api/v1/tcp/server/start", json=server_config)
        print(f"Server start: {server_response.status_code}, {server_response.json()}")
        
        if server_response.status_code != 200:
            pytest.skip("服务器启动失败")
        
        server_id = server_response.json()["data"]["server_id"]
        
        # 等待服务器完全启动
        time.sleep(2)
        
        # 验证服务器正在运行
        status_response = client.get(f"/api/v1/tcp/server/{server_id}/status")
        print(f"Server status: {status_response.status_code}, {status_response.json()}")
        
        # 尝试连接客户端
        client_config = {
            "host": "127.0.0.1",
            "port": 9997,
            "timeout": 10.0,
            "auto_reconnect": False,
            "ssl_enabled": False
        }
        
        print(f"Attempting client connection with config: {client_config}")
        
        try:
            client_response = client.post("/api/v1/tcp/client/connect", json=client_config)
            print(f"Client connect response: {client_response.status_code}")
            print(f"Client connect text: {client_response.text}")
            
            if client_response.status_code == 200:
                data = client_response.json()
                print(f"Client connect data: {data}")
                client_id = data["data"]["client_id"]
                
                # 断开客户端
                disconnect_response = client.post(f"/api/v1/tcp/client/{client_id}/disconnect")
                print(f"Client disconnect: {disconnect_response.status_code}, {disconnect_response.json()}")
            
        except Exception as e:
            print(f"Client connection error: {e}")
        
        # 清理：停止服务器
        stop_response = client.post(f"/api/v1/tcp/server/{server_id}/stop")
        print(f"Server cleanup: {stop_response.status_code}, {stop_response.json()}")


if __name__ == "__main__":
    test_tcp_server_only()
    print("\n" + "="*50 + "\n")
    test_tcp_client_connection_debug() 