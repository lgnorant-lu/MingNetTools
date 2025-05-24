#!/usr/bin/env python3
"""
---------------------------------------------------------------
File name:                  run_stable.py
Author:                     Ignorant-lu
Date created:               2025/05/24
Description:                稳定启动脚本，禁用自动重载以保持WebSocket连接稳定
----------------------------------------------------------------

Changed history:            
                            2025/05/24: 初始创建;
----
"""

import uvicorn
import os
import sys

# 添加app目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 强制设置环境变量以禁用重载
    os.environ["RELOAD"] = "false"
    
    print("🚀 启动网络安全工具平台 (稳定模式)")
    print("📝 自动重载已禁用，WebSocket连接将保持稳定")
    print("🔧 如需修改代码，请手动重启服务器")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 强制禁用重载
        log_level="info",
        access_log=True,
    ) 