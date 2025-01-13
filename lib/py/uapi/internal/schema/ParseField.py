import re
from typing import TYPE_CHECKING
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UFieldDeclaration import UFieldDeclaration

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType
    from uapi.internal.schema.ParseContext import ParseContext


def parse_field(field_declaration: str, type_declaration_value: object,
                ctx: 'ParseContext') -> 'UFieldDeclaration':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseTypeDeclaration import parse_type_declaration

    regex_string = r"^([a-z][a-zA-Z0-9_]*)(!)?$"
    regex = re.compile(regex_string)

    matcher = regex.match(field_declaration)
    if not matcher:
        final_path = ctx.path + [field_declaration]
        raise UApiSchemaParseError([SchemaParseFailure(ctx.document_name, final_path,
                                                       "KeyRegexMatchFailed",
                                                       {"regex": regex_string})], ctx.uapi_schema_document_names_to_json)

    field_name = matcher.group(0)
    optional = bool(matcher.group(2))

    this_path = ctx.path + [field_name]

    if not isinstance(type_declaration_value, list):
        raise UApiSchemaParseError(get_type_unexpected_parse_failure(
            ctx.document_name,
            this_path,
            type_declaration_value,
            "Array"), ctx.uapi_schema_document_names_to_json)
    type_declaration_array = type_declaration_value

    type_declaration = parse_type_declaration(
        type_declaration_array, ctx.copy(path=this_path))

    return UFieldDeclaration(field_name, type_declaration, optional)
