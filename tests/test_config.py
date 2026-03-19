"""Tests for config.py module."""
import yaml
import pytest
from pathlib import Path
from claude_switch.config import ModelConfig, ClaudeConfig, ConfigManager


class TestModelConfig:
    """Tests for ModelConfig dataclass."""

    def test_model_config_creation(self):
        """Test creating a ModelConfig instance."""
        model = ModelConfig(
            model_id="test-model-id",
            small_fast_model="test-small-model",
            description="Test description"
        )
        assert model.model_id == "test-model-id"
        assert model.small_fast_model == "test-small-model"
        assert model.description == "Test description"

    def test_model_config_defaults(self):
        """Test ModelConfig with default values."""
        model = ModelConfig(model_id="test-id")
        assert model.small_fast_model == ""
        assert model.description == ""


class TestClaudeConfig:
    """Tests for ClaudeConfig dataclass."""

    def test_claude_config_creation(self, sample_model_config):
        """Test creating a ClaudeConfig instance."""
        config = ClaudeConfig(
            api_key="sk-test-123",
            base_url="https://api.test.com",
            timeout_ms=600000,
            disable_nonessential_traffic=True,
            description="Test config"
        )
        config.add_model("test-model", sample_model_config)
        config.default_model = "test-model"
        assert config.api_key == "sk-test-123"
        assert config.base_url == "https://api.test.com"
        assert config.timeout_ms == 600000
        assert config.disable_nonessential_traffic is True
        assert config.description == "Test config"
        assert len(config.models) == 1
        assert config.default_model == "test-model"

    def test_claude_config_defaults(self):
        """Test ClaudeConfig with default values."""
        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://test.com"
        )
        assert config.timeout_ms == 600000
        assert config.disable_nonessential_traffic is True
        assert config.description == ""
        assert config.models == {}
        assert config.default_model == ""

    def test_post_init_sets_default_model(self, sample_model_config):
        """Test __post_init__ automatically sets default model."""
        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://test.com"
        )
        config.add_model("model1", sample_model_config)
        assert config.default_model == "model1"

    def test_add_model_success(self):
        """Test adding a model successfully."""
        config = ClaudeConfig(api_key="sk-test", base_url="https://test.com")
        model = ModelConfig(model_id="new-model-id")

        result = config.add_model("new-model", model)
        assert result is True
        assert "new-model" in config.models
        assert config.default_model == "new-model"

    def test_add_model_duplicate(self, sample_model_config):
        """Test adding a duplicate model fails."""
        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://test.com"
        )
        config.add_model("test-model", sample_model_config)

        result = config.add_model("test-model", sample_model_config)
        assert result is False

    def test_remove_model_success(self, sample_model_config):
        """Test removing a model successfully."""
        model2 = ModelConfig(model_id="model2-id")
        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://test.com",
            default_model="model1"
        )
        config.add_model("model1", sample_model_config)
        config.add_model("model2", model2)

        result = config.remove_model("model1")
        assert result is True
        assert "model1" not in config.models
        assert config.default_model == "model2"

    def test_remove_model_nonexistent(self, sample_claude_config):
        """Test removing a nonexistent model fails."""
        result = sample_claude_config.remove_model("nonexistent")
        assert result is False

    def test_remove_last_model(self, sample_model_config):
        """Test removing the last model clears default."""
        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://test.com"
        )
        config.add_model("model1", sample_model_config)

        result = config.remove_model("model1")
        assert result is True
        assert config.models == {}
        assert config.default_model == ""

    def test_get_model_exists(self, sample_claude_config):
        """Test getting an existing model."""
        model = sample_claude_config.get_model("test-model")
        assert model is not None
        assert model.model_id == "test-model-id"

    def test_get_model_not_exists(self, sample_claude_config):
        """Test getting a nonexistent model."""
        model = sample_claude_config.get_model("nonexistent")
        assert model is None

    def test_set_default_model_success(self, sample_claude_config):
        """Test setting default model successfully."""
        result = sample_claude_config.set_default_model("test-model")
        assert result is True
        assert sample_claude_config.default_model == "test-model"

    def test_set_default_model_nonexistent(self, sample_claude_config):
        """Test setting default to nonexistent model fails."""
        result = sample_claude_config.set_default_model("nonexistent")
        assert result is False

    def test_to_env_vars_with_specified_model(self, sample_claude_config):
        """Test converting config to environment variables with specified model."""
        env_vars = sample_claude_config.to_env_vars("test-model")

        assert env_vars["ANTHROPIC_API_KEY"] == "sk-test-key-123"
        assert env_vars["ANTHROPIC_BASE_URL"] == "https://api.test.com"
        assert env_vars["ANTHROPIC_MODEL"] == "test-model-id"
        assert env_vars["ANTHROPIC_SMALL_FAST_MODEL"] == "test-small-model-id"
        assert env_vars["API_TIMEOUT_MS"] == "600000"
        assert env_vars["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] == "1"

    def test_to_env_vars_with_default_model(self, sample_claude_config):
        """Test converting config to environment variables using default model."""
        env_vars = sample_claude_config.to_env_vars()

        assert env_vars["ANTHROPIC_MODEL"] == "test-model-id"

    def test_to_env_vars_nonexistent_model(self, sample_claude_config):
        """Test converting config with nonexistent model raises error."""
        with pytest.raises(ValueError, match="模型 'nonexistent' 不存在"):
            sample_claude_config.to_env_vars("nonexistent")

    def test_to_env_vars_small_fast_model_fallback(self):
        """Test small_fast_model falls back to main model if empty."""
        model = ModelConfig(model_id="main-model", small_fast_model="")
        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://test.com"
        )
        config.add_model("model", model)

        env_vars = config.to_env_vars()
        assert env_vars["ANTHROPIC_SMALL_FAST_MODEL"] == "main-model"

    def test_to_env_vars_disable_traffic_false(self):
        """Test environment variable when disable_nonessential_traffic is False."""
        model = ModelConfig(model_id="main-model")
        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://test.com",
            disable_nonessential_traffic=False
        )
        config.add_model("model", model)

        env_vars = config.to_env_vars()
        assert env_vars["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] == "0"


class TestConfigManager:
    """Tests for ConfigManager class."""

    def test_config_manager_initialization(self, temp_config_dir):
        """Test ConfigManager initialization creates directory."""
        manager = ConfigManager(str(temp_config_dir))
        assert manager.config_dir.exists()
        assert manager.config_file == temp_config_dir / "config.yaml"

    def test_add_config_success(self, temp_config_dir, sample_claude_config):
        """Test adding a config successfully."""
        manager = ConfigManager(str(temp_config_dir))
        result = manager.add_config("test-config", sample_claude_config)

        assert result is True
        assert manager.config_exists("test-config")

    def test_add_config_duplicate(self, temp_config_dir, sample_claude_config):
        """Test adding a duplicate config fails."""
        manager = ConfigManager(str(temp_config_dir))
        manager.add_config("test-config", sample_claude_config)

        result = manager.add_config("test-config", sample_claude_config)
        assert result is False

    def test_update_config_success(self, temp_config_dir, sample_claude_config):
        """Test updating an existing config."""
        manager = ConfigManager(str(temp_config_dir))
        manager.add_config("test-config", sample_claude_config)

        sample_claude_config.description = "Updated description"
        result = manager.update_config("test-config", sample_claude_config)

        assert result is True
        updated = manager.get_config("test-config")
        assert updated.description == "Updated description"

    def test_update_config_nonexistent(self, temp_config_dir, sample_claude_config):
        """Test updating a nonexistent config fails."""
        manager = ConfigManager(str(temp_config_dir))
        result = manager.update_config("test-config", sample_claude_config)
        assert result is False

    def test_remove_config_success(self, temp_config_dir, sample_claude_config):
        """Test removing a config successfully."""
        manager = ConfigManager(str(temp_config_dir))
        manager.add_config("test-config", sample_claude_config)

        result = manager.remove_config("test-config")
        assert result is True
        assert not manager.config_exists("test-config")

    def test_remove_config_nonexistent(self, temp_config_dir):
        """Test removing a nonexistent config fails."""
        manager = ConfigManager(str(temp_config_dir))
        result = manager.remove_config("nonexistent")
        assert result is False

    def test_get_config_exists(self, temp_config_dir, sample_claude_config):
        """Test getting an existing config."""
        manager = ConfigManager(str(temp_config_dir))
        manager.add_config("test-config", sample_claude_config)

        config = manager.get_config("test-config")
        assert config is not None

    def test_get_config_not_exists(self, temp_config_dir):
        """Test getting a nonexistent config."""
        manager = ConfigManager(str(temp_config_dir))
        config = manager.get_config("nonexistent")
        assert config is None

    def test_list_configs(self, temp_config_dir, sample_claude_config):
        """Test listing all configs."""
        manager = ConfigManager(str(temp_config_dir))
        manager.add_config("test-config", sample_claude_config)

        config2 = ClaudeConfig(api_key="sk-test2", base_url="https://test2.com")
        manager.add_config("config2", config2)

        configs = manager.list_configs()
        assert len(configs) == 2
        assert "test-config" in configs
        assert "config2" in configs

    def test_config_exists(self, temp_config_dir, sample_claude_config):
        """Test checking if config exists."""
        manager = ConfigManager(str(temp_config_dir))
        manager.add_config("test-config", sample_claude_config)

        assert manager.config_exists("test-config") is True
        assert manager.config_exists("nonexistent") is False

    def test_set_default_config_success(self, temp_config_dir, sample_claude_config):
        """Test setting default config successfully."""
        manager = ConfigManager(str(temp_config_dir))
        manager.add_config("test-config", sample_claude_config)

        result = manager.set_default_config("test-config")
        assert result is True
        assert manager.get_default_config_name() == "test-config"

    def test_set_default_config_nonexistent(self, temp_config_dir):
        """Test setting default to nonexistent config fails."""
        manager = ConfigManager(str(temp_config_dir))
        result = manager.set_default_config("nonexistent")
        assert result is False

    def test_get_default_config(self, temp_config_dir, sample_claude_config):
        """Test getting default config."""
        manager = ConfigManager(str(temp_config_dir))
        manager.add_config("test-config", sample_claude_config)
        manager.set_default_config("test-config")

        default = manager.get_default_config()
        assert default is not None
        assert manager.get_default_config_name() == "test-config"

    def test_get_default_config_none(self, temp_config_dir):
        """Test getting default config when none is set."""
        manager = ConfigManager(str(temp_config_dir))
        default = manager.get_default_config()
        assert default is None

    def test_get_config_file_path(self, temp_config_dir):
        """Test getting config file path."""
        manager = ConfigManager(str(temp_config_dir))
        path = manager.get_config_file_path()
        assert path == str(temp_config_dir / "config.yaml")

    def test_persistence(self, temp_config_dir, sample_claude_config):
        """Test that configs persist across manager instances."""
        manager1 = ConfigManager(str(temp_config_dir))
        manager1.add_config("test-config", sample_claude_config)
        manager1.set_default_config("test-config")

        manager2 = ConfigManager(str(temp_config_dir))
        config = manager2.get_config("test-config")
        assert config is not None
        assert manager2.get_default_config_name() == "test-config"

    def test_load_corrupted_config(self, temp_config_dir):
        """Test loading a corrupted config file initializes empty."""
        config_file = temp_config_dir / "config.yaml"
        config_file.write_text("invalid: yaml: [[[", encoding='utf-8')

        manager = ConfigManager(str(temp_config_dir))
        assert len(manager.list_configs()) == 0
        assert manager.get_default_config_name() == ""

    def test_create_example_config(self, temp_config_dir):
        """Test creating example config file."""
        manager = ConfigManager(str(temp_config_dir))
        manager.create_example_config()

        assert manager.config_file.exists()

        # Verify example config content
        with open(manager.config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        assert "configs" in data
        assert "default_config" in data
        assert "deepseek" in data["configs"]
        assert "anthropic" in data["configs"]

    def test_save_and_load_with_models(self, temp_config_dir):
        """Test saving and loading config with multiple models."""
        manager = ConfigManager(str(temp_config_dir))

        config = ClaudeConfig(
            api_key="sk-test",
            base_url="https://test.com"
        )

        model1 = ModelConfig(model_id="model1-id")
        model2 = ModelConfig(model_id="model2-id", small_fast_model="model1-id")

        config.add_model("model1", model1)
        config.add_model("model2", model2)
        config.set_default_model("model2")

        manager.add_config("multi-model", config)

        # Load in new manager instance
        manager2 = ConfigManager(str(temp_config_dir))
        loaded = manager2.get_config("multi-model")

        assert loaded is not None
        assert len(loaded.models) == 2
        assert "model1" in loaded.models
        assert "model2" in loaded.models
        assert loaded.default_model == "model2"
        assert loaded.models["model2"].small_fast_model == "model1-id"
