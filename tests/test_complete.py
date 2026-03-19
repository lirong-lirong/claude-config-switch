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
        model1 = ModelConfig(name="chat", model="deepseek-chat", description="Chat model")
        model2 = ModelConfig(name="reasoner", model="deepseek-reasoner", description="Reasoner model")

        config = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model1, "reasoner": model2},
            default_model="chat"
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_config_model_names(""))

        assert len(results) == 2
        assert any(r[0] == "deepseek:chat" for r in results)
        assert any(r[0] == "deepseek:reasoner" for r in results)

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_with_config_prefix(self, mock_manager):
        """Test completing config:model names with config prefix."""
        model = ModelConfig(name="chat", model="deepseek-chat")

        config1 = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model}
        )
        config2 = ClaudeConfig(
            name="anthropic",
            api_key="sk-ant-test",
            base_url="https://api.anthropic.com",
            models={"sonnet": ModelConfig(name="sonnet", model="claude-sonnet")}
        )
        mock_manager.list_configs.return_value = [config1, config2]

        results = list(complete_config_model_names("deep"))

        assert len(results) == 1
        assert results[0][0] == "deepseek:chat"

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_with_full_prefix(self, mock_manager):
        """Test completing config:model names with full config:model prefix."""
        model1 = ModelConfig(name="chat", model="deepseek-chat")
        model2 = ModelConfig(name="coder", model="deepseek-coder")

        config = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model1, "coder": model2}
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_config_model_names("deepseek:c"))

        assert len(results) == 2
        assert any(r[0] == "deepseek:chat" for r in results)
        assert any(r[0] == "deepseek:coder" for r in results)

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_default_marker(self, mock_manager):
        """Test completing config:model names includes default marker."""
        model = ModelConfig(name="chat", model="deepseek-chat")

        config = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model},
            default_model="chat"
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_config_model_names(""))

        assert len(results) == 1
        assert "(默认)" in results[0][1]

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_with_description(self, mock_manager):
        """Test completing config:model names includes description."""
        model = ModelConfig(
            name="chat",
            model="deepseek-chat",
            description="Chat model"
        )

        config = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model}
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_config_model_names(""))

        assert len(results) == 1
        assert "Chat model" in results[0][1]

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_no_match(self, mock_manager):
        """Test completing config:model names with no matches."""
        model = ModelConfig(name="chat", model="deepseek-chat")

        config = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model}
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_config_model_names("anthropic:"))

        assert len(results) == 0

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_model_names_empty_configs(self, mock_manager):
        """Test completing config:model names with empty configs."""
        mock_manager.list_configs.return_value = []

        results = list(complete_config_model_names(""))

        assert len(results) == 0
