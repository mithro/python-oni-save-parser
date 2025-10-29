"""Game object behavior parsing."""

from typing import Any

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.game_objects.types import GameObjectBehavior
from oni_save_parser.save_structure.type_templates import TypeTemplate, parse_by_template, unparse_by_template
from oni_save_parser.save_structure.type_templates.template_parser import validate_dotnet_identifier_name


def parse_behavior(parser: BinaryParser, templates: list[TypeTemplate]) -> GameObjectBehavior:
    """Parse a single game object behavior (component).

    Args:
        parser: Binary parser positioned at behavior data
        templates: Type templates for deserialization

    Returns:
        Parsed behavior with template data and extra data

    Raises:
        CorruptionError: If behavior data is invalid
    """
    # Read behavior name (e.g., "MinionIdentity", "Health")
    name_raw = parser.read_klei_string()
    if name_raw is None:
        raise CorruptionError("Expected behavior name, got null", offset=parser.offset)
    name = validate_dotnet_identifier_name(name_raw)

    # Read data length (for validation)
    data_length = parser.read_int32()
    if data_length < 0:
        raise CorruptionError(f"Invalid behavior data length: {data_length}", offset=parser.offset)

    # Track start position for length validation
    start_offset = parser.offset

    # Parse template data (fields and properties defined by type template)
    template_data: dict[str, Any] | None = None
    try:
        template_data = parse_by_template(parser, templates, name)
    except CorruptionError:
        # If template not found, skip the entire data block
        parser.offset = start_offset + data_length
        return GameObjectBehavior(
            name=name, template_data=None, extra_data=None, extra_raw=parser.data[start_offset : parser.offset]
        )

    # TODO: Parse extra data for specific behavior types
    # - Storage: Has special extra data for stored items
    # - MinionModifiers: Has special minion modifier data
    # - Modifiers: Has special modifier data
    extra_data = None

    # Capture remaining data as raw bytes
    bytes_consumed = parser.offset - start_offset
    remaining = data_length - bytes_consumed

    if remaining < 0:
        raise CorruptionError(
            f"Behavior {name} consumed more data than expected: "
            f"consumed {bytes_consumed}, expected {data_length}",
            offset=parser.offset,
        )

    extra_raw = parser.read_bytes(remaining) if remaining > 0 else b""

    return GameObjectBehavior(name=name, template_data=template_data, extra_data=extra_data, extra_raw=extra_raw)


def unparse_behavior(
    writer: BinaryWriter, templates: list[TypeTemplate], behavior: GameObjectBehavior
) -> None:
    """Write a game object behavior to binary data.

    Args:
        writer: Binary writer to append to
        templates: Type templates for serialization
        behavior: Behavior to write
    """
    # Write behavior name
    writer.write_klei_string(behavior.name)

    # Build behavior data in temporary buffer to measure length
    data_writer = BinaryWriter()

    # Write template data
    if behavior.template_data is not None:
        unparse_by_template(data_writer, templates, behavior.name, behavior.template_data)

    # TODO: Write extra data for specific behavior types

    # Write extra raw data
    if behavior.extra_raw:
        data_writer.write_bytes(behavior.extra_raw)

    # Write data length and data
    writer.write_int32(len(data_writer.data))
    writer.write_bytes(data_writer.data)
