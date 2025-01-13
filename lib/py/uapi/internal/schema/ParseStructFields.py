from typing import TYPE_CHECKING

from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

if TYPE_CHECKING:
    from uapi.internal.schema.ParseContext import ParseContext
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration


def parse_struct_fields(reference_struct: dict[str, object], ctx: 'ParseContext') -> dict[str, 'UFieldDeclaration']:
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.ParseField import parse_field

    parse_failures = []
    fields: dict[str, 'UFieldDeclaration'] = {}

    for field_declaration, type_declaration_value in reference_struct.items():
        for existing_field in fields.keys():
            existing_field_no_opt = existing_field.split("!")[0]
            field_no_opt = field_declaration.split("!")[0]
            if field_no_opt == existing_field_no_opt:
                final_path = ctx.path + [field_declaration]
                final_other_path = ctx.path + [existing_field]
                parse_failures.append(SchemaParseFailure(
                    ctx.document_name, final_path, "PathCollision", {"document": ctx.document_name, "path": final_other_path}))

        try:
            parsed_field = parse_field(
                field_declaration, type_declaration_value, ctx)
            field_name = parsed_field.field_name
            fields[field_name] = parsed_field
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    return fields
