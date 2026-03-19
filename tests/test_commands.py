"""Tests for commands.py module."""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO
from claude_switch.commands import (
    add_config_impl,
    list_configs_impl,
    remove_config_impl,
    edit_config_impl,
    show_config_impl,
    add_model_impl,
    remove_model_impl,
    list_models_impl,
    set_default_model_impl,
    use_config_impl,
    set_default_config_impl,
    current_config_impl
)
from claude_switch.config import ClaudeConfig, ModelConfig


class TestAddConfigImpl:
    """Tests for add_config_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_add_config_success(self, mock_print, mock_manager):
        """Test adding a config successfully."""
        mock_manager.add_config.return_value = True

        add_config_impl(
            name="test",
            api_key="sk-test",
            base_url="https://test.com"
        )

        mock_manager.add_config.assert_called_once()
        config_arg = mock_manager.add_config.call_args[0][0]
        assert config_arg.name == "test"
        assert config_arg.api_key == "sk-test"
        assert config_arg.base_url == "https://test.com"

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_add_config_duplicate(self, mock_print, mock_manager):
        """Test adding a duplicate config."""
        mock_manager.add_config.return_value = False

        add_config_impl(
            name="test",
            api_key="sk-test",
            base_url="https://test.com"
        )

        mock_manager.add_config.assert_called_once()


class TestListConfigsImpl:
    """Tests for list_configs_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_configs_empty(self, mock_print, mock_manager):
        """Test listing configs when none exist."""
        mock_manager.list_configs.return_value = []

        list_configs_impl()

        mock_manager.list_configs.assert_called_once()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_configs_with_data(self, mock_print, mock_manager, sample_claude_config):
        """Test listing configs with data."""
        mock_manager.list_configs.return_value = [sample_claude_config]

        list_configs_impl()

        mock_manager.list_configs.assert_called_once()


class TestRemoveConfigImpl:
    """Tests for remove_config_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_remove_config_success(self, mock_print, mock_manager):
        """Test removing a config successfully."""
        mock_manager.remove_config.return_value = True

        remove_config_impl("test")

        mock_manager.remove_config.assert_called_once_with("test")

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_remove_config_not_exists(self, mock_print, mock_manager):
        """Test removing a nonexistent config."""
        mock_manager.remove_config.return_value = False

        remove_config_impl("nonexistent")

        mock_manager.remove_config.assert_called_once_with("nonexistent")


class TestEditConfigImpl:
    """Tests for edit_config_impl function."""

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.os.path.exists')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_edit_config_file_exists(self, mock_print, mock_manager, mock_exists, mock_subprocess):
        """Test editing existing config file."""
        mock_manager.get_config_file_path.return_value = "/path/to/config.json"
        mock_exists.return_value = True

        edit_config_impl()

        mock_subprocess.assert_called_once_with(["vim", "/path/to/config.json"])

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.os.path.exists')
    @patch('claude_switch.commands.os.makedirs')
    @patch('claude_switch.commands.os.path.dirname')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_edit_config_file_not_exists(self, mock_print, mock_manager, mock_dirname,
                                          mock_makedirs, mock_exists, mock_subprocess):
        """Test editing when config file doesn't exist."""
        mock_manager.get_config_file_path.return_value = "/path/to/config.json"
        mock_exists.return_value = False
        mock_dirname.return_value = "/path/to"

        edit_config_impl()

        mock_manager.create_example_config.assert_called_once()
        mock_subprocess.assert_called_once_with(["vim", "/path/to/config.json"])

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.os.path.exists')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_edit_config_vim_not_found(self, mock_print, mock_manager, mock_exists, mock_subprocess):
        """Test editing when vim is not found."""
        mock_manager.get_config_file_path.return_value = "/path/to/config.json"
        mock_exists.return_value = True
        mock_subprocess.side_effect = FileNotFoundError()

        edit_config_impl()

        mock_subprocess.assert_called_once()


class TestShowConfigImpl:
    """Tests for show_config_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_show_config_exists(self, mock_print, mock_manager, sample_claude_config):
        """Test showing an existing config."""
        mock_manager.get_config.return_value = sample_claude_config

        show_config_impl("test-config")

        mock_manager.get_config.assert_called_once_with("test-config")

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_show_config_not_exists(self, mock_print, mock_manager):
        """Test showing a nonexistent config."""
        mock_manager.get_config.return_value = None

        show_config_impl("nonexistent")

        mock_manager.get_config.assert_called_once_with("nonexistent")


class TestAddModelImpl:
    """Tests for add_model_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_add_model_success(self, mock_print, mock_manager, sample_claude_config):
        """Test adding a model successfully."""
        mock_manager.get_config.return_value = sample_claude_config

        add_model_impl(
            config_name="test-config",
            model_name="new-model",
            model_id="new-model-id"
        )

        mock_manager.get_config.assert_called_once_with("test-config")
        mock_manager.update_config.assert_called_once()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_add_model_config_not_exists(self, mock_print, mock_manager):
        """Test adding a model to nonexistent config."""
        mock_manager.get_config.return_value = None

        add_model_impl(
            config_name="nonexistent",
            model_name="model",
            model_id="model-id"
        )

        mock_manager.get_config.assert_called_once_with("nonexistent")
        mock_manager.update_config.assert_not_called()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_add_model_with_set_default(self, mock_print, mock_manager):
        """Test adding a model with set_default flag."""
        config = ClaudeConfig(name="test", api_key="sk-test", base_url="https://test.com")
        model1 = ModelConfig(name="model1", model="model1-id")
        config.add_model(model1)
        mock_manager.get_config.return_value = config

        add_model_impl(
            config_name="test",
            model_name="model2",
            model_id="model2-id",
            set_default=True
        )

        assert config.default_model == "model2"
        mock_manager.update_config.assert_called_once()


