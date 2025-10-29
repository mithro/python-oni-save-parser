"""TypeTemplate binary parsing and unparsing."""

import re

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.type_templates.type_info_parser import (
    parse_type_info,
    unparse_type_info,
)
from oni_save_parser.save_structure.type_templates.types import (
    TypeTemplate,
    TypeTemplateMember,
)

# Regex to detect non-printable characters (0x00-0x1F)
REGEX_IDENTIFIER_INVAL_CHARS = re.compile(r"[\x00-\x1F]")


def validate_dotnet_identifier_name(name: str | None) -> str:
    """Validate a .NET identifier name.

    Args:
        name: Identifier name to validate

    Returns:
        Validated name

    Raises:
        CorruptionError: If name is invalid
    """
    if not name or len(name) == 0:
        raise CorruptionError(
            "A .NET identifier name must not be null or zero length",
        )

    if len(name) >= 512:
        # C# compiler limit: CS0645: Identifier too long
        # Anything >= 512 chars likely indicates parser error
        raise CorruptionError(
            "A .NET identifier name exceeded 511 characters. "
            "This most likely indicates a parser error",
        )

    # Check for non-printable characters
    if REGEX_IDENTIFIER_INVAL_CHARS.search(name):
        raise CorruptionError(
            "A .NET identifier name contains non-printable characters. "
            "This most likely indicates a parser error",
        )

    return name


def parse_template(parser: BinaryParser) -> TypeTemplate:
    """Parse a single TypeTemplate from binary data.

    Args:
        parser: Binary parser positioned at TypeTemplate data

    Returns:
        Parsed TypeTemplate structure

    Raises:
        CorruptionError: If data is invalid
    """
    name_raw = parser.read_klei_string()
    name = validate_dotnet_identifier_name(name_raw)

    field_count = parser.read_int32()
    prop_count = parser.read_int32()

    fields: list[TypeTemplateMember] = []
    for _ in range(field_count):
        field_name_raw = parser.read_klei_string()
        field_name = validate_dotnet_identifier_name(field_name_raw)
        field_type = parse_type_info(parser)
        fields.append(TypeTemplateMember(name=field_name, type=field_type))

    properties: list[TypeTemplateMember] = []
    for _ in range(prop_count):
        prop_name_raw = parser.read_klei_string()
        prop_name = validate_dotnet_identifier_name(prop_name_raw)
        prop_type = parse_type_info(parser)
        properties.append(TypeTemplateMember(name=prop_name, type=prop_type))

    return TypeTemplate(name=name, fields=fields, properties=properties)


def unparse_template(writer: BinaryWriter, template: TypeTemplate) -> None:
    """Write a single TypeTemplate to binary data.

    Args:
        writer: Binary writer to append to
        template: TypeTemplate structure to write
    """
    writer.write_klei_string(template.name)

    writer.write_int32(len(template.fields))
    writer.write_int32(len(template.properties))

    for field in template.fields:
        writer.write_klei_string(field.name)
        unparse_type_info(writer, field.type)

    for prop in template.properties:
        writer.write_klei_string(prop.name)
        unparse_type_info(writer, prop.type)


def parse_templates(parser: BinaryParser) -> list[TypeTemplate]:
    """Parse multiple TypeTemplates from binary data.

    Args:
        parser: Binary parser positioned at template list data

    Returns:
        List of parsed TypeTemplate structures

    Raises:
        CorruptionError: If data is invalid
    """
    template_count = parser.read_int32()
    templates: list[TypeTemplate] = []
    for _ in range(template_count):
        templates.append(parse_template(parser))
    return templates


def unparse_templates(writer: BinaryWriter, templates: list[TypeTemplate]) -> None:
    """Write multiple TypeTemplates to binary data.

    Args:
        writer: Binary writer to append to
        templates: List of TypeTemplate structures to write
    """
    writer.write_int32(len(templates))
    for template in templates:
        unparse_template(writer, template)
