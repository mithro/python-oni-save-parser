"""Game objects data structures."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Vector3:
    """3D vector (position or scale)."""

    x: float
    y: float
    z: float


@dataclass
class Quaternion:
    """Quaternion rotation (4 floats)."""

    x: float
    y: float
    z: float
    w: float


@dataclass
class GameObjectBehavior:
    """Component attached to a game object.

    Behaviors are the game's component system, each tied to a .NET class.
    Examples: MinionIdentity, Health, Storage, PrimaryElement, etc.
    """

    name: str  # .NET class name (e.g., "MinionIdentity", "Health")
    template_data: dict[str, Any] | None  # Parsed template data
    extra_data: Any | None  # Extra data for specific behaviors (Storage, Modifiers)
    extra_raw: bytes  # Unparsed extra data (preserved as-is)


@dataclass
class GameObject:
    """Game entity in the ONI world.

    Represents a Unity GameObject with transform and behaviors (components).
    """

    position: Vector3  # 3D position in world
    rotation: Quaternion  # Rotation
    scale: Vector3  # Scale factors
    folder: int  # 0-255, used to look up Unity prefab
    behaviors: list[GameObjectBehavior]  # Attached components


@dataclass
class GameObjectGroup:
    """Group of game objects with the same prefab.

    Game objects are organized by prefab type (e.g., all "Minion", all "Tile").
    This structure enables efficient storage and lookup.
    """

    prefab_name: str  # Unity prefab name (e.g., "Minion", "Tile", "Door")
    objects: list[GameObject]  # Instances of this prefab type
