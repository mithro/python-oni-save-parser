"""Tests for TypeTemplate parsing."""

import pytest
from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.type_templates.template_parser import (
    parse_template,
    parse_templates,
    unparse_template,
    unparse_templates,
    validate_dotnet_identifier_name,
)
from oni_save_parser.save_structure.type_templates.types import (
    TypeInfo,
    TypeTemplate,
    TypeTemplateMember,
)


def test_validate_dotnet_identifier_name_valid():
    """Should accept valid identifier names."""
    assert validate_dotnet_identifier_name("TestClass") == "TestClass"
    assert validate_dotnet_identifier_name("_field") == "_field"
    assert validate_dotnet_identifier_name("prop123") == "prop123"


def test_validate_dotnet_identifier_name_null():
    """Should reject null/empty names."""
    with pytest.raises(CorruptionError, match="must not be null or zero length"):
        validate_dotnet_identifier_name(None)


def test_validate_dotnet_identifier_name_empty():
    """Should reject empty names."""
    with pytest.raises(CorruptionError, match="must not be null or zero length"):
        validate_dotnet_identifier_name("")


def test_validate_dotnet_identifier_name_too_long():
    """Should reject names >= 512 chars."""
    long_name = "a" * 512
    with pytest.raises(CorruptionError, match="exceeded 511 characters"):
        validate_dotnet_identifier_name(long_name)


def test_validate_dotnet_identifier_name_non_printable():
    """Should reject names with non-printable characters."""
    invalid_name = "Test\x00Class"
    with pytest.raises(CorruptionError, match="non-printable characters"):
        validate_dotnet_identifier_name(invalid_name)


def test_parse_simple_template():
    """Should parse template with fields and properties."""
    # Template: name="TestClass", 2 fields, 1 property
    writer = BinaryWriter()
    writer.write_klei_string("TestClass")
    writer.write_int32(2)  # field count
    writer.write_int32(1)  # property count

    # Field 1: name="field1", type=Int32 (6)
    writer.write_klei_string("field1")
    writer.write_byte(6)

    # Field 2: name="field2", type=String (12)
    writer.write_klei_string("field2")
    writer.write_byte(12)

    # Property 1: name="prop1", type=Boolean (3)
    writer.write_klei_string("prop1")
    writer.write_byte(3)

    parser = BinaryParser(writer.data)
    template = parse_template(parser)

    assert template.name == "TestClass"
    assert len(template.fields) == 2
    assert len(template.properties) == 1

    assert template.fields[0].name == "field1"
    assert template.fields[0].type.info == 6

    assert template.fields[1].name == "field2"
    assert template.fields[1].type.info == 12

    assert template.properties[0].name == "prop1"
    assert template.properties[0].type.info == 3


def test_parse_template_no_members():
    """Should parse template with no fields or properties."""
    writer = BinaryWriter()
    writer.write_klei_string("EmptyClass")
    writer.write_int32(0)  # field count
    writer.write_int32(0)  # property count

    parser = BinaryParser(writer.data)
    template = parse_template(parser)

    assert template.name == "EmptyClass"
    assert len(template.fields) == 0
    assert len(template.properties) == 0


def test_parse_templates():
    """Should parse multiple templates."""
    writer = BinaryWriter()
    writer.write_int32(2)  # template count

    # Template 1
    writer.write_klei_string("Class1")
    writer.write_int32(1)  # field count
    writer.write_int32(0)  # property count
    writer.write_klei_string("field1")
    writer.write_byte(6)  # Int32

    # Template 2
    writer.write_klei_string("Class2")
    writer.write_int32(0)  # field count
    writer.write_int32(1)  # property count
    writer.write_klei_string("prop1")
    writer.write_byte(12)  # String

    parser = BinaryParser(writer.data)
    templates = parse_templates(parser)

    assert len(templates) == 2
    assert templates[0].name == "Class1"
    assert len(templates[0].fields) == 1
    assert templates[1].name == "Class2"
    assert len(templates[1].properties) == 1


def test_unparse_simple_template():
    """Should write template with fields and properties."""
    field1 = TypeTemplateMember(name="field1", type=TypeInfo(info=6))
    field2 = TypeTemplateMember(name="field2", type=TypeInfo(info=12))
    prop1 = TypeTemplateMember(name="prop1", type=TypeInfo(info=3))

    template = TypeTemplate(
        name="TestClass", fields=[field1, field2], properties=[prop1]
    )

    writer = BinaryWriter()
    unparse_template(writer, template)

    # Parse back and verify
    parser = BinaryParser(writer.data)
    parsed = parse_template(parser)

    assert parsed.name == "TestClass"
    assert len(parsed.fields) == 2
    assert len(parsed.properties) == 1


def test_unparse_templates():
    """Should write multiple templates."""
    template1 = TypeTemplate(
        name="Class1",
        fields=[TypeTemplateMember(name="field1", type=TypeInfo(info=6))],
        properties=[],
    )
    template2 = TypeTemplate(
        name="Class2",
        fields=[],
        properties=[TypeTemplateMember(name="prop1", type=TypeInfo(info=12))],
    )

    templates = [template1, template2]

    writer = BinaryWriter()
    unparse_templates(writer, templates)

    # Parse back and verify
    parser = BinaryParser(writer.data)
    parsed = parse_templates(parser)

    assert len(parsed) == 2
    assert parsed[0].name == "Class1"
    assert parsed[1].name == "Class2"


def test_round_trip_complex_template():
    """Should round-trip template with complex types."""
    # Create a template with array and generic types
    array_field = TypeTemplateMember(
        name="arrayField",
        type=TypeInfo(info=17, sub_types=[TypeInfo(info=6)]),  # Array<Int32>
    )
    list_prop = TypeTemplateMember(
        name="listProp",
        type=TypeInfo(info=148, sub_types=[TypeInfo(info=12)]),  # List<String>
    )

    template = TypeTemplate(name="ComplexClass", fields=[array_field], properties=[list_prop])

    # Write
    writer = BinaryWriter()
    unparse_template(writer, template)

    # Read back
    parser = BinaryParser(writer.data)
    parsed = parse_template(parser)

    assert parsed.name == "ComplexClass"
    assert len(parsed.fields) == 1
    assert parsed.fields[0].name == "arrayField"
    assert parsed.fields[0].type.info == 17
    assert parsed.fields[0].type.sub_types[0].info == 6

    assert len(parsed.properties) == 1
    assert parsed.properties[0].name == "listProp"
    assert parsed.properties[0].type.info == 148
    assert parsed.properties[0].type.sub_types[0].info == 12
