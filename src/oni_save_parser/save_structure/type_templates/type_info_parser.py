"""TypeInfo binary parsing and unparsing."""

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.type_templates.types import (
    GENERIC_TYPES,
    SerializationTypeCode,
    SerializationTypeInfo,
    TypeInfo,
    get_type_code,
)


def parse_type_info(parser: BinaryParser) -> TypeInfo:
    """Parse TypeInfo from binary data.

    Args:
        parser: Binary parser positioned at TypeInfo data

    Returns:
        Parsed TypeInfo structure

    Raises:
        CorruptionError: If data is invalid
    """
    info = parser.read_byte()
    type_code = get_type_code(info)

    template_name: str | None = None
    sub_types: list[TypeInfo] | None = None

    # UserDefined and Enumeration types have a template name
    if type_code in (SerializationTypeCode.UserDefined, SerializationTypeCode.Enumeration):
        user_type_name = parser.read_klei_string()
        if user_type_name is None:
            raise CorruptionError(
                "Expected non-null type name for user-defined or enumeration type",
                offset=parser.offset,
            )
        template_name = user_type_name

    # Generic types have subtypes
    if info & SerializationTypeInfo.IS_GENERIC_TYPE:
        if type_code not in GENERIC_TYPES:
            raise CorruptionError(
                f"Unsupported non-generic type {type_code} marked as generic",
                offset=parser.offset,
            )
        sub_type_count = parser.read_byte()
        sub_types = []
        for _ in range(sub_type_count):
            sub_types.append(parse_type_info(parser))

    # Array types always have one subtype (element type)
    elif type_code == SerializationTypeCode.Array:
        sub_type = parse_type_info(parser)
        sub_types = [sub_type]

    return TypeInfo(info=info, template_name=template_name, sub_types=sub_types)


def unparse_type_info(writer: BinaryWriter, type_info: TypeInfo) -> None:
    """Write TypeInfo to binary data.

    Args:
        writer: Binary writer to append to
        type_info: TypeInfo structure to write
    """
    writer.write_byte(type_info.info)
    type_code = get_type_code(type_info.info)

    # Write template name for UserDefined and Enumeration types
    if type_code in (SerializationTypeCode.UserDefined, SerializationTypeCode.Enumeration):
        writer.write_klei_string(type_info.template_name)

    # Write subtypes for generic types
    if type_info.info & SerializationTypeInfo.IS_GENERIC_TYPE:
        assert type_info.sub_types is not None, "Generic types must have sub_types"
        writer.write_byte(len(type_info.sub_types))
        for sub_type in type_info.sub_types:
            unparse_type_info(writer, sub_type)

    # Write subtype for array types
    elif type_code == SerializationTypeCode.Array:
        assert type_info.sub_types is not None, "Array types must have sub_types"
        unparse_type_info(writer, type_info.sub_types[0])
