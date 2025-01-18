from typing import TYPE_CHECKING
from uapi.internal.types.UFieldDeclaration import UFieldDeclaration

if TYPE_CHECKING:
    from uapi.internal.schema.ParseContext import ParseContext


def parse_headers_type(path: list[object], type_declaration_value: object,
                       header_field: str,
                       ctx: 'ParseContext') -> 'UFieldDeclaration':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseTypeDeclaration import parse_type_declaration

    if not isinstance(type_declaration_value, list):
        raise UApiSchemaParseError(get_type_unexpected_parse_failure(
            ctx.document_name, path, type_declaration_value, "Array"), ctx.uapi_schema_document_names_to_json)

    type_declaration_array = type_declaration_value

    try:
        type_declaration = parse_type_declaration(
            path, type_declaration_array, ctx)

        return UFieldDeclaration(header_field, type_declaration, False)
    except UApiSchemaParseError as e:
        raise UApiSchemaParseError(
            e.schema_parse_failures, ctx.uapi_schema_document_names_to_json)
