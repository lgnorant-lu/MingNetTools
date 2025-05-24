"""
真实App TestClient测试 - 使用实际的app对象
"""

import pytest
from fastapi.testclient import TestClient


def test_real_app_testclient():
    """使用真实app对象的TestClient测试"""
    
    from app.main import app
    
    # 验证app对象类型
    assert app is not None
    assert callable(app)
    
    # 创建TestClient
    with TestClient(app) as client:
        # 测试健康检查端点
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime" in data
        assert "services" in data
        assert "environment" in data


def test_real_app_without_context():
    """不使用上下文管理器的真实app测试"""
    
    from app.main import app
    
    # 直接创建TestClient
    client = TestClient(app)
    
    # 测试根路径
    response = client.get("/")
    assert response.status_code in [200, 307]  # 可能是重定向
    
    # 测试API信息端点
    response = client.get("/info")
    if response.status_code == 200:
        data = response.json()
        assert "data" in data 