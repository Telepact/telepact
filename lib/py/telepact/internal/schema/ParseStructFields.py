#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

from ...internal.schema.SchemaParseFailure import SchemaParseFailure

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ..types.TFieldDeclaration import TFieldDeclaration


def parse_struct_fields(path: list[object], reference_struct: dict[str, object], is_header: bool, ctx: 'ParseContext') -> dict[str, 'TFieldDeclaration']:
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.ParseField import parse_field

    parse_failures = []
    fields: dict[str, 'TFieldDeclaration'] = {}

    for field_declaration, type_declaration_value in reference_struct.items():
        for existing_field in fields.keys():
            existing_field_no_opt = existing_field.split("!")[0]
            field_no_opt = field_declaration.split("!")[0]
            if field_no_opt == existing_field_no_opt:
                struct_path = list(path)
                parse_failures.append(SchemaParseFailure(
                    ctx.document_name, struct_path, "DuplicateField", {
                        "field": field_no_opt}))

        try:
            parsed_field = parse_field(path,
                                       field_declaration, type_declaration_value,
                                       is_header, ctx)
            field_name = parsed_field.field_name
            fields[field_name] = parsed_field
        except TelepactSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, ctx.telepact_schema_document_names_to_json)

    return fields
