"""Tests for commands.py module."""
import pytest
from unittest.mock import patch
from claude_switch.commands import (
    list_configs_impl,
    edit_config_impl,
    use_config_impl,
    current_config_impl
)
from claude_switch.config import ClaudeConfig, ModelConfig


class TestListConfigsImpl:
    """Tests for list_configs_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_configs_empty(self, mock_print, mock_manager):
        """Test listing configs when none exist."""
        mock_manager.get_load_error.return_value = None
        mock_manager.list_configs.return_value = {}

        list_configs_impl()

        mock_manager.list_configs.assert_called_once()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_configs_with_data(self, mock_print, mock_manager, sample_claude_config):
        """Test listing configs with data shows details and models."""
        mock_manager.get_load_error.return_value = None
        mock_manager.list_configs.return_value = {"test-config": sample_claude_config}

        list_configs_impl()

        mock_manager.list_configs.assert_called_once()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_configs_no_models(self, mock_print, mock_manager):
        """Test listing configs when config has no models."""
        mock_manager.get_load_error.return_value = None
        config = ClaudeConfig(api_key="sk-test", base_url="https://test.com")
        mock_manager.list_configs.return_value = {"test": config}

        list_configs_impl()

        mock_manager.list_configs.assert_called_once()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_configs_with_load_error(self, mock_print, mock_manager):
        """Test listing configs when config file has a load error."""
        mock_manager.get_load_error.return_value = "Expecting value: line 1 column 1 (char 0)"

        list_configs_impl()

        mock_manager.list_configs.assert_not_called()


class TestEditConfigImpl:
    """Tests for edit_config_impl function."""

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.os.path.exists')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_edit_config_file_exists(self, mock_print, mock_manager, mock_exists, mock_subprocess):
        """Test editing existing config file."""
        mock_manager.get_config_file_path.return_value = "/path/to/config.yaml"
        mock_exists.return_value = True

        edit_config_impl()

        mock_subprocess.assert_called_once_with(["vim", "/path/to/config.yaml"])

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.os.path.exists')
    @patch('claude_switch.commands.os.makedirs')
    @patch('claude_switch.commands.os.path.dirname')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_edit_config_file_not_exists(self, mock_print, mock_manager, mock_dirname,
                                          mock_makedirs, mock_exists, mock_subprocess):
        """Test editing when config file doesn't exist."""
        mock_manager.get_config_file_path.return_value = "/path/to/config.yaml"
        mock_exists.return_value = False
        mock_dirname.return_value = "/path/to"

        edit_config_impl()

        mock_manager.create_example_config.assert_called_once()
        mock_subprocess.assert_called_once_with(["vim", "/path/to/config.yaml"])

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.os.path.exists')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_edit_config_vim_not_found(self, mock_print, mock_manager, mock_exists, mock_subprocess):
        """Test editing when vim is not found."""
        mock_manager.get_config_file_path.return_value = "/path/to/config.yaml"
        mock_exists.return_value = True
        mock_subprocess.side_effect = FileNotFoundError()

        edit_config_impl()

        mock_subprocess.assert_called_once()


class TestUseConfigImpl:
    """Tests for use_config_impl function."""

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_with_default(self, mock_print, mock_manager, mock_subprocess, sample_claude_config):
        """Test using default config."""
        mock_manager.get_default_config.return_value = sample_claude_config
        mock_manager.get_default_config_name.return_value = "test-config"

        use_config_impl()

        mock_manager.get_default_config.assert_called_once()
        mock_subprocess.assert_called_once()

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_no_default(self, mock_print, mock_manager, mock_subprocess):
        """Test using config when no default is set."""
        mock_manager.get_default_config.return_value = None

        use_config_impl()

        mock_manager.get_default_config.assert_called_once()
        mock_subprocess.assert_not_called()

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_with_config_name(self, mock_print, mock_manager, mock_subprocess, sample_claude_config):
        """Test using config with specific config name."""
        mock_manager.get_config.return_value = sample_claude_config

        use_config_impl("test-config")

        mock_manager.get_config.assert_called_once_with("test-config")
        mock_subprocess.assert_called_once()

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_with_config_model_format(self, mock_print, mock_manager, mock_subprocess, sample_claude_config):
        """Test using config with config:model format."""
        mock_manager.get_config.return_value = sample_claude_config

        use_config_impl("test-config:test-model")

        mock_manager.get_config.assert_called_once_with("test-config")
        mock_subprocess.assert_called_once()

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_not_exists(self, mock_print, mock_manager, mock_subprocess):
        """Test using nonexistent config."""
        mock_manager.get_config.return_value = None

        use_config_impl("nonexistent")

        mock_manager.get_config.assert_called_once_with("nonexistent")
        mock_subprocess.assert_not_called()

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_with_args(self, mock_print, mock_manager, mock_subprocess, sample_claude_config):
        """Test using config with additional args."""
        mock_manager.get_config.return_value = sample_claude_config

        use_config_impl("test-config", "--debug --verbose")

        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert "--debug" in call_args[0][0]
        assert "--verbose" in call_args[0][0]

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_no_models(self, mock_print, mock_manager, mock_subprocess):
        """Test using config with no models."""
        config = ClaudeConfig(api_key="sk-test", base_url="https://test.com")
        mock_manager.get_config.return_value = config

        use_config_impl("test")

        mock_subprocess.assert_not_called()

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_invalid_model(self, mock_print, mock_manager, mock_subprocess, sample_claude_config):
        """Test using config with invalid model name."""
        mock_manager.get_config.return_value = sample_claude_config

        use_config_impl("test-config:nonexistent-model")

        mock_subprocess.assert_not_called()


class TestCurrentConfigImpl:
    """Tests for current_config_impl function."""

    @patch('claude_switch.commands.os.environ.get')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_current_config_with_env_vars(self, mock_print, mock_manager, mock_env_get, sample_claude_config):
        """Test showing current config with environment variables."""
        mock_env_get.side_effect = lambda key: {
            "ANTHROPIC_API_KEY": "sk-test",
            "ANTHROPIC_BASE_URL": "https://test.com",
            "ANTHROPIC_MODEL": "test-model",
        }.get(key)
        mock_manager.get_default_config_name.return_value = "test-config"

        current_config_impl()

        mock_manager.get_default_config_name.assert_called_once()

    @patch('claude_switch.commands.os.environ.get')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_current_config_no_default(self, mock_print, mock_manager, mock_env_get):
        """Test showing current config when no default is set."""
        mock_env_get.return_value = None
        mock_manager.get_default_config_name.return_value = ""

        current_config_impl()

        mock_manager.get_default_config_name.assert_called_once()
