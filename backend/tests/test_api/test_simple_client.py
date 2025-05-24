"""
简单TestClient测试 - 用于诊断协程问题
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import time


def test_simple_testclient():
    """最简单的TestClient测试，不依赖任何fixture"""
    
    # 创建简单FastAPI应用
    app = FastAPI(title="Simple Test App", version="1.0.0")
    
    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "version": "1.0.0", 
            "timestamp": time.time()
        }
    
    # 创建TestClient
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


def test_simple_testclient_without_context():
    """不使用上下文管理器的TestClient测试"""
    
    # 创建简单FastAPI应用
    app = FastAPI(title="Simple Test App 2", version="1.0.0")
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test successful"}
    
    # 不使用上下文管理器
    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "test successful" 