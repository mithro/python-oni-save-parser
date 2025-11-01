"""Tests for DataTransformer."""
import tempfile
from pathlib import Path

from oni_save_parser import load_save_file
from oni_save_parser.rendering.transformers import DataTransformer
from oni_save_parser.assets.element_registry import ElementRegistry


def test_data_transformer_initialization() -> None:
    """Test creating a DataTransformer."""
    registry = ElementRegistry()
    transformer = DataTransformer(registry)
    assert transformer is not None


def test_transform_with_real_save(tmp_path: Path) -> None:
    """Test transforming a real save file to WorldModel."""
    # Use existing test save
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        # Skip if test save not available
        import pytest
        pytest.skip("Test save file not available")

    # Load and transform
    registry = ElementRegistry()
    transformer = DataTransformer(registry)
    save_data = load_save_file(save_path)

    world_model = transformer.transform(save_data)

    # Verify basic structure
    assert world_model is not None
    assert world_model.metadata is not None
    assert len(world_model.asteroids) > 0

    # Verify first asteroid has data
    asteroid = world_model.asteroids[0]
    assert asteroid.width > 0
    assert asteroid.height > 0
    assert len(asteroid.cells) == asteroid.height
    assert len(asteroid.cells[0]) == asteroid.width
