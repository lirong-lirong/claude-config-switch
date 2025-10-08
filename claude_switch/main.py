'''
Author: lirong lirongleiyang@163.com
Date: 2025-10-08 18:47:21
LastEditors: lirong lirongleiyang@163.com
LastEditTime: 2025-10-08 19:08:14
FilePath: /claude-code-switch/claude_switch/main.py
Description:

Copyright (c) 2025 by lirong, All Rights Reserved.
'''

"""
Claude Code切换器主程序 - 支持多模型版本
"""
import typer
from typing import Optional, List
from typing_extensions import Annotated
from claude_switch.complete import complete_model_names, complete_config_model_names, complete_config_names

app = typer.Typer(no_args_is_help=True, help="Claude Code Config Switch", rich_markup_mode="rich")

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
    from claude_switch.commands import add_config_impl
    add_config_impl(name, api_key, base_url, timeout_ms, disable_nonessential_traffic, description)


@app.command(name="list")
@app.command(name="ls")
def list_configs() -> None:
    """[bold green]列出所有配置[/bold green]

    显示所有已保存的API配置及其详细信息。

    [bold]示例:[/bold]
    claude-switch list
    claude-switch ls
    """
    from claude_switch.commands import list_configs_impl
    list_configs_impl()


@app.command(name="remove")
@app.command(name="rm")
def remove_config(
    name: Annotated[str, typer.Argument(help="配置名称", autocompletion=complete_config_names)]
) -> None:
    """删除配置"""
    from claude_switch.commands import remove_config_impl
    remove_config_impl(name)


@app.command(name="edit")
def edit_config() -> None:
    """使用vim编辑配置文件"""
    from claude_switch.commands import edit_config_impl
    edit_config_impl()


@app.command(name="show")
def show_config(
    name: Annotated[str, typer.Argument(help="配置名称", autocompletion=complete_config_names)]
) -> None:
    """显示配置详情"""
    from claude_switch.commands import show_config_impl
    show_config_impl(name)


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
    from claude_switch.commands import add_model_impl
    add_model_impl(config_name, model_name, model_id, small_fast_model, description, set_default)


@app.command(name="model-remove")
def remove_model(
    config_model: Annotated[str, typer.Argument(help="配置:模型", autocompletion=complete_config_model_names)]
) -> None:
    """从配置中删除模型"""
    from claude_switch.commands import remove_model_impl
    remove_model_impl(config_model)


@app.command(name="model-list")
def list_models(
    config_name: Annotated[str, typer.Argument(help="配置名称", autocompletion=complete_config_names)]
) -> None:
    """列出配置中的所有模型"""
    from claude_switch.commands import list_models_impl
    list_models_impl(config_name)


@app.command(name="model-set-default")
def set_default_model(
    config_model: Annotated[str, typer.Argument(help="配置:模型", autocompletion=complete_config_model_names)]
) -> None:
    """设置配置的默认模型"""
    from claude_switch.commands import set_default_model_impl
    set_default_model_impl(config_model)



@app.command(name="run")
def use_config(
    config_model: Annotated[Optional[str], typer.Argument(help="配置:模型", autocompletion=complete_config_model_names)] = None,
    args: Annotated[Optional[str], typer.Option(help="传递给Claude Code的参数")] = None
) -> None:
    """使用指定配置启动Claude Code（无参数时使用默认配置）"""
    from claude_switch.commands import use_config_impl
    use_config_impl(config_model, args)


@app.command(name="default")
def set_default_config(
    name: Annotated[Optional[str], typer.Argument(help="配置名称", autocompletion=complete_config_names)] = None
) -> None:
    """设置或显示默认配置"""
    from claude_switch.commands import set_default_config_impl
    set_default_config_impl(name)


@app.command(name="current")
def current_config() -> None:
    """显示当前环境变量和默认配置"""
    from claude_switch.commands import current_config_impl
    current_config_impl()


def main():
    """主函数入口"""
    app()


if __name__ == "__main__":
    main()