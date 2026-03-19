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
from typing import Optional
from typing_extensions import Annotated
from claude_switch.complete import complete_config_model_names

app = typer.Typer(no_args_is_help=True, help="Claude Code Config Switch", rich_markup_mode="rich")


@app.command(name="list")
@app.command(name="ls")
def list_configs() -> None:
    """[bold green]列出所有配置及其详情[/bold green]

    显示所有已保存的API配置，包括模型信息。

    [bold]示例:[/bold]
    claude-switch list
    claude-switch ls
    """
    from claude_switch.commands import list_configs_impl
    list_configs_impl()


@app.command(name="edit")
def edit_config() -> None:
    """使用vim编辑配置文件"""
    from claude_switch.commands import edit_config_impl
    edit_config_impl()


@app.command(name="run")
def use_config(
    config_model: Annotated[Optional[str], typer.Argument(help="配置:模型", autocompletion=complete_config_model_names)] = None,
    args: Annotated[Optional[str], typer.Option(help="传递给Claude Code的参数")] = None
) -> None:
    """使用指定配置启动Claude Code（无参数时使用默认配置）"""
    from claude_switch.commands import use_config_impl
    use_config_impl(config_model, args)


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