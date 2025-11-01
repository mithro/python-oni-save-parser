"""Top-level game objects parsing."""

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.game_objects.group_parser import (
    parse_game_object_group,
    unparse_game_object_group,
)
from oni_save_parser.save_structure.game_objects.types import GameObjectGroup
from oni_save_parser.save_structure.type_templates import TypeTemplate


def parse_game_objects(
    parser: BinaryParser, templates: list[TypeTemplate]
) -> list[GameObjectGroup]:
    """Parse all game object groups.

    Args:
        parser: Binary parser positioned at game objects data
        templates: Type templates for behavior deserialization

    Returns:
        List of game object groups

    Raises:
        CorruptionError: If game objects data is invalid
    """
    # Read group count
    group_count = parser.read_int32()
    if group_count < 0:
        msg = f"Invalid game object group count: {group_count}"
        raise CorruptionError(msg, offset=parser.offset)

    # Parse groups
    groups = []
    for _ in range(group_count):
        group = parse_game_object_group(parser, templates)
        groups.append(group)

    return groups


def unparse_game_objects(
    writer: BinaryWriter, templates: list[TypeTemplate], groups: list[GameObjectGroup]
) -> None:
    """Write game object groups to binary data.

    Args:
        writer: Binary writer to append to
        templates: Type templates for behavior serialization
        groups: List of game object groups to write
    """
    # Write group count
    writer.write_int32(len(groups))

    # Write groups
    for group in groups:
        unparse_game_object_group(writer, templates, group)
