# 项目结构文档

## 项目概览
- **项目名称**: 网络安全工具平台 (Network Security Platform)
- **最后更新**: 2025-05-23
- **版本**: v0.1.0-dev
- **技术栈**: Python + FastAPI + Vue.js + PySide6

## 根目录结构

```
network_security_platform/
├── backend/                    # 后端API服务 [计划中]
├── frontend/                  # Vue.js前端 [计划中]
├── desktop_client/            # PySide6桌面客户端 [计划中]
├── cli_tools/                 # 命令行工具 [计划中]
├── deployment/                # 部署配置 [计划中]
├── docs/                      # 项目文档 [计划中]
├── tests/                     # 集成测试 [计划中]
├── logs/                      # 日志目录 [计划中]
├── data/                      # 数据目录 [计划中]
├── config/                    # 配置文件 [计划中]
├── .github/                   # GitHub Actions工作流 [计划中]
├── .vscode/                   # VS Code配置 [计划中]
├── Structure.md               # 项目结构文档 [已完成]
├── Thread.md                  # 任务进程文档 [进行中]
├── Design.md                  # 设计文档 [计划中]
├── Log.md                     # 变更日志索引 [计划中]
├── Issues.md                  # 问题追踪 [计划中]
├── Diagram.md                 # 绘图日志索引 [计划中]
├── Plan.md                    # 详细实施计划 [已完成]
├── README.md                  # 项目说明 [计划中]
├── CONTRIBUTING.md            # 贡献指南 [计划中]
├── SECURITY.md               # 安全政策 [计划中]
├── LICENSE                   # 开源许可证 [计划中]
├── pyproject.toml            # UV根项目配置 [计划中]
├── uv.lock                   # UV全局锁定文件 [计划中]
├── .gitignore                # Git忽略文件 [计划中]
├── .ruff.toml               # Ruff配置 [计划中]
├── mypy.ini                 # MyPy配置 [计划中]
├── .pre-commit-config.yaml  # Pre-commit钩子 [计划中]
└── docker-compose.yml        # 开发环境 [计划中]
```

## 详细模块结构

### 后端服务 (backend/)
```
backend/                      # 后端API服务 [计划中]
├── app/                      # 主应用目录
│   ├── __init__.py          # 应用初始化 [计划中]
│   ├── main.py              # FastAPI应用入口 [计划中]
│   ├── config.py            # 配置管理 [计划中]
│   ├── database.py          # 数据库连接 [计划中]
│   ├── models/              # 数据模型
│   │   ├── __init__.py      # 模型包初始化 [计划中]
│   │   ├── scan.py          # 扫描相关模型 [计划中]
│   │   ├── ping.py          # PING相关模型 [计划中]
│   │   └── connection.py    # 连接相关模型 [计划中]
│   ├── schemas/             # Pydantic模式
│   │   ├── __init__.py      # 模式包初始化 [计划中]
│   │   ├── scan.py          # 扫描请求/响应模式 [计划中]
│   │   ├── ping.py          # PING请求/响应模式 [计划中]
│   │   └── connection.py    # 连接请求/响应模式 [计划中]
│   ├── api/                 # API路由
│   │   ├── __init__.py      # API包初始化 [计划中]
│   │   └── v1/              # API v1版本
│   │       ├── __init__.py  # v1包初始化 [计划中]
│   │       ├── scan.py      # 扫描API端点 [计划中]
│   │       ├── ping.py      # PING API端点 [计划中]
│   │       ├── connection.py # 连接API端点 [计划中]
│   │       └── websocket.py # WebSocket端点 [计划中]
│   ├── core/                # 核心网络工具
│   │   ├── __init__.py      # 核心包初始化 [计划中]
│   │   ├── port_scanner.py  # 端口扫描核心引擎 [计划中]
│   │   ├── ping_tool.py     # PING工具核心引擎 [计划中]
│   │   ├── tcp_server.py    # TCP服务器核心 [计划中]
│   │   ├── tcp_client.py    # TCP客户端核心 [计划中]
│   │   └── network_utils.py # 网络工具函数库 [计划中]
│   ├── services/            # 业务逻辑服务
│   │   ├── __init__.py      # 服务包初始化 [计划中]
│   │   ├── scan_service.py  # 扫描业务逻辑 [计划中]
│   │   ├── ping_service.py  # PING业务逻辑 [计划中]
│   │   └── connection_service.py # 连接业务逻辑 [计划中]
│   ├── utils/               # 工具函数
│   │   ├── __init__.py      # 工具包初始化 [计划中]
│   │   ├── logger.py        # 日志配置 [计划中]
│   │   ├── security.py      # 安全工具 [计划中]
│   │   └── validators.py    # 验证器 [计划中]
│   └── tasks/               # Celery任务
│       ├── __init__.py      # 任务包初始化 [计划中]
│       ├── scan_tasks.py    # 扫描异步任务 [计划中]
│       └── ping_tasks.py    # PING异步任务 [计划中]
├── alembic/                 # 数据库迁移
│   ├── env.py              # Alembic环境配置 [计划中]
│   ├── script.py.mako      # 迁移脚本模板 [计划中]
│   └── versions/           # 迁移版本文件 [计划中]
├── tests/                   # 后端测试 (TDD)
│   ├── __init__.py         # 测试包初始化 [计划中]
│   ├── conftest.py         # Pytest配置 [计划中]
│   ├── test_core/          # 核心功能测试
│   │   ├── test_port_scanner.py # 端口扫描测试 [计划中]
│   │   ├── test_ping_tool.py    # PING工具测试 [计划中]
│   │   └── test_tcp_comm.py     # TCP通信测试 [计划中]
│   ├── test_api/           # API测试
│   │   ├── test_scan_api.py     # 扫描API测试 [计划中]
│   │   ├── test_ping_api.py     # PING API测试 [计划中]
│   │   └── test_connection_api.py # 连接API测试 [计划中]
│   └── test_services/      # 服务层测试
│       ├── test_scan_service.py # 扫描服务测试 [计划中]
│       └── test_ping_service.py # PING服务测试 [计划中]
├── pyproject.toml          # UV项目配置 [计划中]
├── uv.lock                 # UV锁定文件 [计划中]
├── Dockerfile              # Docker构建文件 [计划中]
└── docker-compose.yml      # 开发环境配置 [计划中]
```

