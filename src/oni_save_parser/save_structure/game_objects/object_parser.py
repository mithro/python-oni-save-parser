"""Game object parsing."""

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.game_objects.behavior_parser import (
    parse_behavior,
    unparse_behavior,
)
from oni_save_parser.save_structure.game_objects.types import GameObject, Quaternion, Vector3
from oni_save_parser.save_structure.type_templates import TypeTemplate


def parse_vector3(parser: BinaryParser) -> Vector3:
    """Parse a Vector3 (3 floats)."""
    x = parser.read_single()
    y = parser.read_single()
    z = parser.read_single()
    return Vector3(x=x, y=y, z=z)


def parse_quaternion(parser: BinaryParser) -> Quaternion:
    """Parse a Quaternion (4 floats)."""
    x = parser.read_single()
    y = parser.read_single()
    z = parser.read_single()
    w = parser.read_single()
    return Quaternion(x=x, y=y, z=z, w=w)


def parse_game_object(parser: BinaryParser, templates: list[TypeTemplate]) -> GameObject:
    """Parse a single game object.

    Args:
        parser: Binary parser positioned at game object data
        templates: Type templates for behavior deserialization

    Returns:
        Parsed game object with transform and behaviors

    Raises:
        CorruptionError: If game object data is invalid
    """
    # Parse transform
    position = parse_vector3(parser)
    rotation = parse_quaternion(parser)
    scale = parse_vector3(parser)

    # Parse folder (0-255, used to look up Unity prefab)
    folder = parser.read_byte()

    # Parse behaviors
    behavior_count = parser.read_int32()
    if behavior_count < 0:
        raise CorruptionError(f"Invalid behavior count: {behavior_count}", offset=parser.offset)

    behaviors = []
    for _ in range(behavior_count):
        behavior = parse_behavior(parser, templates)
        behaviors.append(behavior)

    return GameObject(
        position=position, rotation=rotation, scale=scale, folder=folder, behaviors=behaviors
    )


def unparse_vector3(writer: BinaryWriter, vector: Vector3) -> None:
    """Write a Vector3 (3 floats)."""
    writer.write_single(vector.x)
    writer.write_single(vector.y)
    writer.write_single(vector.z)


def unparse_quaternion(writer: BinaryWriter, quaternion: Quaternion) -> None:
    """Write a Quaternion (4 floats)."""
    writer.write_single(quaternion.x)
    writer.write_single(quaternion.y)
    writer.write_single(quaternion.z)
    writer.write_single(quaternion.w)


def unparse_game_object(
    writer: BinaryWriter, templates: list[TypeTemplate], obj: GameObject
) -> None:
    """Write a game object to binary data.

    Args:
        writer: Binary writer to append to
        templates: Type templates for behavior serialization
        obj: Game object to write
    """
    # Write transform
    unparse_vector3(writer, obj.position)
    unparse_quaternion(writer, obj.rotation)
    unparse_vector3(writer, obj.scale)

    # Write folder
    writer.write_byte(obj.folder)

    # Write behaviors
    writer.write_int32(len(obj.behaviors))
    for behavior in obj.behaviors:
        unparse_behavior(writer, templates, behavior)
