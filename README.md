# 网络安全工具平台-Ming

> 基于Python FastAPI + Vue.js 3 + PySide6的多端网络安全工具平台(待完成doge)

## 🚀 项目简介

网络安全工具平台是一个集成端口扫描、PING监控、TCP通信功能的现代化网络安全解决方案。采用严格的TDD开发方法论，确保代码质量和可靠性。

### ✨ 核心功能

- **🔍 端口扫描**: 高性能多线程端口扫描器，支持TCP/UDP协议
- **📡 PING监控**: 实时网络质量监控和延迟分析
- **🔗 TCP通信**: 安全的TCP服务器/客户端通信实验室
- **📊 实时可视化**: Vue.js前端提供实时数据展示
- **🖥️ 桌面客户端**: PySide6跨平台桌面应用
- **⚡ REST API**: 完整的RESTful API接口

### 🏗️ 技术架构

- **后端**: Python 3.11+ + FastAPI + SQLAlchemy + Redis + Celery
- **前端**: Vue.js 3 + TypeScript + Element Plus + Vite
- **桌面**: PySide6 + QtQuick
- **工具链**: uv + ruff + mypy + pytest

## 🛠️ 开发环境设置

### 环境要求

- Python 3.11+
- Node.js 18+ (前端开发)
- Redis (可选，用于任务队列)

### 快速开始

1. **克隆项目**
   ```bash
   git clone https://github.com/lgnorant-lu/MingNetTools.git
   cd MingNetTools
   ```

2. **安装依赖管理工具**
   ```bash
   # 安装pipx (如果未安装)
   pip install pipx
   pipx ensurepath
   
   # 安装uv
   pipx install uv
   ```

3. **安装项目依赖**
   ```bash
   # 同步所有依赖并创建虚拟环境
   uv sync
   
   # 激活虚拟环境
   source .venv/bin/activate  # Linux/macOS
   .venv/Scripts/activate     # Windows
   ```

4. **运行测试**
   ```bash
   # 运行所有测试
   uv run pytest
   
   # 运行测试并生成覆盖率报告
   uv run pytest --cov
   ```

5. **启动开发服务器**
   ```bash
   # 启动FastAPI后端 (默认端口: 8000)
   uv run uvicorn backend.app.main:app --reload
   
   # 启动前端开发服务器 (端口: 3000)
   cd frontend && npm run dev
   ```

## 📁 项目结构

```
MingNetTools/
├── backend/          # FastAPI后端服务
├── frontend/         # Vue.js前端应用
├── desktop_client/   # PySide6桌面客户端
├── cli_tools/        # 命令行工具
├── tests/           # 集成测试
├── docs/            # 项目文档
└── deployment/      # 部署配置
```

## 🧪 测试驱动开发

项目采用严格的TDD方法论：

- **单元测试覆盖率**: > 90%
- **集成测试**: API端点完整测试
- **性能测试**: 网络工具性能基准测试
- **安全测试**: 代码安全扫描

```bash
# 运行不同类型的测试
uv run pytest tests/test_core/      # 核心功能测试
uv run pytest tests/test_api/       # API测试
uv run pytest -m "not slow"        # 跳过慢速测试
```

## 📚 文档

- [详细设计文档](Design.md)
- [项目结构说明](Structure.md)
- [开发进程追踪](Thread.md)
- [API文档](http://localhost:8000/docs) (开发服务器启动后可访问)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 编写测试并确保通过
4. 提交更改: `git commit -am 'Add new feature'`
5. 推送到分支: `git push origin feature/new-feature`
6. 提交Pull Request

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🎯 开发状态

- ✅ 核心网络工具模块 (100% 测试覆盖率)
- ✅ API框架架构 (100% 完成)
- ⏳ API端点功能集成 (90%+ 完成率)
- 📋 前端界面开发 (部分完成)
- 📋 桌面客户端 (计划中)

---

**维护者**: Ignorant-lu  
**最后更新**: 2025-05-25
