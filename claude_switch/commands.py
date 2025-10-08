'''
Author: lirong lirongleiyang@163.com
Date: 2025-10-08 19:08:14
LastEditors: lirong lirongleiyang@163.com
LastEditTime: 2025-10-08 19:08:14
FilePath: /claude-code-switch/claude_switch/commands.py
Description: CLI命令实现模块

Copyright (c) 2025 by lirong, All Rights Reserved.
'''

"""
Claude Code切换器命令实现模块
"""
import subprocess
import sys
import os
from typing import Optional, List
from rich import print
from rich.table import Table
from claude_switch.config import ClaudeConfig, ModelConfig, config_manager

def add_config_impl(
    name: str,
    api_key: str,
    base_url: str,
    timeout_ms: int = 600000,
    disable_nonessential_traffic: bool = True,
    description: str = ""
) -> None:
    """添加新的Claude Code配置实现"""
    config = ClaudeConfig(
        name=name,
        api_key=api_key,
        base_url=base_url,
        timeout_ms=timeout_ms,
        disable_nonessential_traffic=disable_nonessential_traffic,
        description=description
    )

    if config_manager.add_config(config):
        print(f"[green]✓[/green] 配置 '{name}' 添加成功")
    else:
        print(f"[red]✗[/red] 配置 '{name}' 已存在")

def list_configs_impl() -> None:
    """列出所有配置实现"""
    configs = config_manager.list_configs()

    if not configs:
        print("[yellow]暂无配置[/yellow]")
        return

    table = Table(title="Claude Code配置列表")
    table.add_column("名称", style="cyan")
    table.add_column("API URL", style="magenta")
    table.add_column("默认模型", style="green")
    table.add_column("模型数量", style="blue")
    table.add_column("描述", style="white")

    for config in configs:
        model_count = len(config.models)
        default_model = config.default_model if config.default_model else "[dim]未设置[/dim]"
        table.add_row(
            config.name,
            config.base_url,
            default_model,
            str(model_count),
            config.description
        )

    print(table)

def remove_config_impl(name: str) -> None:
    """删除配置实现"""
    if config_manager.remove_config(name):
        print(f"[green]✓[/green] 配置 '{name}' 删除成功")
    else:
        print(f"[red]✗[/red] 配置 '{name}' 不存在")

def edit_config_impl() -> None:
    """使用vim编辑配置文件实现"""
    config_file = config_manager.get_config_file_path()

    if not os.path.exists(config_file):
        print(f"[yellow]![/yellow] 配置文件不存在，创建包含示例配置的新文件: {config_file}")
        # 确保目录存在
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        # 创建包含示例配置的文件
        config_manager.create_example_config()

    print(f"[green]→[/green] 使用vim打开配置文件: {config_file}")
    try:
        subprocess.run(["vim", config_file])
        print(f"[green]✓[/green] 配置文件编辑完成")
    except FileNotFoundError:
        print(f"[red]✗[/red] 未找到vim编辑器，请确保vim已安装")
    except KeyboardInterrupt:
        print("\n[yellow]![/yellow] 已退出vim编辑")

def show_config_impl(name: str) -> None:
    """显示配置详情实现"""
    config = config_manager.get_config(name)
    if not config:
        print(f"[red]✗[/red] 配置 '{name}' 不存在")
        return

    table = Table(title=f"配置详情: {name}")
    table.add_column("项目", style="cyan")
    table.add_column("值", style="white")

    table.add_row("名称", config.name)
    table.add_row("API URL", config.base_url)
    table.add_row("默认模型", config.default_model if config.default_model else "[dim]未设置[/dim]")
    table.add_row("超时时间", f"{config.timeout_ms}ms")
    table.add_row("禁用非必要流量", "是" if config.disable_nonessential_traffic else "否")
    table.add_row("描述", config.description)

    print(table)

    # 显示模型列表
    if config.models:
        model_table = Table(title="模型列表")
        model_table.add_column("模型名称", style="yellow")
        model_table.add_column("模型ID", style="green")
        model_table.add_column("快速小模型", style="blue")
        model_table.add_column("描述", style="white")

        for model_name, model_config in config.models.items():
            is_default = "[green]✓[/green]" if model_name == config.default_model else ""
            model_table.add_row(
                f"{model_name} {is_default}",
                model_config.model,
                model_config.small_fast_model if model_config.small_fast_model else "[dim]未设置[/dim]",
                model_config.description
            )

        print(model_table)

