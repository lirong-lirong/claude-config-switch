#!/bin/bash
###
 # @Author: lirong lirongleiyang@163.com
 # @Date: 2025-10-07 18:57:53
 # @LastEditors: lirong lirongleiyang@163.com
 # @LastEditTime: 2025-10-07 19:05:31
 # @FilePath: /claude-code-switch/install.sh
 # @Description: 
 # 
 # Copyright (c) 2025 by lirong, All Rights Reserved. 
### 

# Claude Code Switch 安装脚本

echo "🚀 安装 Claude Code Switch..."

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 获取Python用户bin目录
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
USER_BIN_DIR="$HOME/Library/Python/$PYTHON_VERSION/bin"

# 安装包
pip3 install -e .

if [ $? -eq 0 ]; then
    echo "✅ Claude Code Switch 安装成功！"
    echo ""

    # 检查PATH是否包含Python用户bin目录
    if [[ ":$PATH:" != *":$USER_BIN_DIR:"* ]]; then
        echo "🔧 配置环境变量..."
        SHELL_TYPE=$(basename "$SHELL")
        RC_FILE=""

        case "$SHELL_TYPE" in
            "zsh")
                RC_FILE="$HOME/.zshrc"
                ;;
            "bash")
                RC_FILE="$HOME/.bashrc"
                ;;
        esac

        if [ -n "$RC_FILE" ]; then
            # 添加PATH到shell配置文件
            echo "" >> "$RC_FILE"
            echo "# Claude Code Switch - Python用户bin目录" >> "$RC_FILE"
            echo "export PATH=\"$USER_BIN_DIR:\$PATH\"" >> "$RC_FILE"
            echo "✅ 已将 $USER_BIN_DIR 添加到 PATH (在 $RC_FILE 中)"

            # 立即生效
            export PATH="$USER_BIN_DIR:$PATH"
        else
            echo "⚠️  无法自动配置PATH，请手动添加:"
            echo "   export PATH=\"$USER_BIN_DIR:\$PATH\""
        fi
    else
        echo "✅ PATH已包含Python用户bin目录"
    fi

    echo ""
    echo "📝 使用方法:"
    echo "   claude-switch --help"
    echo ""
    echo "💡 提示: 重启终端或运行 'source ~/.bashrc' (或 ~/.zshrc) 使配置生效"
else
    echo "❌ 安装失败"
    exit 1
fi