"""Tests for complete.py module."""
import pytest
from unittest.mock import patch, Mock
from claude_switch.complete import (
    complete_config_names,
    complete_model_names,
    complete_config_model_names
)
from claude_switch.config import ClaudeConfig, ModelConfig


class TestCompleteConfigNames:
    """Tests for complete_config_names function."""

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_names_empty_input(self, mock_manager):
        """Test completing config names with empty input."""
        config1 = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.deepseek.com",
            description="DeepSeek API"
        )
        config2 = ClaudeConfig(
            name="anthropic",
            api_key="sk-ant-test",
            base_url="https://api.anthropic.com",
            description="Anthropic API"
        )
        mock_manager.list_configs.return_value = [config1, config2]

        results = list(complete_config_names(""))

        assert len(results) == 2
        assert ("deepseek", "DeepSeek API") in results
        assert ("anthropic", "Anthropic API") in results

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_names_with_prefix(self, mock_manager):
        """Test completing config names with prefix."""
        config1 = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.deepseek.com",
            description="DeepSeek API"
        )
        config2 = ClaudeConfig(
            name="anthropic",
            api_key="sk-ant-test",
            base_url="https://api.anthropic.com",
            description="Anthropic API"
        )
        mock_manager.list_configs.return_value = [config1, config2]

        results = list(complete_config_names("deep"))

        assert len(results) == 1
        assert ("deepseek", "DeepSeek API") in results

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_names_no_description(self, mock_manager):
        """Test completing config names without description."""
        config = ClaudeConfig(
            name="test",
            api_key="sk-test",
            base_url="https://api.test.com"
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_config_names("test"))

        assert len(results) == 1
        assert results[0][0] == "test"
        assert "https://api.test.com" in results[0][1]

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_names_no_match(self, mock_manager):
        """Test completing config names with no matches."""
        config = ClaudeConfig(
            name="test",
            api_key="sk-test",
            base_url="https://api.test.com"
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_config_names("nonexistent"))

        assert len(results) == 0

    @patch('claude_switch.complete.config_manager')
    def test_complete_config_names_empty_list(self, mock_manager):
        """Test completing config names with empty config list."""
        mock_manager.list_configs.return_value = []

        results = list(complete_config_names(""))

        assert len(results) == 0


class TestCompleteModelNames:
    """Tests for complete_model_names function."""

    @patch('claude_switch.complete.config_manager')
    def test_complete_model_names_empty_input(self, mock_manager):
        """Test completing model names with empty input."""
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

        results = list(complete_model_names(""))

        assert len(results) == 2
        assert any(r[0] == "deepseek:chat" for r in results)
        assert any(r[0] == "deepseek:reasoner" for r in results)

    @patch('claude_switch.complete.config_manager')
    def test_complete_model_names_with_prefix(self, mock_manager):
        """Test completing model names with prefix."""
        model1 = ModelConfig(name="chat", model="deepseek-chat")
        model2 = ModelConfig(name="reasoner", model="deepseek-reasoner")

        config = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model1, "reasoner": model2},
            default_model="chat"
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_model_names("deepseek:c"))

        assert len(results) == 1
        assert results[0][0] == "deepseek:chat"

    @patch('claude_switch.complete.config_manager')
    def test_complete_model_names_default_indicator(self, mock_manager):
        """Test completing model names shows default indicator."""
        model = ModelConfig(name="chat", model="deepseek-chat")

        config = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model},
            default_model="chat"
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_model_names(""))

        assert len(results) == 1
        assert "(默认)" in results[0][1]

    @patch('claude_switch.complete.config_manager')
    def test_complete_model_names_with_description(self, mock_manager):
        """Test completing model names includes description."""
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

        results = list(complete_model_names(""))

        assert len(results) == 1
        assert "Chat model" in results[0][1]

    @patch('claude_switch.complete.config_manager')
    def test_complete_model_names_multiple_configs(self, mock_manager):
        """Test completing model names from multiple configs."""
        model1 = ModelConfig(name="chat", model="deepseek-chat")
        model2 = ModelConfig(name="sonnet", model="claude-3-5-sonnet")

        config1 = ClaudeConfig(
            name="deepseek",
            api_key="sk-test",
            base_url="https://api.test.com",
            models={"chat": model1}
        )
        config2 = ClaudeConfig(
            name="anthropic",
            api_key="sk-ant-test",
            base_url="https://api.anthropic.com",
            models={"sonnet": model2}
        )
        mock_manager.list_configs.return_value = [config1, config2]

        results = list(complete_model_names(""))

        assert len(results) == 2
        assert any(r[0] == "deepseek:chat" for r in results)
        assert any(r[0] == "anthropic:sonnet" for r in results)

    @patch('claude_switch.complete.config_manager')
    def test_complete_model_names_no_models(self, mock_manager):
        """Test completing model names when config has no models."""
        config = ClaudeConfig(
            name="test",
            api_key="sk-test",
            base_url="https://api.test.com"
        )
        mock_manager.list_configs.return_value = [config]

        results = list(complete_model_names(""))

        assert len(results) == 0


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
