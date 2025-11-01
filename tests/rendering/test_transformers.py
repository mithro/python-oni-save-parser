"""Tests for DataTransformer."""
import tempfile
from pathlib import Path

from oni_save_parser import load_save_file
from oni_save_parser.rendering.transformers import DataTransformer
from oni_save_parser.rendering.models import ElementState
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


def test_determine_state_gas_elements() -> None:
    """Test that gas elements are correctly identified."""
    registry = ElementRegistry()
    transformer = DataTransformer(registry)

    # Gas elements should be classified as GAS
    assert transformer._determine_state("Oxygen", 1.0) == ElementState.GAS
    assert transformer._determine_state("CarbonDioxide", 1.0) == ElementState.GAS
    assert transformer._determine_state("Hydrogen", 1.0) == ElementState.GAS
    assert transformer._determine_state("ChlorineGas", 1.0) == ElementState.GAS
    assert transformer._determine_state("Steam", 1.0) == ElementState.GAS
    assert transformer._determine_state("Vacuum", 0.0) == ElementState.GAS


def test_determine_state_liquid_elements() -> None:
    """Test that liquid elements are correctly identified."""
    registry = ElementRegistry()
    transformer = DataTransformer(registry)

    # Liquid elements should be classified as LIQUID
    assert transformer._determine_state("Water", 1000.0) == ElementState.LIQUID
    assert transformer._determine_state("DirtyWater", 1000.0) == ElementState.LIQUID
    assert transformer._determine_state("SaltWater", 1000.0) == ElementState.LIQUID
    assert transformer._determine_state("Brine", 1000.0) == ElementState.LIQUID
    assert transformer._determine_state("CrudeOil", 1000.0) == ElementState.LIQUID
    assert transformer._determine_state("Petroleum", 1000.0) == ElementState.LIQUID


def test_determine_state_solid_elements() -> None:
    """Test that solid elements are correctly identified."""
    registry = ElementRegistry()
    transformer = DataTransformer(registry)

    # Solid elements should be classified as SOLID
    assert transformer._determine_state("Granite", 1000.0) == ElementState.SOLID
    assert transformer._determine_state("Sand", 1000.0) == ElementState.SOLID
    assert transformer._determine_state("Dirt", 1000.0) == ElementState.SOLID
    assert transformer._determine_state("Ice", 1000.0) == ElementState.SOLID


def test_determine_state_zero_mass() -> None:
    """Test that zero mass always returns gas/vacuum."""
    registry = ElementRegistry()
    transformer = DataTransformer(registry)

    # Zero mass should always be GAS (vacuum)
    assert transformer._determine_state("Granite", 0.0) == ElementState.GAS
    assert transformer._determine_state("Water", 0.0) == ElementState.GAS
    assert transformer._determine_state("Oxygen", 0.0) == ElementState.GAS
