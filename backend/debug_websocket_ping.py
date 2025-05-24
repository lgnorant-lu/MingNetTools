#!/usr/bin/env python3
"""
WebSocket PING数据调试脚本
"""

import asyncio
import json
from app.core.ping_tool import PingEngine

async def debug_ping_data():
    """调试PING数据格式"""
    
    print("=== WebSocket PING数据调试 ===")
    
    # 创建PING引擎
    ping_engine = PingEngine()
    
    # 测试连续PING
    print("\n--- 测试连续PING数据格式 ---")
    
    count = 0
    async for result in ping_engine.continuous_ping(host="baidu.com", duration=3):
        count += 1
        print(f"\n第{count}次PING结果:")
        print(f"原始结果: {result}")
        
        # 模拟WebSocket数据格式化
        ping_data = {
            "type": "ping_result",
            "target": "baidu.com",
            "sequence": result.get("sequence", 0),
            "success": result.get("success", False),
            "status": get_ping_status(result),  # 使用相同的状态映射
            "response_time": result.get("response_time"),
            "ttl": result.get("ttl"),
            "packet_size": result.get("packet_size", 32),
            "timestamp": result.get("timestamp", None),
            "error": result.get("error_message"),
            "error_message": result.get("error_message"),
            "error_type": result.get("error_type")
        }
        
        print(f"WebSocket格式: {json.dumps(ping_data, indent=2, ensure_ascii=False)}")
        
        if count >= 3:  # 只测试3次
            break

def get_ping_status(result):
    """复制WebSocket的状态映射逻辑"""
    if result.get("success", False):
        return "success"
    
    error_type = result.get("error_type", "")
    if error_type in ["timeout", "unreachable"]:
        return "timeout"
    elif error_type in ["name_resolution", "permission_denied"]:
        return "error"
    else:
        return "timeout"  # 默认为超时

if __name__ == "__main__":
    asyncio.run(debug_ping_data()) 