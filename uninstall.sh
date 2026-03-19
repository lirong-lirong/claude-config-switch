#!/bin/bash
###
# @Description: Claude Code Switch 卸载脚本
###

echo "🗑️ 卸载 Claude Code Switch..."

# 1. 卸载 Python 包
if pip3 uninstall -y claude-code-switch; then
    echo "✅ Claude Code Switch 包卸载成功！"
else
    echo "⚠️  警告：Claude Code Switch 包可能未安装或卸载失败。"
fi

# 2. 清理环境变量配置

echo "🔧 清理环境变量配置..."

# 确定 shell 配置文件
SHELL_TYPE=$(basename "$SHELL")
RC_FILE=""

case "$SHELL_TYPE" in
    "zsh")
        RC_FILE="$HOME/.zshrc"
        ;;
    "bash")
        RC_FILE="$HOME/.bashrc"
        ;;
    *)
        echo "ℹ️  不支持的 Shell 类型 ($SHELL_TYPE)，跳过自动 PATH 清理。"
        ;;
esac

if [ -n "$RC_FILE" ] && [ -f "$RC_FILE" ]; then
    # 使用 sed 命令移除安装脚本添加的注释块和 PATH 导出语句
    # 匹配从 "# Claude Code Switch - Python用户bin目录" 开始的两行内容
    if sed -i.bak "/# Claude Code Switch - Python用户bin目录/,+1d" "$RC_FILE" 2>/dev/null; then
        echo "✅ 已从 $RC_FILE 中移除 PATH 配置。"
        echo "   原文件已备份为 ${RC_FILE}.bak"
    else
        echo "⚠️  警告：在 $RC_FILE 中未找到或无法移除 PATH 配置。"
    fi
else
    echo "⚠️  警告：未找到 shell 配置文件 ($RC_FILE)，无法自动清理 PATH。"
fi

# 3. 移除自动补全 (可选，通常依赖于包卸载，但为确保干净可尝试手动清理)
# 自动补全通常位于特定的 shell 目录，由于没有标准的卸载机制，
# 建议用户在终端重启后，手动清理缓存或相关文件（如果存在）

# 4. 最终提示

echo ""
echo "🎉 卸载完成！"
echo ""
echo "💡 提示：为了使环境变量更改完全生效，请执行以下操作之一："
echo "   1. 重新启动您的终端。"
if [ -n "$RC_FILE" ]; then
    echo "   2. 运行 'source $RC_FILE' 使其立即生效。"
fi
echo ""
