from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.schema.ParseContext import ParseContext
    from uapi.internal.types.UHeaders import UHeaders


def parse_headers_type(path: list[object], headers_definition_as_parsed_json: dict[str, object], schema_key: str, ctx: 'ParseContext') -> 'UHeaders':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.schema.ParseStructFields import parse_struct_fields
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
    from uapi.internal.types.UHeaders import UHeaders

    parse_failures = []
    request_headers = {}
    response_headers = {}

    request_headers_def = headers_definition_as_parsed_json.get(schema_key)

    this_path = path + [schema_key]

    if not isinstance(request_headers_def, dict):
        branch_parse_failures = get_type_unexpected_parse_failure(
            ctx.document_name,
            this_path,
            request_headers_def,
            'Object',
        )
        parse_failures.extend(branch_parse_failures)
    else:
        try:
            request_fields = parse_struct_fields(this_path, request_headers_def, ctx)

            # All headers are optional
            for field in request_fields:
                request_fields[field].optional = True

            request_headers.update(request_fields)
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)
        except Exception as e:
            raise e

    response_key = '->'
    response_path = path + [response_key]

    if response_key not in headers_definition_as_parsed_json:
        parse_failures.append(
            SchemaParseFailure(ctx.document_name, response_path, 'RequiredObjectKeyMissing', {
                'key': response_key,
            })
        )

    response_headers_def = headers_definition_as_parsed_json.get(response_key)

    if not isinstance(response_headers_def, dict):
        branch_parse_failures = get_type_unexpected_parse_failure(
            ctx.document_name,
            this_path,
            response_headers_def,
            'Object',
        )
        parse_failures.extend(branch_parse_failures)
    else:
        try:
            response_fields = parse_struct_fields(response_path, response_headers_def, ctx)

            # All headers are optional
            for field in response_fields:
                response_fields[field].optional = True

            response_headers.update(response_fields)
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)
        except Exception as e:
            raise e

    if parse_failures:
        raise UApiSchemaParseError(parse_failures, ctx.uapi_schema_document_names_to_json)

    return UHeaders(schema_key, request_headers, response_headers)