def add_model_impl(
    config_name: str,
    model_name: str,
    model_id: str,
    small_fast_model: str = "",
    description: str = "",
    set_default: bool = False
) -> None:
    """为配置添加模型实现"""
    config = config_manager.get_config(config_name)
    if not config:
        print(f"[red]✗[/red] 配置 '{config_name}' 不存在")
        return

    model_config = ModelConfig(
        name=model_name,
        model=model_id,
        small_fast_model=small_fast_model,
        description=description
    )

    if config.add_model(model_config):
        if set_default or not config.default_model:
            config.set_default_model(model_name)
        config_manager.update_config(config)
        print(f"[green]✓[/green] 模型 '{model_name}' 添加到配置 '{config_name}' 成功")
    else:
        print(f"[red]✗[/red] 模型 '{model_name}' 已存在于配置 '{config_name}'")

def remove_model_impl(config_model: str) -> None:
    """从配置中删除模型实现"""
    config_name, model_name = config_model.split(':', 1)
    config = config_manager.get_config(config_name)
    if not config:
        print(f"[red]✗[/red] 配置 '{config_name}' 不存在")
        return

    if config.remove_model(model_name):
        config_manager.update_config(config)
        print(f"[green]✓[/green] 模型 '{model_name}' 从配置 '{config_name}' 删除成功")
    else:
        print(f"[red]✗[/red] 模型 '{model_name}' 不存在于配置 '{config_name}'")

def list_models_impl(config_name: str) -> None:
    """列出配置中的所有模型实现"""
    config = config_manager.get_config(config_name)
    if not config:
        print(f"[red]✗[/red] 配置 '{config_name}' 不存在")
        return

    if not config.models:
        print(f"[yellow]配置 '{config_name}' 暂无模型[/yellow]")
        return

    table = Table(title=f"配置 '{config_name}' 的模型列表")
    table.add_column("模型名称", style="yellow")
    table.add_column("模型ID", style="green")
    table.add_column("快速小模型", style="blue")
    table.add_column("描述", style="white")

    for model_name, model_config in config.models.items():
        is_default = "[green]✓[/green]" if model_name == config.default_model else ""
        table.add_row(
            f"{model_name} {is_default}",
            model_config.model,
            model_config.small_fast_model if model_config.small_fast_model else "[dim]未设置[/dim]",
            model_config.description
        )

    print(table)

def set_default_model_impl(config_model: str) -> None:
    """设置配置的默认模型实现"""
    config_name, model_name = config_model.split(':', 1)
    config = config_manager.get_config(config_name)
    if not config:
        print(f"[red]✗[/red] 配置 '{config_name}' 不存在")
        return

    if config.set_default_model(model_name):
        config_manager.update_config(config)
        print(f"[green]✓[/green] 配置 '{config_name}' 的默认模型已设置为 '{model_name}'")
    else:
        print(f"[red]✗[/red] 模型 '{model_name}' 不存在于配置 '{config_name}'")

