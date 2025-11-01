"""Tests for type template data structures."""

from oni_save_parser.save_structure.type_templates.types import (
    GENERIC_TYPES,
    SerializationTypeCode,
    SerializationTypeInfo,
    TypeInfo,
    TypeTemplate,
    TypeTemplateMember,
    get_type_code,
    is_generic_type,
    is_value_type,
)


def test_serialization_type_code_values() -> None:
    """Should have all KSerialization type codes."""
    assert SerializationTypeCode.UserDefined.value == 0
    assert SerializationTypeCode.Int32.value == 6
    assert SerializationTypeCode.String.value == 12
    assert SerializationTypeCode.Array.value == 17
    assert SerializationTypeCode.List.value == 20


def test_serialization_type_info_flags() -> None:
    """Should have correct flag values."""
    assert SerializationTypeInfo.VALUE_MASK == 0x3F
    assert SerializationTypeInfo.IS_VALUE_TYPE == 0x40
    assert SerializationTypeInfo.IS_GENERIC_TYPE == 0x80


def test_get_type_code() -> None:
    """Should extract type code from info byte."""
    assert get_type_code(6) == SerializationTypeCode.Int32
    assert get_type_code(6 | 0x40) == SerializationTypeCode.Int32
    assert get_type_code(6 | 0x80) == SerializationTypeCode.Int32


def test_is_value_type() -> None:
    """Should detect value type flag."""
    assert is_value_type(0x40) is True
    assert is_value_type(6 | 0x40) is True
    assert is_value_type(6) is False


def test_is_generic_type() -> None:
    """Should detect generic type flag."""
    assert is_generic_type(0x80) is True
    assert is_generic_type(20 | 0x80) is True
    assert is_generic_type(20) is False


def test_generic_types_list() -> None:
    """Should list all generic-capable types."""
    assert SerializationTypeCode.List in GENERIC_TYPES
    assert SerializationTypeCode.Dictionary in GENERIC_TYPES
    assert SerializationTypeCode.Int32 not in GENERIC_TYPES


def test_type_info_creation() -> None:
    """Should create TypeInfo instance."""
    info = TypeInfo(info=6, template_name=None, sub_types=None)
    assert info.info == 6
    assert info.template_name is None


def test_type_template_member_creation() -> None:
    """Should create TypeTemplateMember."""
    type_info = TypeInfo(info=6, template_name=None, sub_types=None)
    member = TypeTemplateMember(name="testField", type=type_info)
    assert member.name == "testField"
    assert member.type.info == 6


def test_type_template_creation() -> None:
    """Should create TypeTemplate."""
    template = TypeTemplate(name="TestClass", fields=[], properties=[])
    assert template.name == "TestClass"
    assert len(template.fields) == 0
    assert len(template.properties) == 0
