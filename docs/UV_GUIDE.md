# UV工具链使用指南

> 网络安全工具平台现代化Python依赖管理指南

## 🚀 快速开始

### 环境设置
```bash
# 确保pipx和uv已安装
pip install pipx
pipx install uv
pipx ensurepath

# 验证安装
uv --version
```

### 项目初始化
```bash
# 同步项目依赖
uv sync

# 检查虚拟环境
ls .venv/

# 检查锁定文件
cat uv.lock
```

## 📦 依赖管理

### 添加依赖
```bash
# 添加生产依赖
uv add fastapi>=0.104.0

# 添加开发依赖  
uv add --dev pytest>=7.4.0

# 添加可选依赖组
uv add --optional network ping3>=4.0.0
```

### 移除依赖
```bash
# 移除依赖
uv remove package-name

# 移除开发依赖
uv remove --dev package-name
```

### 依赖信息
```bash
# 查看已安装包
uv pip list

# 显示依赖树
uv pip show package-name

# 检查依赖冲突
uv pip check
```

## 🧪 测试运行

### 使用uv运行测试
```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest backend/tests/test_core/

# 运行带覆盖率的测试
uv run pytest --cov

# 设置Python路径运行API测试
$env:PYTHONPATH="backend"; uv run pytest backend/tests/test_api/ -q
```

### 代码质量检查
```bash
# 代码格式化
uv run ruff format

# 代码检查
uv run ruff check

# 类型检查
uv run mypy backend/

# 安全检查
uv run bandit -r backend/
```

## 🔧 开发工具

### 运行应用
```bash
# 启动FastAPI开发服务器
uv run uvicorn backend.app.main:app --reload

# 运行特定脚本
uv run python backend/app/main.py

# 运行CLI工具
uv run python cli_tools/network_scanner.py --help
```

### 环境管理
```bash
# 激活虚拟环境 (可选)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 查看环境信息
uv python --version
uv pip list

# 重建环境
rm -rf .venv uv.lock
uv sync
```

## 📋 项目配置

### pyproject.toml关键配置
```toml
[tool.uv]
dev-dependencies = [
    "network-security-platform[dev,lint,docs]"
]
python-downloads = "automatic"

[project]
dependencies = [
    "fastapi>=0.104.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.0.0",
    # ... 其他依赖
]

[project.optional-dependencies]
dev = ["pytest>=7.4.0", "pytest-cov>=4.1.0"]
lint = ["ruff>=0.1.0", "mypy>=1.7.0"]
docs = ["mkdocs>=1.5.0"]
```

### pytest配置
```bash
# 设置Python路径（Windows PowerShell）
$env:PYTHONPATH="backend"

# 运行测试的标准格式
uv run pytest backend/tests/ --tb=short --no-cov
```

## 🚨 常见问题

### 模块导入问题
```bash
# 问题: ModuleNotFoundError: No module named 'app'
# 解决: 设置正确的PYTHONPATH
$env:PYTHONPATH="backend"; uv run pytest

# 或者从正确的目录运行
cd backend && uv run pytest tests/
```

### 协程警告
```bash
# 问题: pytest-asyncio警告
# 解决: 添加配置到pytest.ini或pyproject.toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
```

### 硬链接警告
```bash
# 问题: hardlink files warning
# 解决: 设置链接模式
export UV_LINK_MODE=copy
# 或者
uv sync --link-mode=copy
```

## 🔄 CI/CD集成

### GitHub Actions示例
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v1
  
- name: Sync dependencies
  run: uv sync
  
- name: Run tests
  run: uv run pytest
  env:
    PYTHONPATH: backend
```

### Docker集成
```dockerfile
# 安装uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 同步依赖
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
```

## 📊 性能优势

- **速度**: 比pip快10-100倍的依赖解析
- **可靠性**: 锁定文件确保可重现构建
- **缓存**: 智能缓存减少重复下载
- **并行**: 并行安装提升效率

---
**维护者**: Ignorant-lu  
**更新时间**: 2025-05-23  
**uv版本**: 0.7.7 