"""Pytest configuration and shared fixtures."""
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary config directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_config_file(temp_config_dir: Path) -> Path:
    """Create a temporary config file path."""
    return temp_config_dir / "config.yaml"


@pytest.fixture
def sample_model_config():
    """Provide a sample ModelConfig for testing."""
    from claude_switch.config import ModelConfig
    return ModelConfig(
        name="test-model",
        model="test-model-id",
        small_fast_model="test-small-model-id",
        description="Test model description"
    )


@pytest.fixture
def sample_claude_config(sample_model_config):
    """Provide a sample ClaudeConfig for testing."""
    from claude_switch.config import ClaudeConfig
    return ClaudeConfig(
        name="test-config",
        api_key="sk-test-key-123",
        base_url="https://api.test.com",
        timeout_ms=600000,
        disable_nonessential_traffic=True,
        description="Test configuration",
        models={"test-model": sample_model_config},
        default_model="test-model"
    )
