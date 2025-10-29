"""Type-based data parsing and unparsing for KSerialization.

This module handles parsing/unparsing actual data values based on their TypeInfo.
"""

from typing import Any

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.type_templates.types import (
    SerializationTypeCode,
    TypeInfo,
    TypeTemplate,
    get_type_code,
    is_value_type,
)


def parse_by_template(
    parser: BinaryParser, templates: list[TypeTemplate], template_name: str
) -> dict[str, Any]:
    """Parse object data using a type template.

    Args:
        parser: Binary parser positioned at object data
        templates: List of all type templates
        template_name: Name of template to use

    Returns:
        Dictionary with field/property values

    Raises:
        CorruptionError: If template not found
    """
    template = next((t for t in templates if t.name == template_name), None)
    if not template:
        raise CorruptionError(f'Template "{template_name}" not found')

    result: dict[str, Any] = {}

    # Parse fields
    for field in template.fields:
        value = parse_by_type(parser, templates, field.type)
        result[field.name] = value

    # Parse properties
    for prop in template.properties:
        value = parse_by_type(parser, templates, prop.type)
        result[prop.name] = value

    return result


def unparse_by_template(
    writer: BinaryWriter,
    templates: list[TypeTemplate],
    template_name: str,
    obj: dict[str, Any],
) -> None:
    """Write object data using a type template.

    Args:
        writer: Binary writer to append to
        templates: List of all type templates
        template_name: Name of template to use
        obj: Dictionary with field/property values

    Raises:
        CorruptionError: If template not found
    """
    template = next((t for t in templates if t.name == template_name), None)
    if not template:
        raise CorruptionError(f'Template "{template_name}" not found')

    # Write fields
    for field in template.fields:
        value = obj[field.name]
        unparse_by_type(writer, templates, value, field.type)

    # Write properties
    for prop in template.properties:
        value = obj[prop.name]
        unparse_by_type(writer, templates, value, prop.type)


def _parse_array_like(
    parser: BinaryParser, templates: list[TypeTemplate], type_info: TypeInfo
) -> list[Any] | bytes | None:
    """Parse array-like collection (Array, List, HashSet, Queue).

    Args:
        parser: Binary parser
        templates: Type templates
        type_info: Type information with element subtype

    Returns:
        List of elements, Uint8Array for byte arrays, or None for null
    """
    assert type_info.sub_types is not None, "Array-like types must have sub_types"
    element_type = type_info.sub_types[0]

    # Read data-length (ignored, but must be read)
    parser.read_int32()

    # Read element count
    length = parser.read_int32()

    if length == -1:
        return None
    elif length < 0:
        raise CorruptionError(f"Invalid array length {length}", offset=parser.offset - 4)

    # Special case: byte arrays return bytes
    if get_type_code(element_type.info) == SerializationTypeCode.Byte:
        return parser.read_bytes(length)

    # Value types skip data-length prefix on elements
    if is_value_type(element_type.info):
        if get_type_code(element_type.info) != SerializationTypeCode.UserDefined:
            raise CorruptionError(
                f"Type {get_type_code(element_type.info)} cannot be parsed as value-type"
            )
        assert element_type.template_name is not None
        elements = []
        for _ in range(length):
            element = parse_by_template(parser, templates, element_type.template_name)
            elements.append(element)
        return elements

    # Reference types include data-length on each element
    elements = []
    for _ in range(length):
        element = parse_by_type(parser, templates, element_type)
        elements.append(element)
    return elements


def _unparse_array_like(
    writer: BinaryWriter,
    templates: list[TypeTemplate],
    values: list[Any] | bytes | None,
    type_info: TypeInfo,
) -> None:
    """Write array-like collection.

    Args:
        writer: Binary writer
        templates: Type templates
        values: List of values or bytes or None
        type_info: Type information with element subtype
    """
    assert type_info.sub_types is not None, "Array-like types must have sub_types"
    element_type = type_info.sub_types[0]

    if values is None:
        # Null: data-length includes element count
        writer.write_int32(4)
        writer.write_int32(-1)
        return

    # Write elements to temporary buffer to measure length
    temp_writer = BinaryWriter()

    if get_type_code(element_type.info) == SerializationTypeCode.Byte:
        # Byte arrays
        if not isinstance(values, bytes):
            raise CorruptionError("Expected bytes for byte array")
        temp_writer.write_bytes(values)
    elif is_value_type(element_type.info):
        # Value types
        assert element_type.template_name is not None
        assert isinstance(values, list), "Value type arrays must be lists"
        for element in values:
            unparse_by_template(temp_writer, templates, element_type.template_name, element)
    else:
        # Reference types
        assert isinstance(values, list), "Reference type arrays must be lists"
        for element in values:
            unparse_by_type(temp_writer, templates, element, element_type)

    # Write data-length (element count is NOT included)
    writer.write_int32(len(temp_writer.data))
    # Write element count
    writer.write_int32(len(values))
    # Write elements
    writer.write_bytes(temp_writer.data)


