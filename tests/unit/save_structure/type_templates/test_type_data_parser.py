"""Tests for type data parsing."""

import pytest
from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.type_templates.type_data_parser import (
    parse_by_template,
    parse_by_type,
    unparse_by_template,
    unparse_by_type,
)
from oni_save_parser.save_structure.type_templates.types import (
    SerializationTypeCode,
    TypeInfo,
    TypeTemplate,
    TypeTemplateMember,
)


def test_parse_boolean_true():
    """Should parse boolean true."""
    writer = BinaryWriter()
    writer.write_byte(1)

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.Boolean)
    value = parse_by_type(parser, [], type_info)

    assert value is True


def test_parse_boolean_false():
    """Should parse boolean false."""
    writer = BinaryWriter()
    writer.write_byte(0)

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.Boolean)
    value = parse_by_type(parser, [], type_info)

    assert value is False


def test_parse_int32():
    """Should parse Int32."""
    writer = BinaryWriter()
    writer.write_int32(12345)

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.Int32)
    value = parse_by_type(parser, [], type_info)

    assert value == 12345


def test_parse_string():
    """Should parse String."""
    writer = BinaryWriter()
    writer.write_klei_string("Hello World")

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.String)
    value = parse_by_type(parser, [], type_info)

    assert value == "Hello World"


def test_parse_string_null():
    """Should parse null String."""
    writer = BinaryWriter()
    writer.write_klei_string(None)

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.String)
    value = parse_by_type(parser, [], type_info)

    assert value is None


def test_parse_vector2():
    """Should parse Vector2."""
    writer = BinaryWriter()
    writer.write_single(1.5)
    writer.write_single(2.5)

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.Vector2)
    value = parse_by_type(parser, [], type_info)

    assert value == {"x": pytest.approx(1.5), "y": pytest.approx(2.5)}


def test_parse_vector2i():
    """Should parse Vector2I."""
    writer = BinaryWriter()
    writer.write_int32(10)
    writer.write_int32(20)

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.Vector2I)
    value = parse_by_type(parser, [], type_info)

    assert value == {"x": 10, "y": 20}


def test_parse_vector3():
    """Should parse Vector3."""
    writer = BinaryWriter()
    writer.write_single(1.5)
    writer.write_single(2.5)
    writer.write_single(3.5)

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.Vector3)
    value = parse_by_type(parser, [], type_info)

    assert value == {"x": pytest.approx(1.5), "y": pytest.approx(2.5), "z": pytest.approx(3.5)}


def test_parse_colour():
    """Should parse Colour."""
    writer = BinaryWriter()
    writer.write_byte(255)  # r
    writer.write_byte(128)  # g
    writer.write_byte(0)  # b
    writer.write_byte(255)  # a

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.Colour)
    value = parse_by_type(parser, [], type_info)

    assert value["r"] == pytest.approx(1.0, abs=0.01)
    assert value["g"] == pytest.approx(0.5, abs=0.01)
    assert value["b"] == pytest.approx(0.0, abs=0.01)
    assert value["a"] == pytest.approx(1.0, abs=0.01)


def test_parse_array_int32():
    """Should parse Array<Int32>."""
    writer = BinaryWriter()
    writer.write_int32(12)  # data-length (3 ints * 4 bytes)
    writer.write_int32(3)  # element count
    writer.write_int32(10)
    writer.write_int32(20)
    writer.write_int32(30)

    parser = BinaryParser(writer.data)
    element_type = TypeInfo(info=SerializationTypeCode.Int32)
    type_info = TypeInfo(info=SerializationTypeCode.Array, sub_types=[element_type])
    value = parse_by_type(parser, [], type_info)

    assert value == [10, 20, 30]


def test_parse_array_null():
    """Should parse null Array."""
    writer = BinaryWriter()
    writer.write_int32(4)  # data-length
    writer.write_int32(-1)  # null marker

    parser = BinaryParser(writer.data)
    element_type = TypeInfo(info=SerializationTypeCode.Int32)
    type_info = TypeInfo(info=SerializationTypeCode.Array, sub_types=[element_type])
    value = parse_by_type(parser, [], type_info)

    assert value is None


def test_parse_list_string():
    """Should parse List<String>."""
    writer = BinaryWriter()
    # Data length calculation:
    # "Hello": 4 (len) + 5 (bytes) = 9
    # "World": 4 (len) + 5 (bytes) = 9
    # Total: 18
    writer.write_int32(18)  # data-length
    writer.write_int32(2)  # element count
    writer.write_klei_string("Hello")
    writer.write_klei_string("World")

    parser = BinaryParser(writer.data)
    element_type = TypeInfo(info=SerializationTypeCode.String)
    type_info = TypeInfo(info=SerializationTypeCode.List, sub_types=[element_type])
    value = parse_by_type(parser, [], type_info)

    assert value == ["Hello", "World"]


