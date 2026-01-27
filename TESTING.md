# 测试指南

本项目使用 pytest 进行单元测试，本文档说明如何运行和管理测试。

## 测试结构

```
tests/
├── __init__.py           # 测试包初始化
├── conftest.py          # pytest配置和共享fixtures
├── test_config.py       # config.py模块的测试
├── test_commands.py     # commands.py模块的测试
└── test_complete.py     # complete.py模块的测试
```

## 安装测试依赖

### 方式一：使用requirements.txt
```bash
pip3 install -r requirements.txt
```

### 方式二：使用setup.py
```bash
pip3 install -e ".[test]"
```

### 方式三：手动安装
```bash
pip3 install pytest pytest-cov pytest-mock
```

## 运行测试

### 运行所有测试
```bash
pytest tests/
```

### 运行特定测试文件
```bash
pytest tests/test_config.py
pytest tests/test_commands.py
pytest tests/test_complete.py
```

### 运行特定测试类
```bash
pytest tests/test_config.py::TestModelConfig
pytest tests/test_config.py::TestClaudeConfig
pytest tests/test_config.py::TestConfigManager
```

### 运行特定测试函数
```bash
pytest tests/test_config.py::TestModelConfig::test_model_config_creation
```

### 显示详细输出
```bash
pytest tests/ -v
```

### 显示打印输出
```bash
pytest tests/ -s
```

## 测试覆盖率

### 生成覆盖率报告
```bash
pytest tests/ --cov=claude_switch --cov-report=term-missing
```

### 生成HTML覆盖率报告
```bash
pytest tests/ --cov=claude_switch --cov-report=html
```

HTML报告会生成在 `htmlcov/` 目录，用浏览器打开 `htmlcov/index.html` 查看详细报告。

### 当前测试覆盖率

- **总测试数量**：92个测试
- **总体覆盖率**：83%
- **模块覆盖率**：
  - `__init__.py`: 100%
  - `complete.py`: 100%
  - `config.py`: 99%
  - `commands.py`: 94%
  - `main.py`: 0% (CLI入口，通过集成测试覆盖)

## 测试内容

### test_config.py (39个测试)

测试配置管理核心功能：

**ModelConfig测试**：
- 创建模型配置
- 默认值处理

**ClaudeConfig测试**：
- 创建配置
- 添加/删除/获取模型
- 设置默认模型
- 环境变量转换
- 边界条件处理

**ConfigManager测试**：
- 配置的CRUD操作
- 默认配置管理
- 配置持久化
- 损坏文件恢复
- 示例配置生成

### test_commands.py (35个测试)

测试所有CLI命令的业务逻辑：

- **配置管理命令**：add, list, remove, edit, show
- **模型管理命令**：model-add, model-remove, model-list, model-set-default
- **运行命令**：use_config (各种场景)
- **查看命令**：default, current

### test_complete.py (18个测试)

测试自动补全功能：

- **配置名称补全**：前缀匹配、空输入、无匹配
- **模型名称补全**：config:model格式、默认标记、描述显示
- **完整补全**：多配置、多模型、边界情况

## 编写新测试

### 使用fixtures

在 `conftest.py` 中定义了常用的fixtures：

```python
def test_my_function(temp_config_dir, sample_claude_config):
    # temp_config_dir: 临时配置目录
    # sample_claude_config: 示例配置对象
    pass
```

### Mock外部依赖

使用 `pytest-mock` 或 `unittest.mock`：

```python
from unittest.mock import patch

@patch('claude_switch.commands.config_manager')
def test_something(mock_manager):
    mock_manager.get_config.return_value = some_config
    # 测试代码
```

### 测试异常

```python
import pytest

def test_exception():
    with pytest.raises(ValueError, match="错误消息"):
        some_function_that_raises()
```

## 测试最佳实践

1. **一个测试一个断言**：每个测试应该专注于验证一个行为
2. **清晰的测试名称**：使用描述性的名称，如 `test_add_config_success`
3. **独立性**：测试之间不应该有依赖关系
4. **使用fixtures**：共享测试数据和设置
5. **Mock外部依赖**：隔离被测试的代码
6. **测试边界条件**：空值、无效输入、极限情况

## 持续集成

可以在CI/CD中添加以下步骤：

```yaml
# GitHub Actions示例
- name: Install dependencies
  run: pip install -e ".[test]"

- name: Run tests
  run: pytest tests/ --cov=claude_switch --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v2
```

## 调试测试

### 进入pdb调试器
```bash
pytest tests/ --pdb
```

### 在第一个失败时停止
```bash
pytest tests/ -x
```

### 运行上次失败的测试
```bash
pytest tests/ --lf
```

### 显示最慢的10个测试
```bash
pytest tests/ --durations=10
```

## 测试输出示例

```
============================= test session starts ==============================
platform darwin -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/user/claude-code-switch
configfile: pytest.ini
plugins: mock-3.15.1, cov-7.0.0
collecting ... collected 92 items

tests/test_config.py::TestModelConfig::test_model_config_creation PASSED  [  1%]
tests/test_config.py::TestModelConfig::test_model_config_defaults PASSED  [  2%]
...

============================== 92 passed in 0.15s ==============================

================================ tests coverage ================================
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
claude_switch/__init__.py       1      0   100%
claude_switch/commands.py     190     11    94%
claude_switch/complete.py      45      0   100%
claude_switch/config.py       128      1    99%
claude_switch/main.py          58     58     0%
---------------------------------------------------------
TOTAL                         422     70    83%
```

## 常见问题

### Q: 如何查看测试覆盖的代码？
A: 运行 `pytest --cov=claude_switch --cov-report=html`，然后打开 `htmlcov/index.html`

### Q: 如何只运行失败的测试？
A: 使用 `pytest --lf` (last failed)

### Q: 如何并行运行测试？
A: 安装 `pytest-xdist`，然后运行 `pytest -n auto`

### Q: 测试很慢怎么办？
A: 使用 `pytest --durations=10` 查找慢的测试，然后优化它们

## 贡献测试

欢迎贡献新的测试用例！请确保：

1. 测试名称清晰描述测试内容
2. 包含必要的文档字符串
3. 遵循现有的测试结构
4. 运行 `pytest` 确保所有测试通过
5. 检查测试覆盖率没有下降

## 联系

如有测试相关问题，请提交issue到项目仓库。
