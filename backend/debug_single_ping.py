#!/usr/bin/env python3
"""
单次PING数据调试脚本
"""

import asyncio
import json
from app.core.ping_tool import PingEngine

async def debug_single_ping():
    """调试单次PING数据格式"""
    
    print("=== 单次PING数据调试 ===")
    
    # 创建PING引擎
    ping_engine = PingEngine()
    
    # 测试单次PING
    print("\n--- 测试单次PING ---")
    
    try:
        result = await ping_engine.ping_host("baidu.com")
        print(f"原始结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 检查关键字段
        print(f"\n--- 关键字段检查 ---")
        print(f"success: {result.get('success')} (类型: {type(result.get('success'))})")
        print(f"response_time: {result.get('response_time')} (类型: {type(result.get('response_time'))})")
        print(f"ttl: {result.get('ttl')} (类型: {type(result.get('ttl'))})")
        print(f"packet_size: {result.get('packet_size')} (类型: {type(result.get('packet_size'))})")
        print(f"timestamp: {result.get('timestamp')} (类型: {type(result.get('timestamp'))})")
        print(f"error_message: {result.get('error_message')} (类型: {type(result.get('error_message'))})")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(debug_single_ping()) 