### 前端应用 (frontend/)
```
frontend/                    # Vue.js前端 [已完成]
├── public/                  # 静态资源
│   ├── index.html          # HTML模板 [已完成]
│   └── favicon.ico         # 网站图标 [已完成]
├── src/                     # 源代码
│   ├── components/         # Vue组件
│   │   ├── common/         # 通用组件
│   │   │   ├── AppHeader.vue    # 应用头部 [已完成]
│   │   │   ├── AppSidebar.vue   # 侧边栏 [已完成]
│   │   │   └── LoadingSpinner.vue # 加载动画 [已完成]
│   │   ├── scan/           # 扫描相关组件
│   │   │   ├── ScanForm.vue     # 扫描配置表单 [已完成]
│   │   │   ├── ScanResults.vue  # 扫描结果展示 [已完成]
│   │   │   └── ScanProgress.vue # 扫描进度 [已完成]
│   │   ├── ping/           # PING相关组件
│   │   │   ├── PingForm.vue     # PING配置表单 [已完成]
│   │   │   ├── PingChart.vue    # PING图表 [已完成]
│   │   │   └── PingStats.vue    # PING统计 [已完成]
│   │   └── connection/     # 连接相关组件
│   │       ├── ServerPanel.vue  # 服务器控制面板 [已完成]
│   │       ├── ClientPanel.vue  # 客户端面板 [已完成]
│   │       └── MessageList.vue  # 消息列表 [待完善]
│   ├── views/              # 页面视图
│   │   ├── DashboardView.vue   # 仪表板页面 [已完成]
│   │   ├── ScanToolsView.vue   # 扫描工具页面 [已完成]
│   │   ├── PingMonitorView.vue # PING监控页面 [已完成]
│   │   └── ConnectionLabView.vue # 连接实验室页面 [基本完成]
│   ├── stores/             # Pinia状态管理
│   │   ├── index.ts        # 状态管理入口 [已完成]
│   │   ├── dashboard.ts    # 仪表板状态 [已完成]
│   │   ├── scan.ts         # 扫描状态 [已完成]
│   │   ├── ping.ts         # PING状态 [已完成]
│   │   └── connection.ts   # 连接状态 [已完成]
│   ├── api/                # API调用
│   │   ├── client.ts       # API客户端配置 [已完成]
│   │   ├── scan.ts         # 扫描API [已完成]
│   │   ├── ping.ts         # PING API [已完成]
│   │   └── connection.ts   # 连接API [已完成]
│   ├── utils/              # 工具函数
│   │   ├── index.ts        # 工具函数入口 [已完成]
│   │   ├── format.ts       # 格式化工具 [已完成]
│   │   └── websocket.ts    # WebSocket工具 [已完成]
│   ├── router/             # 路由配置
│   │   └── index.ts        # 路由定义 [已完成]
│   ├── App.vue             # 根组件 [已完成]
│   └── main.ts             # 应用入口 [已完成]
├── package.json            # NPM配置 [已完成]
├── vite.config.ts          # Vite配置 [已完成]
├── tsconfig.json           # TypeScript配置 [已完成]
└── Dockerfile              # Docker构建文件 [计划中]
```

