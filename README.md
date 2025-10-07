# Claude Code切换器

一个Python命令行工具，用于管理多个Claude Code API配置并快速切换环境变量启动Claude Code。

## 功能特性

- ✅ 管理多个API配置（名称、API密钥、URL等）
- ✅ 支持为每个API配置多个模型
- ✅ 快速切换配置和模型启动Claude Code
- ✅ 查看当前环境变量配置
- ✅ 安全的配置存储（JSON文件）
- ✅ 美观的命令行界面（Rich）
- ✅ 自动环境变量配置（PATH）
- ✅ 智能安装脚本

## 安装

### 快速安装

```bash
# 克隆项目
git clone <repository-url>
cd claude-code-switch

# 一键安装（自动配置环境变量）
./install.sh
```

### 自动补全

安装完成后，重启终端或运行：

```bash
# Zsh
source ~/.zshrc

# Bash
source ~/.bashrc

# 自动补全
claude-switch --install-completion
```

### 环境变量设置（自动配置）

安装脚本会自动检测并配置 Python 用户 bin 目录到 PATH 中。如果安装后 `claude-switch` 命令仍然找不到，请运行：

```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

或者重启终端。

## 使用方法

**推荐直接编辑配置文件来修改配置**

### 添加配置

```bash
claude-switch add deepseek \
  --api-key sk-xxx \
  --base-url https://api.deepseek.com/anthropic \
  --description "DeepSeek API"
```

### 为配置添加模型

```bash
# 添加Chat模型并设为默认
claude-switch model-add deepseek chat \
  --model-id deepseek-chat \
  --description "DeepSeek Chat模型" \
  --set-default

# 添加Reasoner模型
claude-switch model-add deepseek reasoner \
  --model-id deepseek-reasoner \
  --small-fast-model deepseek-chat \
  --description "DeepSeek Reasoner模型"

# 添加Coder模型
claude-switch model-add deepseek coder \
  --model-id deepseek-coder \
  --description "DeepSeek Coder模型"
```

### 列出所有配置

```bash
claude-switch list
```

### 列出配置中的模型

```bash
claude-switch model-list deepseek
```

### 使用配置启动Claude Code

```bash
# 使用默认模型启动
claude-switch run deepseek

# 使用指定模型启动
claude-switch run deepseek --model reasoner

# 使用指定模型并传递参数给Claude Code
claude-switch run deepseek --model chat --help
```

### 设置默认模型

```bash
claude-switch model-set-default deepseek reasoner
```

### 查看配置详情

```bash
claude-switch show deepseek
```

### 编辑配置

```bash
claude-switch edit deepseek --model deepseek-reasoner
```

### 删除配置

```bash
claude-switch remove deepseek
```

### 查看当前环境变量

```bash
claude-switch current
```

## 配置项说明

配置文件结构：

- `default_config`: 默认配置名称
- `configs`: 配置字典，键为配置名称

每个配置包含以下字段：

- `name`: 配置名称（唯一标识）
- `api_key`: API密钥
- `base_url`: API基础URL
- `timeout_ms`: 超时时间（毫秒）
- `disable_nonessential_traffic`: 是否禁用非必要流量
- `description`: 配置描述
- `models`: 模型配置字典
- `default_model`: 默认模型名称

每个模型配置包含：

- `name`: 模型名称
- `model`: 模型ID
- `small_fast_model`: 快速小模型ID（可选）
- `description`: 模型描述

## 环境变量

启动Claude Code时设置的环境变量：

- `ANTHROPIC_API_KEY`: API密钥
- `ANTHROPIC_BASE_URL`: API基础URL
- `ANTHROPIC_MODEL`: 模型名称
- `ANTHROPIC_SMALL_FAST_MODEL`: 快速小模型名称
- `API_TIMEOUT_MS`: 超时时间
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`: 禁用非必要流量

## 配置文件位置

配置文件存储在：

```
~/.config/claude-code-switch/config.json
```

## 示例配置

```json
{
  "default_config": "deepseek",
  "configs": {
    "deepseek": {
      "name": "deepseek",
      "api_key": "sk-xxx",
      "base_url": "https://api.deepseek.com/anthropic",
      "timeout_ms": 600000,
      "disable_nonessential_traffic": true,
      "description": "DeepSeek API",
      "models": {
        "chat": {
          "name": "chat",
          "model": "deepseek-chat",
          "small_fast_model": "",
          "description": "DeepSeek Chat模型"
        },
        "reasoner": {
          "name": "reasoner",
          "model": "deepseek-reasoner",
          "small_fast_model": "deepseek-chat",
          "description": "DeepSeek Reasoner模型"
        },
        "coder": {
          "name": "coder",
          "model": "deepseek-coder",
          "small_fast_model": "",
          "description": "DeepSeek Coder模型"
        }
      },
      "default_model": "reasoner"
    },
    "anthropic": {
      "name": "anthropic",
      "api_key": "sk-ant-xxx",
      "base_url": "https://api.anthropic.com",
      "timeout_ms": 600000,
      "disable_nonessential_traffic": true,
      "description": "Anthropic官方API",
      "models": {
        "sonnet": {
          "name": "sonnet",
          "model": "claude-3-5-sonnet-20241022",
          "small_fast_model": "claude-3-haiku-20240307",
          "description": "Claude 3.5 Sonnet"
        },
        "opus": {
          "name": "opus",
          "model": "claude-3-opus-20240229",
          "small_fast_model": "claude-3-haiku-20240307",
          "description": "Claude 3 Opus"
        }
      },
      "default_model": "sonnet"
    }
  }
}
```
