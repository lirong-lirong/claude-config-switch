"""
Claude Code切换器主程序 - 支持多模型版本
"""
import typer
import subprocess
import sys
import os
from typing import Optional, List
from typing_extensions import Annotated
from rich import print
from rich.table import Table
from rich.console import Console

from .config import ConfigManager, ClaudeConfig, ModelConfig

app = typer.Typer(no_args_is_help=True, help="Claude Code Config Switch", rich_markup_mode="rich")
config_manager = ConfigManager()
err_console = Console(stderr=True)

def complete_config_names(incomplete: str):
    """为配置名称提供自动补全"""
    configs = config_manager.list_configs()
    for config in configs:
        if config.name.startswith(incomplete):
            yield (config.name, config.description or f"API URL: {config.base_url}")        

def complete_model_names(incomplete: str):
    """为模型名称提供自动补全"""

    # 获取所有配置
    configs = config_manager.list_configs()

    # 收集所有模型名称
    all_models = []
    for config in configs:
        if config.models:
            for model_name, model_config in config.models.items():
                unique_name = f"{config.name}:{model_name}"  
                is_default = " (默认)" if model_name == config.default_model else ""
                help_text = f"{model_config.model}{is_default}"
                if model_config.description:
                    help_text = f"{help_text} - {model_config.description}"
                all_models.append((unique_name, help_text))
                
    # err_console.print(f"{all_models}")
    # 过滤匹配的模型
    if not incomplete:
        # 没有输入时返回所有模型
        for model_name, help_text in all_models:
            yield (model_name, help_text)
    else:
        # 有输入时返回匹配的模型
        for model_name, help_text in all_models:
            if model_name.startswith(incomplete):
                yield (model_name, help_text)


def complete_config_model_names(incomplete: str):
    """为模型名称提供自动补全
        默认输入格式为 [config_name]:[model_name]
    """
    # 返回所有可能的模型名称
    # 获取所有配置
    configs = config_manager.list_configs()

    # 收集所有模型名称
    all_models = []
    for config in configs:
        if config.models:
            for model_name, model_config in config.models.items():
                unique_name = f"{config.name}:{model_name}"  
                is_default = " (默认)" if model_name == config.default_model else ""
                help_text = f"{model_config.model}{is_default}"
                if model_config.description:
                    help_text = f"{help_text} - {model_config.description}"
                all_models.append((unique_name, help_text))
                
    # err_console.print(f"{all_models}")
    # 过滤匹配的模型
    if not incomplete:
        # 没有输入时返回所有模型
        for model_name, help_text in all_models:
            yield (model_name, help_text)
    else:
        # 有输入时返回匹配的模型
        for model_name, help_text in all_models:
            if model_name.startswith(incomplete):
                yield (model_name, help_text)

@app.command(name="add")
def add_config(
    name: Annotated[str, typer.Argument(help="配置名称")],
    api_key: Annotated[str, typer.Option(help="API密钥", prompt=True, hide_input=True)],
    base_url: Annotated[str, typer.Option(help="API基础URL")],
    timeout_ms: Annotated[int, typer.Option(help="超时时间(毫秒)")] = 600000,
    disable_nonessential_traffic: Annotated[bool, typer.Option(help="禁用非必要流量")] = True,
    description: Annotated[str, typer.Option(help="配置描述")] = ""
) -> None:
    """[bold green]添加新的Claude Code配置[/bold green]

    创建一个新的API配置，支持多个模型和提供商。

    [bold]示例:[/bold]
    claude-switch add deepseek --api-key sk-xxx --base-url https://api.deepseek.com/anthropic
    """
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


@app.command(name="list")
@app.command(name="ls")
def list_configs() -> None:
    """[bold green]列出所有配置[/bold green]

    显示所有已保存的API配置及其详细信息。

    [bold]示例:[/bold]
    claude-switch list
    claude-switch ls
    """
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


@app.command(name="remove")
@app.command(name="rm")
def remove_config(
    name: Annotated[str, typer.Argument(help="配置名称", autocompletion=complete_config_names)]
) -> None:
    """删除配置"""
    if config_manager.remove_config(name):
        print(f"[green]✓[/green] 配置 '{name}' 删除成功")
    else:
        print(f"[red]✗[/red] 配置 '{name}' 不存在")


@app.command(name="edit")
def edit_config() -> None:
    """使用vim编辑配置文件"""
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




@app.command(name="show")
def show_config(
    name: Annotated[str, typer.Argument(help="配置名称", autocompletion=complete_config_names)]
) -> None:
    """显示配置详情"""
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


@app.command(name="model-add")
def add_model(
    config_name: Annotated[str, typer.Argument(help="配置名称", autocompletion=complete_config_names)],
    model_name: Annotated[str, typer.Argument(help="模型名称")],
    model_id: Annotated[str, typer.Option(help="模型ID")],
    small_fast_model: Annotated[str, typer.Option(help="快速小模型ID")] = "",
    description: Annotated[str, typer.Option(help="模型描述")] = "",
    set_default: Annotated[bool, typer.Option(help="设置为默认模型")] = False
) -> None:
    """为配置添加模型"""
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


@app.command(name="model-remove")
def remove_model(
    config_model: Annotated[str, typer.Argument(help="配置:模型", autocompletion=complete_config_model_names)]
) -> None:
    """从配置中删除模型"""
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


@app.command(name="model-list")
def list_models(
    config_name: Annotated[str, typer.Argument(help="配置名称", autocompletion=complete_config_names)]
) -> None:
    """列出配置中的所有模型"""
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


@app.command(name="model-set-default")
def set_default_model(
    config_model: Annotated[str, typer.Argument(help="配置:模型", autocompletion=complete_config_model_names)]
) -> None:
    """设置配置的默认模型"""
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



@app.command(name="run")
def use_config(
    config_model: Annotated[Optional[str], typer.Argument(help="配置:模型", autocompletion=complete_config_model_names)] = None,
    args: Annotated[Optional[str], typer.Option(help="传递给Claude Code的参数")] = None
) -> None:
    """使用指定配置启动Claude Code（无参数时使用默认配置）"""
    
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


@app.command(name="default")
def set_default_config(
    name: Annotated[Optional[str], typer.Argument(help="配置名称", autocompletion=complete_config_names)] = None
) -> None:
    """设置或显示默认配置"""
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


@app.command(name="current")
def current_config() -> None:
    """显示当前环境变量和默认配置"""
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


def main():
    """主函数入口"""
    app()


if __name__ == "__main__":
    main()