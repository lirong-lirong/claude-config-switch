"""
Claude Code配置管理模块
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ModelConfig:
    """模型配置类"""
    name: str
    model: str
    small_fast_model: str = ""
    description: str = ""


@dataclass
class ClaudeConfig:
    """Claude Code配置类"""
    name: str
    api_key: str
    base_url: str
    timeout_ms: int = 600000
    disable_nonessential_traffic: bool = True
    description: str = ""
    models: Dict[str, ModelConfig] = None
    default_model: str = ""

    def __post_init__(self):
        if self.models is None:
            self.models = {}
        if not self.default_model and self.models:
            self.default_model = next(iter(self.models.keys()))

    def add_model(self, model_config: ModelConfig) -> bool:
        """添加模型配置"""
        if model_config.name in self.models:
            return False
        self.models[model_config.name] = model_config
        if not self.default_model:
            self.default_model = model_config.name
        return True

    def remove_model(self, model_name: str) -> bool:
        """删除模型配置"""
        if model_name not in self.models:
            return False
        del self.models[model_name]
        if self.default_model == model_name:
            self.default_model = next(iter(self.models.keys())) if self.models else ""
        return True

    def get_model(self, model_name: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        return self.models.get(model_name)

    def set_default_model(self, model_name: str) -> bool:
        """设置默认模型"""
        if model_name not in self.models:
            return False
        self.default_model = model_name
        return True

    def to_env_vars(self, model_name: str = None) -> Dict[str, str]:
        """将配置转换为环境变量字典"""
        if not model_name:
            model_name = self.default_model

        model_config = self.models.get(model_name)
        if not model_config:
            raise ValueError(f"模型 '{model_name}' 不存在")

        return {
            "ANTHROPIC_API_KEY": self.api_key,
            "ANTHROPIC_BASE_URL": self.base_url,
            "ANTHROPIC_MODEL": model_config.model,
            "ANTHROPIC_SMALL_FAST_MODEL": model_config.small_fast_model or model_config.model,
            "API_TIMEOUT_MS": str(self.timeout_ms),
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1" if self.disable_nonessential_traffic else "0"
        }


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".config" / "claude-code-switch"

        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._configs: Dict[str, ClaudeConfig] = {}
        self._load_configs()

    def _load_configs(self):
        """从文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, config_data in data.items():
                        # 处理模型配置
                        models_data = config_data.pop('models', {})
                        config = ClaudeConfig(**config_data)

                        # 添加模型配置
                        for model_name, model_data in models_data.items():
                            model_config = ModelConfig(**model_data)
                            config.add_model(model_config)

                        self._configs[name] = config
            except (json.JSONDecodeError, KeyError, TypeError):
                # 如果配置文件损坏，重新初始化
                self._configs = {}

    def _save_configs(self):
        """保存配置到文件"""
        data = {name: asdict(config) for name, config in self._configs.items()}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_config(self, config: ClaudeConfig) -> bool:
        """添加配置"""
        if config.name in self._configs:
            return False
        self._configs[config.name] = config
        self._save_configs()
        return True

    def update_config(self, config: ClaudeConfig) -> bool:
        """更新配置"""
        if config.name not in self._configs:
            return False
        self._configs[config.name] = config
        self._save_configs()
        return True

    def remove_config(self, name: str) -> bool:
        """删除配置"""
        if name not in self._configs:
            return False
        del self._configs[name]
        self._save_configs()
        return True

    def get_config(self, name: str) -> Optional[ClaudeConfig]:
        """获取配置"""
        return self._configs.get(name)

    def list_configs(self) -> List[ClaudeConfig]:
        """列出所有配置"""
        return list(self._configs.values())

    def config_exists(self, name: str) -> bool:
        """检查配置是否存在"""
        return name in self._configs