def use_config_impl(
    config_model: Optional[str] = None,
    args: Optional[str] = None
) -> None:
    """使用指定配置启动Claude Code实现"""

    model: Optional[str] = None
    # 如果没有指定配置名称，使用默认配置
    if not config_model:
        default_config = config_manager.get_default_config()
        if not default_config:
            print(f"[red]✗[/red] 未设置默认配置，请使用 'claude-switch run <配置名称>' 或先设置默认配置")
            return
        config_name = default_config.name
        config = default_config
    else:
        # 处理 config:model 格式或仅配置名称
        if ":" in config_model:
            config_name, model = config_model.split(":", 1)
        else:
            config_name = config_model
            model = None

        config = config_manager.get_config(config_name)
        if not config:
            print(f"[red]✗[/red] 配置 '{config_name}' 不存在")
            return

    if not config.models:
        print(f"[red]✗[/red] 配置 '{config_name}' 没有配置任何模型")
        return

    # 如果没有指定模型，使用默认模型
    if not model:
        model = config.default_model

    print(f"[green]→[/green] 使用配置 '{config_name}' 模型 '{model}' 启动Claude Code...")

    # 设置环境变量
    try:
        env_vars = config.to_env_vars(model)
    except ValueError as e:
        print(f"[red]✗[/red] {e}")
        return

    current_env = dict(os.environ)
    current_env.update(env_vars)

    # 清理冲突的环境变量
    # 如果设置了ANTHROPIC_API_KEY，就清除ANTHROPIC_AUTH_TOKEN，反之亦然
    if "ANTHROPIC_API_KEY" in current_env and current_env["ANTHROPIC_API_KEY"]:
        current_env.pop("ANTHROPIC_AUTH_TOKEN", None)
    elif "ANTHROPIC_AUTH_TOKEN" in current_env and current_env["ANTHROPIC_AUTH_TOKEN"]:
        current_env.pop("ANTHROPIC_API_KEY", None)

    # 构建Claude Code命令
    claude_command = ["claude"]
    if args:
        # 使用 shlex.split 来正确处理带引号的参数
        import shlex
        claude_command.extend(shlex.split(args))

    try:
        # 启动Claude Code
        subprocess.run(claude_command, env=current_env)
    except FileNotFoundError:
        print(f"[red]✗[/red] 未找到Claude Code命令，请确保已安装Claude Code")
    except KeyboardInterrupt:
        print("\n[yellow]![/yellow] 已退出Claude Code")

def set_default_config_impl(name: Optional[str] = None) -> None:
    """设置或显示默认配置实现"""
    if not name:
        # 显示当前默认配置
        default_config = config_manager.get_default_config()
        if default_config:
            print(f"[green]✓[/green] 当前默认配置: '{default_config.name}'")
        else:
            print(f"[yellow]![/yellow] 未设置默认配置")
        return

    # 设置默认配置
    if config_manager.set_default_config(name):
        print(f"[green]✓[/green] 默认配置已设置为 '{name}'")
    else:
        print(f"[red]✗[/red] 配置 '{name}' 不存在")

def current_config_impl() -> None:
    """显示当前环境变量和默认配置实现"""
    # 显示环境变量
    env_vars = {
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        "ANTHROPIC_BASE_URL": os.environ.get("ANTHROPIC_BASE_URL"),
        "ANTHROPIC_MODEL": os.environ.get("ANTHROPIC_MODEL"),
        "ANTHROPIC_SMALL_FAST_MODEL": os.environ.get("ANTHROPIC_SMALL_FAST_MODEL"),
        "API_TIMEOUT_MS": os.environ.get("API_TIMEOUT_MS"),
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": os.environ.get("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC")
    }

    table = Table(title="当前环境变量")
    table.add_column("变量名", style="yellow")
    table.add_column("值", style="white")

    for var_name, value in env_vars.items():
        display_value = value if value else "[dim]未设置[/dim]"
        if var_name == "ANTHROPIC_API_KEY" and value:
            display_value = "*" * 8
        table.add_row(var_name, display_value)

    print(table)

    # 显示默认配置信息
    default_config = config_manager.get_default_config()
    if default_config:
        print(f"\n[green]✓[/green] 默认配置: '{default_config.name}'")
    else:
        print(f"\n[yellow]![/yellow] 未设置默认配置")