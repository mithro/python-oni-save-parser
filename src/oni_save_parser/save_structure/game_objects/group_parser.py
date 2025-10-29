"""Game object group parsing."""

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.game_objects.object_parser import parse_game_object, unparse_game_object
from oni_save_parser.save_structure.game_objects.types import GameObjectGroup
from oni_save_parser.save_structure.type_templates import TypeTemplate
from oni_save_parser.save_structure.type_templates.template_parser import validate_dotnet_identifier_name


def parse_game_object_group(parser: BinaryParser, templates: list[TypeTemplate]) -> GameObjectGroup:
    """Parse a game object group.

    Groups contain multiple instances of the same prefab type.

    Args:
        parser: Binary parser positioned at group data
        templates: Type templates for behavior deserialization

    Returns:
        Parsed game object group

    Raises:
        CorruptionError: If group data is invalid
    """
    # Read prefab name (e.g., "Minion", "Tile", "Door")
    prefab_name_raw = parser.read_klei_string()
    if prefab_name_raw is None:
        raise CorruptionError("Expected prefab name, got null", offset=parser.offset)
    prefab_name = validate_dotnet_identifier_name(prefab_name_raw)

    # Read instance count
    instance_count = parser.read_int32()
    if instance_count < 0:
        raise CorruptionError(
            f"Invalid instance count for prefab {prefab_name}: {instance_count}", offset=parser.offset
        )

    # Read data length (for validation)
    data_length = parser.read_int32()
    if data_length < 0:
        raise CorruptionError(
            f"Invalid data length for prefab {prefab_name}: {data_length}", offset=parser.offset
        )

    # Track start position for length validation
    start_offset = parser.offset

    # Parse game objects
    objects = []
    for _ in range(instance_count):
        obj = parse_game_object(parser, templates)
        objects.append(obj)

    # Validate data length
    bytes_consumed = parser.offset - start_offset
    if bytes_consumed != data_length:
        raise CorruptionError(
            f"Game object group {prefab_name} data length mismatch: "
            f"expected {data_length}, consumed {bytes_consumed}",
            offset=parser.offset,
        )

    return GameObjectGroup(prefab_name=prefab_name, objects=objects)


def unparse_game_object_group(
    writer: BinaryWriter, templates: list[TypeTemplate], group: GameObjectGroup
) -> None:
    """Write a game object group to binary data.

    Args:
        writer: Binary writer to append to
        templates: Type templates for behavior serialization
        group: Game object group to write
    """
    # Write prefab name
    writer.write_klei_string(group.prefab_name)

    # Write instance count
    writer.write_int32(len(group.objects))

    # Build group data in temporary buffer to measure length
    data_writer = BinaryWriter()
    for obj in group.objects:
        unparse_game_object(data_writer, templates, obj)

    # Write data length and data
    writer.write_int32(len(data_writer.data))
    writer.write_bytes(data_writer.data)
