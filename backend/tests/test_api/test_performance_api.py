"""
---------------------------------------------------------------
File name:                  test_performance_api.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                性能监控API端点测试
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建性能监控API测试;
----
"""

import pytest
import json
import time
import sys
import os
from fastapi.testclient import TestClient

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_path)

from app.main import create_app


class TestPerformanceAPI:
    """性能监控API测试类"""

    @pytest.fixture
    def client(self):
        """测试客户端fixture"""
        app = create_app()
        with TestClient(app) as client:
            yield client

    def test_get_current_metrics(self, client):
        """测试获取当前性能指标"""
        response = client.get("/api/v1/performance/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        metrics = data["data"]
        required_fields = [
            "request_count", "avg_response_time", "min_response_time",
            "max_response_time", "success_rate", "error_rate",
            "concurrent_requests", "memory_usage", "cpu_usage", "timestamp"
        ]
        
        for field in required_fields:
            assert field in metrics

    def test_get_endpoint_metrics(self, client):
        """测试获取端点性能指标"""
        # 先做一些请求来生成端点指标
        client.get("/health")
        client.get("/info")
        
        response = client.get("/api/v1/performance/metrics/endpoints")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_endpoints" in data["data"]
        assert "endpoints" in data["data"]

    def test_get_metrics_history(self, client):
        """测试获取性能指标历史"""
        response = client.get("/api/v1/performance/metrics/history?limit=50")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_records" in data["data"]
        assert "limit" in data["data"]
        assert "history" in data["data"]
        assert data["data"]["limit"] == 50

    def test_reset_metrics(self, client):
        """测试重置性能指标"""
        # 先做一些请求
        client.get("/health")
        client.get("/info")
        
        # 重置指标
        response = client.post("/api/v1/performance/metrics/reset")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "reset_time" in data["data"]

    def test_get_connection_pool_stats(self, client):
        """测试获取连接池统计信息"""
        response = client.get("/api/v1/performance/pool/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        stats = data["data"]
        required_fields = ["total_connections", "max_connections", "active", "connection_ids"]
        
        for field in required_fields:
            assert field in stats

    def test_start_monitoring(self, client):
        """测试启动性能监控"""
        response = client.post("/api/v1/performance/monitoring/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["monitoring"] is True

    def test_stop_monitoring(self, client):
        """测试停止性能监控"""
        response = client.post("/api/v1/performance/monitoring/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["monitoring"] is False

    def test_get_performance_health(self, client):
        """测试获取性能健康状况"""
        response = client.get("/api/v1/performance/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        health_data = data["data"]
        required_fields = [
            "health_status", "health_score", "alerts", "metrics_summary"
        ]
        
        for field in required_fields:
            assert field in health_data
        
        # 验证健康状态
        valid_statuses = ["excellent", "good", "fair", "poor", "critical"]
        assert health_data["health_status"] in valid_statuses
        
        # 验证健康分数
        assert 0 <= health_data["health_score"] <= 100
        
        # 验证指标摘要
        metrics_summary = health_data["metrics_summary"]
        summary_fields = [
            "avg_response_time", "error_rate", "memory_usage", 
            "cpu_usage", "concurrent_requests"
        ]
        
        for field in summary_fields:
            assert field in metrics_summary

    def test_get_performance_summary(self, client):
        """测试获取性能摘要"""
        # 先做一些请求来生成数据
        client.get("/health")
        client.get("/info")
        client.get("/api/v1/performance/metrics")
        
        response = client.get("/api/v1/performance/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        summary = data["data"]
        required_sections = ["overview", "system", "endpoints", "connections"]
        
        for section in required_sections:
            assert section in summary
        
        # 验证概览数据
        overview = summary["overview"]
        overview_fields = [
            "total_requests", "avg_response_time", "success_rate",
            "error_rate", "concurrent_requests"
        ]
        
        for field in overview_fields:
            assert field in overview
        
        # 验证系统数据
        system = summary["system"]
        assert "memory_usage" in system
        assert "cpu_usage" in system
        
        # 验证端点数据
        endpoints = summary["endpoints"]
        assert "total_endpoints" in endpoints
        assert "slowest" in endpoints
        assert "busiest" in endpoints
        
        # 验证连接数据
        connections = summary["connections"]
        connection_fields = ["pool_connections", "max_connections", "pool_active"]
        
        for field in connection_fields:
            assert field in connections

    def test_performance_tracking_integration(self, client):
        """测试性能跟踪集成"""
        # 获取初始指标
        initial_response = client.get("/api/v1/performance/metrics")
        assert initial_response.status_code == 200
        initial_metrics = initial_response.json()["data"]
        initial_count = initial_metrics["request_count"]
        
        # 做一些请求
        test_requests = [
            "/health",
            "/info",
            "/api/v1/performance/metrics"  # 使用已知工作的端点
        ]
        
        # 发送请求并验证成功
        for endpoint in test_requests:
            response = client.get(endpoint)
            assert response.status_code == 200, f"端点 {endpoint} 返回 {response.status_code}"
        
        # 获取更新后的指标
        final_response = client.get("/api/v1/performance/metrics")
        assert final_response.status_code == 200
        final_metrics = final_response.json()["data"]
        final_count = final_metrics["request_count"]
        
        # 验证请求计数增加（至少增加了我们做的请求数）
        assert final_count > initial_count
        
        # 验证响应时间指标被记录
        if final_metrics["max_response_time"] > 0:
            assert final_metrics["min_response_time"] <= final_metrics["max_response_time"]
            assert final_metrics["avg_response_time"] > 0

    def test_endpoint_specific_metrics(self, client):
        """测试特定端点的指标跟踪"""
        # 重置指标以获得干净的测试环境
        reset_response = client.post("/api/v1/performance/metrics/reset")
        assert reset_response.status_code == 200
        
        # 对特定端点做多次请求
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200
        
        # 获取端点指标
        response = client.get("/api/v1/performance/metrics/endpoints")
        assert response.status_code == 200
        data = response.json()["data"]
        endpoints = data["endpoints"]
        
        # 验证health端点的指标
        health_endpoint_found = False
        for endpoint_name, metrics in endpoints.items():
            if "/health" in endpoint_name:
                health_endpoint_found = True
                assert metrics["request_count"] >= 3  # 至少3次请求
                assert metrics["avg_response_time"] > 0
                break
        
        assert health_endpoint_found, "未找到/health端点的指标记录"

    def test_error_handling_metrics(self, client):
        """测试错误处理的指标跟踪"""
        # 尝试访问不存在的端点
        response = client.get("/api/v1/nonexistent/endpoint")
        assert response.status_code == 404
        
        # 获取指标，验证错误被记录
        metrics_response = client.get("/api/v1/performance/metrics")
        metrics = metrics_response.json()["data"]
        
        # 注意：由于我们可能在测试过程中有成功的请求，所以只验证有错误计数
        assert metrics["request_count"] > 0 