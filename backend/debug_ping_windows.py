#!/usr/bin/env python3
"""
Windows PING输出格式调试脚本
"""

import subprocess
import re
import asyncio

async def test_windows_ping():
    """测试Windows PING命令输出格式"""
    
    # 执行PING命令
    cmd = ["ping", "-n", "1", "-w", "3000", "baidu.com"]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    print("=== PING命令执行结果 ===")
    print(f"返回码: {process.returncode}")
    print(f"STDOUT:")
    output = stdout.decode('utf-8', errors='ignore')
    print(output)
    print(f"\nSTDERR:")
    print(stderr.decode('utf-8', errors='ignore'))
    
    # 测试各种正则表达式模式
    patterns = [
        r'时间[<=](\d+)ms',
        r'time[<=](\d+)ms', 
        r'最短\s*=\s*(\d+)ms',
        r'Minimum\s*=\s*(\d+)ms',
        r'来自.*?(\d+)ms',
        r'Reply.*?(\d+)ms',
        r'(\d+)ms',  # 简单匹配任何数字+ms
    ]
    
    print("\n=== 正则表达式测试 ===")
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, output)
        if match:
            print(f"模式 {i+1} 匹配: {pattern} -> {match.groups()}")
        else:
            print(f"模式 {i+1} 无匹配: {pattern}")
    
    # TTL测试
    ttl_pattern = r'TTL=(\d+)'
    ttl_match = re.search(ttl_pattern, output, re.IGNORECASE)
    if ttl_match:
        print(f"\nTTL匹配: {ttl_match.group(1)}")
    else:
        print(f"\nTTL无匹配")
    
    # 检查成功指示
    success_indicators = [
        "丢失 = 0",
        "loss = 0", 
        "已接收 = 1",
        "received = 1",
        "0% 丢失",
        "0% loss",
        "0%",
        "ѽ = 1",  # 中文乱码版本的"已接收 = 1"
        "ʧ = 0",  # 中文乱码版本的"丢失 = 0" 
        "0% ʧ",   # 中文乱码版本的"0% 丢失"
    ]
    
    print(f"\n=== 成功指示检查 ===")
    for indicator in success_indicators:
        if indicator in output:
            print(f"找到成功指示: {indicator}")
    
    # 检查输出中的关键词
    print(f"\n=== 输出分析 ===")
    print(f"输出长度: {len(output)}")
    print(f"包含'0%': {'0%' in output}")
    print(f"包含'ʧ': {'ʧ' in output}")
    print(f"包含'ѽ': {'ѽ' in output}")
    
    # 显示原始字节
    print(f"\n=== 原始字节 ===")
    raw_bytes = stdout[:100]  # 前100字节
    print(f"原始字节: {raw_bytes}")
    
    # 尝试不同编码
    print(f"\n=== 编码测试 ===")
    for encoding in ['utf-8', 'gbk', 'cp936', 'ascii']:
        try:
            decoded = stdout.decode(encoding, errors='ignore')
            print(f"{encoding}: {decoded[:50]}...")
        except Exception as e:
            print(f"{encoding}: 解码失败 - {e}")

if __name__ == "__main__":
    asyncio.run(test_windows_ping()) 