"""命令行补全功能"""

from claude_switch.config import config_manager


def complete_config_model_names(incomplete: str):
    """为 config:model 格式提供自动补全"""
    configs = config_manager.list_configs()

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

    if not incomplete:
        for model_name, help_text in all_models:
            yield (model_name, help_text)
    else:
        for model_name, help_text in all_models:
            if model_name.startswith(incomplete):
                yield (model_name, help_text)
