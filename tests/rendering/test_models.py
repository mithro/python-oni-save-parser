"""Tests for rendering data models."""
from oni_save_parser.rendering.models import (
    Cell,
    ElementState,
    AsteroidData,
    SaveMetadata,
    WorldModel,
)


def test_cell_creation() -> None:
    """Test creating a Cell."""
    cell = Cell(
        element="Oxygen",
        state=ElementState.GAS,
        temperature=300.0,
        mass=1.0,
    )
    assert cell.element == "Oxygen"
    assert cell.state == ElementState.GAS
    assert cell.temperature == 300.0
    assert cell.mass == 1.0


def test_element_state_enum() -> None:
    """Test ElementState enum values."""
    assert ElementState.SOLID.value == "solid"
    assert ElementState.LIQUID.value == "liquid"
    assert ElementState.GAS.value == "gas"


def test_asteroid_data_creation() -> None:
    """Test creating AsteroidData."""
    cells = [[Cell("Vacuum", ElementState.GAS, 0.0, 0.0) for _ in range(10)] for _ in range(10)]
    asteroid = AsteroidData(
        id="1",
        name="Terra",
        width=10,
        height=10,
        cells=cells,
    )
    assert asteroid.id == "1"
    assert asteroid.name == "Terra"
    assert asteroid.width == 10
    assert asteroid.height == 10
    assert len(asteroid.cells) == 10
    assert len(asteroid.cells[0]) == 10


def test_save_metadata_creation() -> None:
    """Test creating SaveMetadata."""
    metadata = SaveMetadata(
        colony_name="TestColony",
        cycle_number=100,
        seed="12345",
    )
    assert metadata.colony_name == "TestColony"
    assert metadata.cycle_number == 100
    assert metadata.seed == "12345"


def test_world_model_creation() -> None:
    """Test creating WorldModel."""
    metadata = SaveMetadata("Colony", 50, "seed")
    cells = [[Cell("Dirt", ElementState.SOLID, 298.0, 1000.0)]]
    asteroid = AsteroidData("1", "Terra", 1, 1, cells)

    model = WorldModel(
        asteroids=[asteroid],
        metadata=metadata,
    )
    assert len(model.asteroids) == 1
    assert model.metadata.colony_name == "Colony"