def parse_by_type(
    parser: BinaryParser, templates: list[TypeTemplate], type_info: TypeInfo
) -> Any:
    """Parse value based on its type information.

    Args:
        parser: Binary parser positioned at value data
        templates: List of all type templates
        type_info: Type information describing the value

    Returns:
        Parsed value (type depends on TypeInfo)

    Raises:
        CorruptionError: If data is invalid or type unknown
    """
    type_code = get_type_code(type_info.info)

    # Simple primitives
    if type_code == SerializationTypeCode.Boolean:
        return parser.read_boolean()
    elif type_code == SerializationTypeCode.Byte:
        return parser.read_byte()
    elif type_code == SerializationTypeCode.SByte:
        return parser.read_sbyte()
    elif type_code == SerializationTypeCode.Int16:
        return parser.read_int16()
    elif type_code == SerializationTypeCode.UInt16:
        return parser.read_uint16()
    elif type_code == SerializationTypeCode.Int32:
        return parser.read_int32()
    elif type_code == SerializationTypeCode.UInt32:
        return parser.read_uint32()
    elif type_code == SerializationTypeCode.Int64:
        return parser.read_int64()
    elif type_code == SerializationTypeCode.UInt64:
        return parser.read_uint64()
    elif type_code == SerializationTypeCode.Single:
        return parser.read_single()
    elif type_code == SerializationTypeCode.Double:
        return parser.read_double()
    elif type_code == SerializationTypeCode.String:
        return parser.read_klei_string()
    elif type_code == SerializationTypeCode.Enumeration:
        return parser.read_int32()  # Enums are stored as int32

    # Vector types
    elif type_code == SerializationTypeCode.Vector2:
        x = parser.read_single()
        y = parser.read_single()
        return {"x": x, "y": y}
    elif type_code == SerializationTypeCode.Vector2I:
        x = parser.read_int32()
        y = parser.read_int32()
        return {"x": x, "y": y}
    elif type_code == SerializationTypeCode.Vector3:
        x = parser.read_single()
        y = parser.read_single()
        z = parser.read_single()
        return {"x": x, "y": y, "z": z}

    # Colour type
    elif type_code == SerializationTypeCode.Colour:
        r = parser.read_byte() / 255.0
        g = parser.read_byte() / 255.0
        b = parser.read_byte() / 255.0
        a = parser.read_byte() / 255.0
        return {"r": r, "g": g, "b": b, "a": a}

    # Array-like collections
    elif type_code in (
        SerializationTypeCode.Array,
        SerializationTypeCode.List,
        SerializationTypeCode.HashSet,
        SerializationTypeCode.Queue,
    ):
        return _parse_array_like(parser, templates, type_info)

    # Dictionary
    elif type_code == SerializationTypeCode.Dictionary:
        assert type_info.sub_types is not None and len(type_info.sub_types) == 2
        key_type, value_type = type_info.sub_types

        # Read data-length (ignored)
        parser.read_int32()

        # Read element count
        count = parser.read_int32()
        if count == -1:
            return None
        elif count < 0:
            raise CorruptionError(f"Invalid dictionary count {count}", offset=parser.offset - 4)

        # Values parsed first, then keys
        pairs: list[tuple[Any, Any]] = []
        values_list = []
        for _ in range(count):
            value = parse_by_type(parser, templates, value_type)
            values_list.append(value)

        for i in range(count):
            key = parse_by_type(parser, templates, key_type)
            pairs.append((key, values_list[i]))

        return pairs

    # Pair
    elif type_code == SerializationTypeCode.Pair:
        assert type_info.sub_types is not None and len(type_info.sub_types) == 2
        key_type, value_type = type_info.sub_types

        # Read data-length
        data_length = parser.read_int32()
        if data_length < 0:
            return None

        key = parse_by_type(parser, templates, key_type)
        value = parse_by_type(parser, templates, value_type)
        return {"key": key, "value": value}

    # UserDefined (template-based object)
    elif type_code == SerializationTypeCode.UserDefined:
        assert type_info.template_name is not None

        # Read data-length
        data_length = parser.read_int32()
        if data_length < 0:
            return None

        parse_start = parser.offset
        obj = parse_by_template(parser, templates, type_info.template_name)
        parse_end = parser.offset

        parse_length = parse_end - parse_start
        if parse_length != data_length:
            raise CorruptionError(
                f'Template "{type_info.template_name}" parsed {abs(parse_length - data_length)} '
                f'bytes {"more" if parse_length > data_length else "less"} than expected',
                offset=parse_start,
            )

        return obj

    else:
        raise CorruptionError(f"Unknown type code {type_code} (typeinfo: {type_info.info})")