class TestRemoveModelImpl:
    """Tests for remove_model_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_remove_model_success(self, mock_print, mock_manager, sample_claude_config):
        """Test removing a model successfully."""
        mock_manager.get_config.return_value = sample_claude_config

        remove_model_impl("test-config:test-model")

        mock_manager.get_config.assert_called_once_with("test-config")
        mock_manager.update_config.assert_called_once()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_remove_model_config_not_exists(self, mock_print, mock_manager):
        """Test removing a model from nonexistent config."""
        mock_manager.get_config.return_value = None

        remove_model_impl("nonexistent:model")

        mock_manager.get_config.assert_called_once_with("nonexistent")
        mock_manager.update_config.assert_not_called()


class TestListModelsImpl:
    """Tests for list_models_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_models_success(self, mock_print, mock_manager, sample_claude_config):
        """Test listing models successfully."""
        mock_manager.get_config.return_value = sample_claude_config

        list_models_impl("test-config")

        mock_manager.get_config.assert_called_once_with("test-config")

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_models_config_not_exists(self, mock_print, mock_manager):
        """Test listing models for nonexistent config."""
        mock_manager.get_config.return_value = None

        list_models_impl("nonexistent")

        mock_manager.get_config.assert_called_once_with("nonexistent")

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_list_models_empty(self, mock_print, mock_manager):
        """Test listing models when config has no models."""
        config = ClaudeConfig(name="test", api_key="sk-test", base_url="https://test.com")
        mock_manager.get_config.return_value = config

        list_models_impl("test")

        mock_manager.get_config.assert_called_once_with("test")


class TestSetDefaultModelImpl:
    """Tests for set_default_model_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_set_default_model_success(self, mock_print, mock_manager, sample_claude_config):
        """Test setting default model successfully."""
        mock_manager.get_config.return_value = sample_claude_config

        set_default_model_impl("test-config:test-model")

        mock_manager.get_config.assert_called_once_with("test-config")
        mock_manager.update_config.assert_called_once()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_set_default_model_config_not_exists(self, mock_print, mock_manager):
        """Test setting default model for nonexistent config."""
        mock_manager.get_config.return_value = None

        set_default_model_impl("nonexistent:model")

        mock_manager.get_config.assert_called_once_with("nonexistent")
        mock_manager.update_config.assert_not_called()


class TestUseConfigImpl:
    """Tests for use_config_impl function."""

    @patch('claude_switch.commands.subprocess.run')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_use_config_with_default(self, mock_print, mock_manager, mock_subprocess, sample_claude_config):
        """Test using default config."""
        mock_manager.get_default_config.return_value = sample_claude_config

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
        config = ClaudeConfig(name="test", api_key="sk-test", base_url="https://test.com")
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


class TestSetDefaultConfigImpl:
    """Tests for set_default_config_impl function."""

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_set_default_config_success(self, mock_print, mock_manager):
        """Test setting default config successfully."""
        mock_manager.set_default_config.return_value = True

        set_default_config_impl("test")

        mock_manager.set_default_config.assert_called_once_with("test")

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_set_default_config_not_exists(self, mock_print, mock_manager):
        """Test setting default to nonexistent config."""
        mock_manager.set_default_config.return_value = False

        set_default_config_impl("nonexistent")

        mock_manager.set_default_config.assert_called_once_with("nonexistent")

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_set_default_config_show_default(self, mock_print, mock_manager, sample_claude_config):
        """Test showing current default config."""
        mock_manager.get_default_config.return_value = sample_claude_config

        set_default_config_impl()

        mock_manager.get_default_config.assert_called_once()
        mock_manager.set_default_config.assert_not_called()

    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_set_default_config_show_no_default(self, mock_print, mock_manager):
        """Test showing when no default is set."""
        mock_manager.get_default_config.return_value = None

        set_default_config_impl()

        mock_manager.get_default_config.assert_called_once()


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
        mock_manager.get_default_config.return_value = sample_claude_config

        current_config_impl()

        mock_manager.get_default_config.assert_called_once()

    @patch('claude_switch.commands.os.environ.get')
    @patch('claude_switch.commands.config_manager')
    @patch('claude_switch.commands.print')
    def test_current_config_no_default(self, mock_print, mock_manager, mock_env_get):
        """Test showing current config when no default is set."""
        mock_env_get.return_value = None
        mock_manager.get_default_config.return_value = None

        current_config_impl()

        mock_manager.get_default_config.assert_called_once()
