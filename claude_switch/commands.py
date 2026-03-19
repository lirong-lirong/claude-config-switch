"""
Claude Code切换器命令实现模块
"""
import subprocess
import os
from typing import Optional
from rich import print
from rich.table import Table
from claude_switch.config import config_manager


def list_configs_impl() -> None:
    """列出所有配置及详情"""
    load_error = config_manager.get_load_error()
    if load_error:
        print(f"[red]✗[/red] 配置文件加载失败: {load_error}")
        print("[yellow]![/yellow] 请使用 'ccs edit' 修复配置文件后重试")
        return

    configs = config_manager.list_configs()

    if not configs:
        print("[yellow]暂无配置，请使用 'ccs edit' 编辑配置文件[/yellow]")
        return

    for config in configs:
        # 配置基本信息
        table = Table(title=f"配置: {config.name}")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="white")

        table.add_row("名称", config.name)
        table.add_row("API URL", config.base_url)
        table.add_row("默认模型", config.default_model if config.default_model else "[dim]未设置[/dim]")
        table.add_row("超时时间", f"{config.timeout_ms}ms")
        table.add_row("禁用非必要流量", "是" if config.disable_nonessential_traffic else "否")
        table.add_row("描述", config.description or "[dim]无[/dim]")

        print(table)

        # 模型列表
        if config.models:
            model_table = Table(title=f"  模型列表")
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
                    model_config.description or ""
                )

            print(model_table)
        else:
            print("  [dim]暂无模型[/dim]")
        print()

    # 汇总表
    summary = Table(title="配置汇总")
    summary.add_column("配置", style="cyan")
    summary.add_column("模型列表", style="white")

    for config in configs:
        if config.models:
            parts = []
            for mname in config.models:
                if mname == config.default_model:
                    parts.append(f"[green]✓[/green] {mname}")
                else:
                    parts.append(mname)
            model_str = ", ".join(parts)
        else:
            model_str = "[dim]暂无模型[/dim]"
        summary.add_row(config.name, model_str)

    print(summary)


def edit_config_impl() -> None:
    """使用vim编辑配置文件实现"""
    config_file = config_manager.get_config_file_path()

    if not os.path.exists(config_file):
        print(f"[yellow]![/yellow] 配置文件不存在，创建包含示例配置的新文件: {config_file}")
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        config_manager.create_example_config()

    print(f"[green]→[/green] 使用vim打开配置文件: {config_file}")
    try:
        subprocess.run(["vim", config_file])
        print(f"[green]✓[/green] 配置文件编辑完成")
    except FileNotFoundError:
        print(f"[red]✗[/red] 未找到vim编辑器，请确保vim已安装")
    except KeyboardInterrupt:
        print("\n[yellow]![/yellow] 已退出vim编辑")


def use_config_impl(
    config_model: Optional[str] = None,
    args: Optional[str] = None
) -> None:
    """使用指定配置启动Claude Code实现"""

    model: Optional[str] = None
    if not config_model:
        default_config = config_manager.get_default_config()
        if not default_config:
            print(f"[red]✗[/red] 未设置默认配置，请使用 'ccs run <配置名称>' 或先在配置文件中设置 default_config")
            return
        config_name = default_config.name
        config = default_config
    else:
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

    if not model:
        model = config.default_model

    print(f"[green]→[/green] 使用配置 '{config_name}' 模型 '{model}' 启动Claude Code...")

    try:
        env_vars = config.to_env_vars(model)
    except ValueError as e:
        print(f"[red]✗[/red] {e}")
        return

    current_env = dict(os.environ)
    current_env.update(env_vars)

    if "ANTHROPIC_API_KEY" in current_env and current_env["ANTHROPIC_API_KEY"]:
        current_env.pop("ANTHROPIC_AUTH_TOKEN", None)
    elif "ANTHROPIC_AUTH_TOKEN" in current_env and current_env["ANTHROPIC_AUTH_TOKEN"]:
        current_env.pop("ANTHROPIC_API_KEY", None)

    claude_command = ["claude"]
    if args:
        import shlex
        claude_command.extend(shlex.split(args))

    try:
        subprocess.run(claude_command, env=current_env)
    except FileNotFoundError:
        print(f"[red]✗[/red] 未找到Claude Code命令，请确保已安装Claude Code")
    except KeyboardInterrupt:
        print("\n[yellow]![/yellow] 已退出Claude Code")


def current_config_impl() -> None:
    """显示当前环境变量和默认配置实现"""
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

    default_config = config_manager.get_default_config()
    if default_config:
        print(f"\n[green]✓[/green] 默认配置: '{default_config.name}'")
    else:
        print(f"\n[yellow]![/yellow] 未设置默认配置")
