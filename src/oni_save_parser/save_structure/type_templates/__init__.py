"""KSerialization type template system."""

from .template_parser import (
    parse_template,
    parse_templates,
    unparse_template,
    unparse_templates,
    validate_dotnet_identifier_name,
)
from .type_data_parser import (
    parse_by_template,
    parse_by_type,
    unparse_by_template,
    unparse_by_type,
)
from .type_info_parser import parse_type_info, unparse_type_info
from .types import (
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

__all__ = [
    "SerializationTypeCode",
    "SerializationTypeInfo",
    "TypeInfo",
    "TypeTemplate",
    "TypeTemplateMember",
    "get_type_code",
    "is_value_type",
    "is_generic_type",
    "GENERIC_TYPES",
    "parse_type_info",
    "unparse_type_info",
    "parse_template",
    "parse_templates",
    "unparse_template",
    "unparse_templates",
    "validate_dotnet_identifier_name",
    "parse_by_type",
    "unparse_by_type",
    "parse_by_template",
    "unparse_by_template",
]