def test_parse_dictionary_string_int32():
    """Should parse Dictionary<String, Int32>."""
    writer = BinaryWriter()
    # Values first, then keys
    # Data: two int32s (8 bytes) + two strings (4+1 + 4+1 = 10 bytes) = 18
    writer.write_int32(18)  # data-length
    writer.write_int32(2)  # element count
    # Values
    writer.write_int32(100)
    writer.write_int32(200)
    # Keys
    writer.write_klei_string("a")
    writer.write_klei_string("b")

    parser = BinaryParser(writer.data)
    key_type = TypeInfo(info=SerializationTypeCode.String)
    value_type = TypeInfo(info=SerializationTypeCode.Int32)
    type_info = TypeInfo(info=SerializationTypeCode.Dictionary, sub_types=[key_type, value_type])
    value = parse_by_type(parser, [], type_info)

    assert value == [("a", 100), ("b", 200)]


def test_parse_pair():
    """Should parse Pair<String, Int32>."""
    writer = BinaryWriter()
    # Data: string (4+5) + int32 (4) = 13
    writer.write_int32(13)  # data-length
    writer.write_klei_string("Hello")
    writer.write_int32(42)

    parser = BinaryParser(writer.data)
    key_type = TypeInfo(info=SerializationTypeCode.String)
    value_type = TypeInfo(info=SerializationTypeCode.Int32)
    type_info = TypeInfo(info=SerializationTypeCode.Pair, sub_types=[key_type, value_type])
    value = parse_by_type(parser, [], type_info)

    assert value == {"key": "Hello", "value": 42}


def test_parse_user_defined():
    """Should parse UserDefined type."""
    # Create a simple template
    field1 = TypeTemplateMember(name="field1", type=TypeInfo(info=SerializationTypeCode.Int32))
    field2 = TypeTemplateMember(name="field2", type=TypeInfo(info=SerializationTypeCode.String))
    template = TypeTemplate(name="TestClass", fields=[field1, field2], properties=[])
    templates = [template]

    # Write object data
    writer = BinaryWriter()
    writer.write_int32(8)  # data-length (4 + 4)
    writer.write_int32(123)
    writer.write_klei_string("")

    parser = BinaryParser(writer.data)
    type_info = TypeInfo(info=SerializationTypeCode.UserDefined, template_name="TestClass")
    value = parse_by_type(parser, templates, type_info)

    assert value == {"field1": 123, "field2": ""}


def test_parse_by_template():
    """Should parse object using template."""
    field1 = TypeTemplateMember(name="x", type=TypeInfo(info=SerializationTypeCode.Int32))
    field2 = TypeTemplateMember(name="y", type=TypeInfo(info=SerializationTypeCode.String))
    template = TypeTemplate(name="Point", fields=[field1, field2], properties=[])
    templates = [template]

    writer = BinaryWriter()
    writer.write_int32(10)
    writer.write_klei_string("test")

    parser = BinaryParser(writer.data)
    obj = parse_by_template(parser, templates, "Point")

    assert obj == {"x": 10, "y": "test"}


def test_unparse_int32():
    """Should write Int32."""
    writer = BinaryWriter()
    type_info = TypeInfo(info=SerializationTypeCode.Int32)
    unparse_by_type(writer, [], 12345, type_info)

    parser = BinaryParser(writer.data)
    assert parser.read_int32() == 12345


def test_unparse_vector2():
    """Should write Vector2."""
    writer = BinaryWriter()
    type_info = TypeInfo(info=SerializationTypeCode.Vector2)
    unparse_by_type(writer, [], {"x": 1.5, "y": 2.5}, type_info)

    parser = BinaryParser(writer.data)
    assert parser.read_single() == pytest.approx(1.5)
    assert parser.read_single() == pytest.approx(2.5)


def test_unparse_array_int32():
    """Should write Array<Int32>."""
    writer = BinaryWriter()
    element_type = TypeInfo(info=SerializationTypeCode.Int32)
    type_info = TypeInfo(info=SerializationTypeCode.Array, sub_types=[element_type])
    unparse_by_type(writer, [], [10, 20, 30], type_info)

    parser = BinaryParser(writer.data)
    assert parser.read_int32() == 12  # data-length
    assert parser.read_int32() == 3  # element count
    assert parser.read_int32() == 10
    assert parser.read_int32() == 20
    assert parser.read_int32() == 30


def test_round_trip_complex_structure():
    """Should round-trip complex nested structure."""
    # Create templates
    inner_field = TypeTemplateMember(name="value", type=TypeInfo(info=SerializationTypeCode.Int32))
    inner_template = TypeTemplate(name="Inner", fields=[inner_field], properties=[])

    outer_field = TypeTemplateMember(
        name="inner", type=TypeInfo(info=SerializationTypeCode.UserDefined, template_name="Inner")
    )
    outer_template = TypeTemplate(name="Outer", fields=[outer_field], properties=[])
    templates = [inner_template, outer_template]

    # Original data
    original = {"inner": {"value": 42}}

    # Write
    writer = BinaryWriter()
    unparse_by_template(writer, templates, "Outer", original)

    # Read
    parser = BinaryParser(writer.data)
    parsed = parse_by_template(parser, templates, "Outer")

    assert parsed == original


def test_template_not_found():
    """Should raise error when template not found."""
    writer = BinaryWriter()
    parser = BinaryParser(writer.data)

    with pytest.raises(CorruptionError, match="Template.*not found"):
        parse_by_template(parser, [], "NonExistent")
