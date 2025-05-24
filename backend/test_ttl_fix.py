#!/usr/bin/env python3
"""
TTL解析测试脚本
"""

import subprocess
import re
import asyncio

async def test_ttl_parsing():
    """测试TTL解析"""
    
    # 执行PING命令
    cmd = ["ping", "-n", "1", "-w", "3000", "baidu.com"]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    print("=== PING TTL解析测试 ===")
    print(f"返回码: {process.returncode}")
    
    # 尝试不同编码
    for encoding in ['gbk', 'cp936', 'utf-8']:
        try:
            output = stdout.decode(encoding, errors='ignore')
            print(f"\n--- {encoding}编码输出 ---")
            print(output)
            
            # 测试TTL正则表达式
            ttl_patterns = [
                r'TTL=(\d+)',
                r'ttl=(\d+)',
                r'TTL\s*=\s*(\d+)',
                r'ttl\s*=\s*(\d+)',
                r'生存时间=(\d+)',  # 中文
                r'(?:TTL|ttl|生存时间)[:=\s]*(\d+)'  # 通用模式
            ]
            
            print(f"\n--- TTL解析测试 ({encoding}) ---")
            for i, pattern in enumerate(ttl_patterns):
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    print(f"模式 {i+1} 匹配: {pattern} -> TTL={match.group(1)}")
                else:
                    print(f"模式 {i+1} 无匹配: {pattern}")
            
            # 检查原始字节中的TTL信息
            print(f"\n--- 原始输出分析 ({encoding}) ---")
            lines = output.split('\n')
            for j, line in enumerate(lines):
                if 'TTL' in line.upper() or '生存时间' in line:
                    print(f"第{j+1}行包含TTL: {line.strip()}")
            
            break
            
        except Exception as e:
            print(f"{encoding}解码失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_ttl_parsing()) 