### 桌面客户端 (desktop_client/)
```
desktop_client/              # PySide6桌面客户端 [计划中]
├── src/                     # 源代码
│   ├── main.py             # 应用入口 [计划中]
│   ├── ui/                 # UI模块
│   │   ├── __init__.py     # UI包初始化 [计划中]
│   │   ├── main_window.py  # 主窗口 [计划中]
│   │   ├── scan_widget.py  # 扫描控件 [计划中]
│   │   ├── ping_widget.py  # PING控件 [计划中]
│   │   └── connection_widget.py # 连接控件 [计划中]
│   ├── qml/                # QML界面文件
│   │   ├── main.qml        # 主界面 [计划中]
│   │   ├── ScanView.qml    # 扫描视图 [计划中]
│   │   ├── PingView.qml    # PING视图 [计划中]
│   │   └── ConnectionView.qml # 连接视图 [计划中]
│   ├── api/                # API客户端
│   │   ├── __init__.py     # API包初始化 [计划中]
│   │   └── client.py       # HTTP客户端 [计划中]
│   ├── models/             # 数据模型
│   │   ├── __init__.py     # 模型包初始化 [计划中]
│   │   └── data.py         # 数据类定义 [计划中]
│   └── utils/              # 工具函数
│       ├── __init__.py     # 工具包初始化 [计划中]
│       └── helpers.py      # 助手函数 [计划中]
├── resources/              # 图标和资源文件
│   ├── icons/              # 图标文件 [计划中]
│   └── qml.qrc             # Qt资源文件 [计划中]
├── tests/                  # 桌面客户端测试 (TDD)
│   ├── __init__.py         # 测试包初始化 [计划中]
│   └── test_ui.py          # UI测试 [计划中]
├── pyproject.toml          # UV项目配置 [计划中]
└── build.py                # 构建脚本 [计划中]
```

### 命令行工具 (cli_tools/)
```
cli_tools/                   # 命令行工具 [计划中]
├── network_scanner.py      # 网络扫描CLI [计划中]
├── ping_monitor.py         # PING监控CLI [计划中]
├── tcp_tools.py            # TCP工具CLI [计划中]
├── tests/                  # CLI工具测试 (TDD)
│   ├── __init__.py         # 测试包初始化 [计划中]
│   ├── test_scanner.py     # 扫描工具测试 [计划中]
│   ├── test_ping.py        # PING工具测试 [计划中]
│   └── test_tcp.py         # TCP工具测试 [计划中]
└── pyproject.toml          # UV项目配置 [计划中]
```

## 状态标记说明
- **[已完成]**: 功能已实现并通过测试
- **[进行中]**: 当前正在开发中
- **[计划中]**: 已规划，等待开发
- **[待补全]**: 需要进一步完善的功能

## 依赖关系说明

### 模块间依赖
1. **frontend** → **backend**: HTTP API + WebSocket
2. **desktop_client** → **backend**: HTTP API
3. **cli_tools** → **backend**: HTTP API (可选，也可独立运行)
4. **backend/core** ← **backend/services** ← **backend/api**
5. **backend/models** ← **backend/services**

### 技术栈依赖
- **后端**: Python 3.11+ + FastAPI + SQLAlchemy + Redis + Celery
- **前端**: Node.js 18+ + Vue.js 3 + TypeScript + Vite
- **桌面**: Python 3.11+ + PySide6
- **工具**: uv + ruff + mypy + pytest

## 开发优先级
1. **阶段1**: 后端核心功能 (core模块) - TDD驱动
2. **阶段2**: 后端API接口 (api模块) - TDD驱动
3. **阶段3**: 前端基础界面 (views + components)
4. **阶段4**: 桌面客户端开发
5. **阶段5**: CLI工具开发
6. **阶段6**: 部署和优化 