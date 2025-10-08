'''
Author: lirong lirongleiyang@163.com
Date: 2025-10-08 18:53:23
LastEditors: lirong lirongleiyang@163.com
LastEditTime: 2025-10-08 19:08:24
FilePath: /claude-code-switch/claude_switch/complete.py
Description: 

Copyright (c) 2025 by lirong, All Rights Reserved. 
'''
""" 命令行补全功能 """

from claude_switch.config import config_manager
from rich.console import Console
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