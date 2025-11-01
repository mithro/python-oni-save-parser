"""Data models for rendering pipeline."""
from dataclasses import dataclass
from enum import Enum


class ElementState(Enum):
    """Physical state of an element."""
    SOLID = "solid"
    LIQUID = "liquid"
    GAS = "gas"


@dataclass
class Cell:
    """Single grid cell in the world."""
    element: str
    state: ElementState
    temperature: float
    mass: float


@dataclass
class AsteroidData:
    """Data for a single asteroid/world."""
    id: str
    name: str
    width: int
    height: int
    cells: list[list[Cell]]  # 2D grid: cells[y][x]


@dataclass
class SaveMetadata:
    """Metadata about the save file."""
    colony_name: str
    cycle_number: int
    seed: str


@dataclass
class WorldModel:
    """Complete world model for rendering."""
    asteroids: list[AsteroidData]
    metadata: SaveMetadata
