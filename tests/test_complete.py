"""Tests for complete.py module."""
import pytest
from unittest.mock import patch
from claude_switch.complete import complete_config_model_names
from claude_switch.config import ClaudeConfig, ModelConfig


class TestCompleteConfigModelNames:
    """Tests for complete_config_model_names function."""

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_empty_input(self, mock_manager):
        """Test completing config:model names with empty input."""
        model1 = ModelConfig(model_id="deepseek-chat", description="Chat model")
        model2 = ModelConfig(model_id="deepseek-reasoner", description="Reasoner model")

        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://api.test.com",
            default_model="chat"
        )
        config.add_model("chat", model1)
        config.add_model("reasoner", model2)
        mock_manager.list_configs.return_value = {"deepseek": config}

        results = list(complete_config_model_names(""))

        assert len(results) == 2
        assert any(r[0] == "deepseek:chat" for r in results)
        assert any(r[0] == "deepseek:reasoner" for r in results)

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_with_config_prefix(self, mock_manager):
        """Test completing config:model names with config prefix."""
        model = ModelConfig(model_id="deepseek-chat")

        config1 = ClaudeConfig(
            api_key="sk-test",
            base_url="https://api.test.com"
        )
        config1.add_model("chat", model)

        config2 = ClaudeConfig(
            api_key="sk-ant-test",
            base_url="https://api.anthropic.com"
        )
        config2.add_model("sonnet", ModelConfig(model_id="claude-sonnet"))

        mock_manager.list_configs.return_value = {"deepseek": config1, "anthropic": config2}

        results = list(complete_config_model_names("deep"))

        assert len(results) == 1
        assert results[0][0] == "deepseek:chat"

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_with_full_prefix(self, mock_manager):
        """Test completing config:model names with full config:model prefix."""
        model1 = ModelConfig(model_id="deepseek-chat")
        model2 = ModelConfig(model_id="deepseek-coder")

        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://api.test.com"
        )
        config.add_model("chat", model1)
        config.add_model("coder", model2)
        mock_manager.list_configs.return_value = {"deepseek": config}

        results = list(complete_config_model_names("deepseek:c"))

        assert len(results) == 2
        assert any(r[0] == "deepseek:chat" for r in results)
        assert any(r[0] == "deepseek:coder" for r in results)

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_default_marker(self, mock_manager):
        """Test completing config:model names includes default marker."""
        model = ModelConfig(model_id="deepseek-chat")

        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://api.test.com",
            default_model="chat"
        )
        config.add_model("chat", model)
        mock_manager.list_configs.return_value = {"deepseek": config}

        results = list(complete_config_model_names(""))

        assert len(results) == 1
        assert "(默认)" in results[0][1]

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_with_description(self, mock_manager):
        """Test completing config:model names includes description."""
        model = ModelConfig(
            model_id="deepseek-chat",
            description="Chat model"
        )

        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://api.test.com"
        )
        config.add_model("chat", model)
        mock_manager.list_configs.return_value = {"deepseek": config}

        results = list(complete_config_model_names(""))

        assert len(results) == 1
        assert "Chat model" in results[0][1]

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_no_match(self, mock_manager):
        """Test completing config:model names with no matches."""
        model = ModelConfig(model_id="deepseek-chat")

        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://api.test.com"
        )
        config.add_model("chat", model)
        mock_manager.list_configs.return_value = {"deepseek": config}

        results = list(complete_config_model_names("anthropic:"))

        assert len(results) == 0

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_empty_configs(self, mock_manager):
        """Test completing config:model names with empty configs."""
        mock_manager.list_configs.return_value = {}

        results = list(complete_config_model_names(""))

        assert len(results) == 0
