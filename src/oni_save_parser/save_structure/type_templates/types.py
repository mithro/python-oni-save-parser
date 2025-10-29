"""KSerialization type system data structures."""

from dataclasses import dataclass
from enum import IntEnum


class SerializationTypeCode(IntEnum):
    """Type codes from KSerialization.

    These values appear in the lower 6 bits of SerializationTypeInfo.
    """

    UserDefined = 0
    SByte = 1
    Byte = 2
    Boolean = 3
    Int16 = 4
    UInt16 = 5
    Int32 = 6
    UInt32 = 7
    Int64 = 8
    UInt64 = 9
    Single = 10
    Double = 11
    String = 12
    Enumeration = 13
    Vector2I = 14
    Vector2 = 15
    Vector3 = 16
    Array = 17
    Pair = 18
    Dictionary = 19
    List = 20
    HashSet = 21
    Queue = 22
    Colour = 23


class SerializationTypeInfo:
    """Bit flags for SerializationTypeInfo byte.

    The info byte combines type code (lower 6 bits) with flags.
    """

    VALUE_MASK = 0x3F  # Mask for type code
    IS_VALUE_TYPE = 0x40  # Flag for value types
    IS_GENERIC_TYPE = 0x80  # Flag for generic types


def get_type_code(info: int) -> SerializationTypeCode:
    """Extract type code from info byte.

    Args:
        info: SerializationTypeInfo byte

    Returns:
        Type code enum value
    """
    return SerializationTypeCode(info & SerializationTypeInfo.VALUE_MASK)


def is_value_type(info: int) -> bool:
    """Check if info byte indicates value type.

    Args:
        info: SerializationTypeInfo byte

    Returns:
        True if value type flag set
    """
    return bool(info & SerializationTypeInfo.IS_VALUE_TYPE)


def is_generic_type(info: int) -> bool:
    """Check if info byte indicates generic type.

    Args:
        info: SerializationTypeInfo byte

    Returns:
        True if generic type flag set
    """
    return bool(info & SerializationTypeInfo.IS_GENERIC_TYPE)


# Types that can be generic
GENERIC_TYPES: list[SerializationTypeCode] = [
    SerializationTypeCode.Pair,
    SerializationTypeCode.Dictionary,
    SerializationTypeCode.List,
    SerializationTypeCode.HashSet,
    SerializationTypeCode.UserDefined,
    SerializationTypeCode.Queue,
]


@dataclass
class TypeInfo:
    """Type information from KSerialization.

    Namespace: KSerialization
    Class: TypeInfo
    """

    info: int  # SerializationTypeInfo byte
    template_name: str | None = None  # For UserDefined/Enumeration types
    sub_types: list["TypeInfo"] | None = None  # For generic types/arrays


@dataclass
class TypeTemplateMember:
    """Field or property in a type template.

    Namespace: KSerialization
    Class: DeserializationTemplate.SerializedInfo
    """

    name: str  # Field/property name
    type: TypeInfo  # Type information


@dataclass
class TypeTemplate:
    """Template describing how to serialize/deserialize a .NET class.

    Namespace: KSerialization
    Class: DeserializationTemplate
    """

    name: str  # .NET class name (short or fully qualified)
    fields: list[TypeTemplateMember]  # Field members in serialization order
    properties: list[TypeTemplateMember]  # Property members in serialization order