def unparse_by_type(
    writer: BinaryWriter, templates: list[TypeTemplate], value: Any, type_info: TypeInfo
) -> None:
    """Write value based on its type information.

    Args:
        writer: Binary writer to append to
        templates: List of all type templates
        value: Value to write
        type_info: Type information describing the value

    Raises:
        CorruptionError: If type is unknown
    """
    type_code = get_type_code(type_info.info)

    # Simple primitives
    if type_code == SerializationTypeCode.Boolean:
        writer.write_boolean(value)
    elif type_code == SerializationTypeCode.Byte:
        writer.write_byte(value)
    elif type_code == SerializationTypeCode.SByte:
        writer.write_sbyte(value)
    elif type_code == SerializationTypeCode.Int16:
        writer.write_int16(value)
    elif type_code == SerializationTypeCode.UInt16:
        writer.write_uint16(value)
    elif type_code == SerializationTypeCode.Int32:
        writer.write_int32(value)
    elif type_code == SerializationTypeCode.UInt32:
        writer.write_uint32(value)
    elif type_code == SerializationTypeCode.Int64:
        writer.write_int64(value)
    elif type_code == SerializationTypeCode.UInt64:
        writer.write_uint64(value)
    elif type_code == SerializationTypeCode.Single:
        writer.write_single(value)
    elif type_code == SerializationTypeCode.Double:
        writer.write_double(value)
    elif type_code == SerializationTypeCode.String:
        writer.write_klei_string(value)
    elif type_code == SerializationTypeCode.Enumeration:
        writer.write_int32(value)

    # Vector types
    elif type_code == SerializationTypeCode.Vector2:
        writer.write_single(value["x"])
        writer.write_single(value["y"])
    elif type_code == SerializationTypeCode.Vector2I:
        writer.write_int32(value["x"])
        writer.write_int32(value["y"])
    elif type_code == SerializationTypeCode.Vector3:
        writer.write_single(value["x"])
        writer.write_single(value["y"])
        writer.write_single(value["z"])

    # Colour type
    elif type_code == SerializationTypeCode.Colour:

        def frac_to_byte(num: float) -> int:
            byte_val = round(num * 255)
            return max(0, min(255, byte_val))

        writer.write_byte(frac_to_byte(value["r"]))
        writer.write_byte(frac_to_byte(value["g"]))
        writer.write_byte(frac_to_byte(value["b"]))
        writer.write_byte(frac_to_byte(value["a"]))

    # Array-like collections
    elif type_code in (
        SerializationTypeCode.Array,
        SerializationTypeCode.List,
        SerializationTypeCode.HashSet,
        SerializationTypeCode.Queue,
    ):
        _unparse_array_like(writer, templates, value, type_info)

    # Dictionary
    elif type_code == SerializationTypeCode.Dictionary:
        assert type_info.sub_types is not None and len(type_info.sub_types) == 2
        key_type, value_type = type_info.sub_types

        if value is None:
            writer.write_int32(4)
            writer.write_int32(-1)
            return

        # Write to temp buffer to measure
        temp_writer = BinaryWriter()

        # Values first
        for key, val in value:
            unparse_by_type(temp_writer, templates, val, value_type)
        # Then keys
        for key, val in value:
            unparse_by_type(temp_writer, templates, key, key_type)

        # Write data-length (element count NOT included)
        writer.write_int32(len(temp_writer.data))
        # Write element count
        writer.write_int32(len(value))
        # Write data
        writer.write_bytes(temp_writer.data)

    # Pair
    elif type_code == SerializationTypeCode.Pair:
        assert type_info.sub_types is not None and len(type_info.sub_types) == 2
        key_type, value_type = type_info.sub_types

        if value is None:
            writer.write_int32(4)
            writer.write_int32(-1)
            return

        # Write to temp buffer to measure
        temp_writer = BinaryWriter()
        unparse_by_type(temp_writer, templates, value["key"], key_type)
        unparse_by_type(temp_writer, templates, value["value"], value_type)

        # Write data-length then data
        writer.write_int32(len(temp_writer.data))
        writer.write_bytes(temp_writer.data)

    # UserDefined
    elif type_code == SerializationTypeCode.UserDefined:
        assert type_info.template_name is not None

        if value is None:
            writer.write_int32(-1)
            return

        # Write to temp buffer to measure
        temp_writer = BinaryWriter()
        unparse_by_template(temp_writer, templates, type_info.template_name, value)

        # Write data-length then data
        writer.write_int32(len(temp_writer.data))
        writer.write_bytes(temp_writer.data)

    else:
        raise CorruptionError(f"Unknown type code {type_code} (typeinfo: {type_info.info})")
