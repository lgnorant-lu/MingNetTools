# 变更日志索引

## 概述
本文档作为项目变更日志的索引，详细的变更记录分别存储在 `logs/` 目录下的对应模块文件中。

## 日志文件结构

```
logs/
├── core/                       # 核心功能变更日志
│   ├── port_scanner.md        # 端口扫描引擎变更记录
│   ├── ping_tool.md           # PING工具变更记录
│   ├── tcp_communication.md   # TCP通信模块变更记录
│   └── network_utils.md       # 网络工具库变更记录
├── api/                        # API层变更日志
│   ├── scan_api.md            # 扫描API变更记录
│   ├── ping_api.md            # PING API变更记录
│   ├── connection_api.md      # 连接API变更记录
│   └── websocket.md           # WebSocket功能变更记录
├── frontend/                   # 前端变更日志
│   ├── ui_components.md       # UI组件变更记录
│   ├── views.md               # 页面视图变更记录
│   ├── stores.md              # 状态管理变更记录
│   └── api_client.md          # API客户端变更记录
├── desktop/                    # 桌面客户端变更日志
│   ├── ui_widgets.md          # UI控件变更记录
│   ├── qml_views.md           # QML视图变更记录
│   └── api_integration.md     # API集成变更记录
├── deployment/                 # 部署配置变更日志
│   ├── docker.md              # Docker配置变更记录
│   ├── nginx.md               # Nginx配置变更记录
│   ├── cicd.md                # CI/CD流水线变更记录
│   └── monitoring.md          # 监控配置变更记录
└── infrastructure/             # 基础设施变更日志
    ├── database.md            # 数据库结构变更记录
    ├── security.md            # 安全配置变更记录
    └── performance.md         # 性能优化变更记录
```

## 版本标记体系

### 版本号格式
- **主版本号**: 重大架构变更或不兼容更新
- **次版本号**: 新功能添加或重要功能修改  
- **修订号**: Bug修复和小幅改进
- **构建号**: 开发过程中的持续集成构建

示例: `v1.2.3-build.123`

### 当前版本状态
- **当前版本**: v0.1.0-dev
- **最新稳定版**: 尚未发布
- **开发分支**: main

## 变更记录索引

### v0.1.0-dev (开发中)

#### 2025-05-23 项目初始化
**变更范围**: 项目结构和基础配置

