"""Tests for TypeInfo parsing."""

from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.type_templates.type_info_parser import (
    parse_type_info,
    unparse_type_info,
)
from oni_save_parser.save_structure.type_templates.types import (
    TypeInfo,
)


def test_parse_simple_type() -> None:
    """Should parse simple type (Int32)."""
    # Int32 type code = 6
    data = bytes([6])
    parser = BinaryParser(data)
    type_info = parse_type_info(parser)

    assert type_info.info == 6
    assert type_info.template_name is None
    assert type_info.sub_types is None


def test_parse_user_defined_type() -> None:
    """Should parse UserDefined type with template name."""
    # UserDefined = 0, then length-prefixed string "TestClass"
    writer = BinaryWriter()
    writer.write_byte(0)
    writer.write_klei_string("TestClass")

    parser = BinaryParser(writer.data)
    type_info = parse_type_info(parser)

    assert type_info.info == 0
    assert type_info.template_name == "TestClass"
    assert type_info.sub_types is None


def test_parse_enumeration_type() -> None:
    """Should parse Enumeration type with template name."""
    # Enumeration = 13
    writer = BinaryWriter()
    writer.write_byte(13)
    writer.write_klei_string("MyEnum")

    parser = BinaryParser(writer.data)
    type_info = parse_type_info(parser)

    assert type_info.info == 13
    assert type_info.template_name == "MyEnum"
    assert type_info.sub_types is None


def test_parse_array_type() -> None:
    """Should parse Array type with element subtype."""
    # Array = 17, element type = Int32 (6)
    data = bytes([17, 6])
    parser = BinaryParser(data)
    type_info = parse_type_info(parser)

    assert type_info.info == 17
    assert type_info.template_name is None
    assert type_info.sub_types is not None
    assert len(type_info.sub_types) == 1
    assert type_info.sub_types[0].info == 6


def test_parse_generic_list_type() -> None:
    """Should parse generic List<String> type."""
    # List = 20, IS_GENERIC_TYPE = 0x80
    # info byte = 20 | 0x80 = 148
    # subtype count = 1
    # subtype: String = 12
    data = bytes([148, 1, 12])
    parser = BinaryParser(data)
    type_info = parse_type_info(parser)

    assert type_info.info == 148
    assert type_info.template_name is None
    assert type_info.sub_types is not None
    assert len(type_info.sub_types) == 1
    assert type_info.sub_types[0].info == 12


def test_parse_generic_dictionary_type() -> None:
    """Should parse generic Dictionary<String, Int32>."""
    # Dictionary = 19, IS_GENERIC_TYPE = 0x80
    # info byte = 19 | 0x80 = 147
    # subtype count = 2
    # subtype 1: String = 12
    # subtype 2: Int32 = 6
    data = bytes([147, 2, 12, 6])
    parser = BinaryParser(data)
    type_info = parse_type_info(parser)

    assert type_info.info == 147
    assert type_info.sub_types is not None
    assert len(type_info.sub_types) == 2
    assert type_info.sub_types[0].info == 12
    assert type_info.sub_types[1].info == 6


def test_unparse_simple_type() -> None:
    """Should write simple type."""
    type_info = TypeInfo(info=6, template_name=None, sub_types=None)

    writer = BinaryWriter()
    unparse_type_info(writer, type_info)

    assert writer.data == bytes([6])


def test_unparse_user_defined_type() -> None:
    """Should write UserDefined type with template name."""
    type_info = TypeInfo(info=0, template_name="TestClass", sub_types=None)

    writer = BinaryWriter()
    unparse_type_info(writer, type_info)

    # Parse it back to verify
    parser = BinaryParser(writer.data)
    assert parser.read_byte() == 0
    assert parser.read_klei_string() == "TestClass"


def test_unparse_array_type() -> None:
    """Should write Array type with element subtype."""
    element_type = TypeInfo(info=6, template_name=None, sub_types=None)
    type_info = TypeInfo(info=17, template_name=None, sub_types=[element_type])

    writer = BinaryWriter()
    unparse_type_info(writer, type_info)

    assert writer.data == bytes([17, 6])


def test_unparse_generic_list_type() -> None:
    """Should write generic List<String> type."""
    string_type = TypeInfo(info=12, template_name=None, sub_types=None)
    type_info = TypeInfo(info=148, template_name=None, sub_types=[string_type])

    writer = BinaryWriter()
    unparse_type_info(writer, type_info)

    assert writer.data == bytes([148, 1, 12])


def test_round_trip_complex_type() -> None:
    """Should round-trip complex nested type."""
    # List<Dictionary<String, Int32>>
    string_type = TypeInfo(info=12)
    int_type = TypeInfo(info=6)
    dict_type = TypeInfo(info=147, sub_types=[string_type, int_type])  # 19 | 0x80
    list_type = TypeInfo(info=148, sub_types=[dict_type])  # 20 | 0x80

    # Write
    writer = BinaryWriter()
    unparse_type_info(writer, list_type)

    # Read back
    parser = BinaryParser(writer.data)
    parsed = parse_type_info(parser)

    assert parsed.info == 148
    assert parsed.sub_types is not None
    assert len(parsed.sub_types) == 1
    assert parsed.sub_types[0].info == 147
    assert parsed.sub_types[0].sub_types is not None
    assert len(parsed.sub_types[0].sub_types) == 2
    assert parsed.sub_types[0].sub_types[0].info == 12
    assert parsed.sub_types[0].sub_types[1].info == 6