- **文档系统**: [🔗 查看详情](logs/infrastructure/documentation.md#2024-01-14-init)
  - ✅ 创建Structure.md - 项目结构文档
  - ✅ 创建Thread.md - 任务进程文档  
  - ✅ 创建Design.md - 系统设计文档
  - ✅ 创建Log.md - 本变更日志索引
  - ⏳ 创建Issues.md - 问题追踪文档
  - ⏳ 创建Diagram.md - 绘图日志索引

- **项目配置**: [🔗 查看详情](logs/infrastructure/project_setup.md#2024-01-14-init)
  - ⏳ pyproject.toml - UV项目配置
  - ⏳ .gitignore - Git忽略规则
  - ⏳ .ruff.toml - 代码质量配置
  - ⏳ mypy.ini - 类型检查配置

**关联任务**: Thread.md#2025-05-23-项目初始化
**影响模块**: 全项目
**TDD状态**: 文档驱动开发 (DDD)

#### 2025-05-23 响应式布局系统修复
**变更范围**: 前端界面响应式设计优化

- **全局样式修复**: [🔗 查看详情](logs/frontend/responsive_layout.md#2025-05-23-fix)
  - ✅ main.css - 移除破坏性grid布局和宽度限制
  - ✅ App.vue - 断点策略统一与优化
  - ✅ DashboardView.vue - 响应式断点重构
  - ✅ ScanToolsView.vue - 栅格配置统一
  - ✅ PingMonitorView.vue - 栅格配置统一
  - ✅ ConnectionLabView.vue - 断点策略调整
  - ✅ WelcomeItem.vue - 图标布局修复
  - ✅ AboutView.vue - 断点对齐

- **断点系统重构**: [🔗 查看详情](logs/frontend/breakpoints.md#2025-05-23-refactor)
  - ✅ 移动端: ≤768px
  - ✅ 平板端: 769px-1023px
  - ✅ 过渡断点: 1024px-1199px (与Element Plus md对齐)
  - ✅ 桌面端: ≥1200px (与Element Plus lg对齐)

**关联任务**: Thread.md#2025-05-23-响应式布局系统修复
**影响模块**: frontend/src/
**修复类型**: [FIX][P0] 布局系统关键问题修复

#### 2025-05-23 前端API集成阶段第1轮完成
**变更范围**: 前端与后端API完整集成

- **API客户端系统**: [🔗 查看详情](logs/frontend/api_integration.md#2025-05-23-phase1)
  - ✅ client.ts - axios客户端配置，统一请求/响应拦截
  - ✅ scanApi.ts - 端口扫描API接口，WebSocket实时推送
  - ✅ pingApi.ts - PING监控API接口，延迟监控
  - ✅ tcpApi.ts - TCP通信API接口，服务器/客户端管理
  - ✅ systemApi.ts - 系统监控API接口，状态检查

- **状态管理重构**: [🔗 查看详情](logs/frontend/state_management.md#2025-05-23-pinia)
  - ✅ dashboard.ts - Dashboard页面状态管理store
  - ✅ 响应式计算属性 - 系统健康状态、资源使用率
  - ✅ 异步数据获取 - 系统状态、服务状态、性能统计
  - ✅ 错误处理机制 - 统一错误提示和状态管理

- **Dashboard功能增强**: [🔗 查看详情](logs/frontend/dashboard_upgrade.md#2025-05-23-real-api)
  - ✅ DashboardView.vue - 从模拟数据转向真实API调用
  - ✅ 实时监控面板 - CPU、内存、磁盘使用率实时显示
  - ✅ 服务状态表格 - 后端服务运行状态监控
  - ✅ 性能统计卡片 - 扫描、PING、TCP连接次数统计
  - ✅ 自动刷新机制 - 定时更新和手动刷新功能

**关联任务**: Thread.md#2025-05-23-前端API集成阶段第1轮完成
**影响模块**: frontend/src/api/, frontend/src/stores/, frontend/src/views/
**开发类型**: [FEAT][P0] 前后端集成关键功能开发

#### 2025-05-23 后端核心模块
**变更范围**: 核心网络工具实现

- **TDD测试用例**: [🔗 查看详情](logs/core/testing.md#2025-05-23-tdd-init)
  - ⏳ test_port_scanner.py - 端口扫描测试用例
  - ⏳ test_ping_tool.py - PING工具测试用例
  - ⏳ test_tcp_comm.py - TCP通信测试用例

- **核心引擎**: [🔗 查看详情](logs/core/engines.md#2025-05-23-implementation)
  - ⏳ port_scanner.py - 异步端口扫描引擎
  - ⏳ ping_tool.py - ICMP PING工具引擎
  - ⏳ tcp_server.py - 高性能TCP服务器
  - ⏳ tcp_client.py - TCP客户端实现
  - ⏳ network_utils.py - 网络工具函数库

**关联任务**: Thread.md#TDD-核心网络工具测试用例编写
**影响模块**: backend/app/core/
**TDD状态**: 红-绿-重构循环

#### 2025-05-23 API框架搭建
**变更范围**: FastAPI应用框架

- **FastAPI配置**: [🔗 查看详情](logs/api/framework.md#2025-05-23-setup)
  - ⏳ main.py - FastAPI应用入口
  - ⏳ config.py - 配置管理
  - ⏳ database.py - 数据库连接
  - ⏳ middleware.py - 中间件配置

- **API路由**: [🔗 查看详情](logs/api/routes.md#2025-05-23-setup)
  - ⏳ scan.py - 扫描API端点
  - ⏳ ping.py - PING API端点
  - ⏳ connection.py - 连接API端点
  - ⏳ websocket.py - WebSocket端点

**关联任务**: Thread.md#基础API框架搭建
**影响模块**: backend/app/
**TDD状态**: API测试先行

## 变更模板

### 日志文件模板
每个模块的详细变更日志应遵循以下格式：

```markdown
# [模块名] 变更记录

## [日期] [版本] [变更类型]

### 变更概述
简要描述本次变更的目标和范围

### 变更详情
#### 新增功能 (Added)
- 具体新增的功能描述

#### 修改功能 (Changed)  
- 具体修改的功能描述

#### 废弃功能 (Deprecated)
- 即将废弃的功能描述

#### 移除功能 (Removed)
- 已移除的功能描述

#### 修复问题 (Fixed)
- 修复的Bug描述

#### 安全更新 (Security)
- 安全相关的修复和更新

### TDD实践记录
- **测试用例**: 编写的测试用例说明
- **测试覆盖率**: 当前模块测试覆盖率
- **重构记录**: 重构改进的具体内容

### 影响分析
- **向后兼容性**: 是否影响现有API
- **依赖变更**: 新增或修改的依赖项
- **配置变更**: 需要更新的配置项

### 相关链接
- **Issues**: 关联的问题编号
- **Pull Requests**: 关联的PR编号
- **Documentation**: 相关文档更新
```

## 变更类型定义

### 变更类型标识
- `[FEAT]` - 新功能 (Feature)
- `[FIX]` - Bug修复 (Fix)
- `[DOCS]` - 文档更新 (Documentation)
- `[STYLE]` - 代码格式 (Style)
- `[REFACTOR]` - 代码重构 (Refactor)
- `[PERF]` - 性能优化 (Performance)
- `[TEST]` - 测试相关 (Test)
- `[BUILD]` - 构建相关 (Build)
- `[CI]` - CI/CD相关 (Continuous Integration)
- `[SECURITY]` - 安全修复 (Security)
- `[BREAKING]` - 重大变更 (Breaking Change)

### 优先级标识
- `[P0]` - 紧急 (Critical)
- `[P1]` - 高优先级 (High)
- `[P2]` - 中优先级 (Medium)  
- `[P3]` - 低优先级 (Low)

## 自动化日志

### Git提交信息规范
提交信息格式: `[TYPE][Priority] 简要描述`

示例:
```
[FEAT][P1] 实现异步端口扫描引擎
[FIX][P0] 修复PING工具内存泄漏问题
[TEST][P2] 添加TCP通信模块单元测试
```

### 自动化工具集成
- **commitizen**: 规范化提交信息格式
- **conventional-changelog**: 自动生成变更日志
- **semantic-release**: 自动版本发布

## 监控和告警

### 变更影响监控
- **API兼容性**: 自动检测API变更影响
- **性能回归**: 监控性能指标变化
- **安全扫描**: 自动安全漏洞检测

### 告警机制
- **重大变更**: 自动通知相关开发人员
- **性能下降**: 超过阈值时发送告警
- **安全问题**: 立即通知安全团队

## 查看指南

### 按模块查看
要查看特定模块的详细变更记录，请访问对应的日志文件：
- 核心功能: `logs/core/[module].md`
- API接口: `logs/api/[module].md`  
- 前端组件: `logs/frontend/[module].md`
- 基础设施: `logs/infrastructure/[module].md`

### 按版本查看
要查看特定版本的所有变更：
1. 在本文档中找到版本号
2. 点击对应的详情链接
3. 查看相关模块的变更记录

### 按时间查看
按时间倒序查看最新变更：
1. 查看本文档的版本历史部分
2. 从最新日期开始浏览
3. 关注状态标记了解进度

---
*最后更新: 2025-05-23*