from typing import TYPE_CHECKING, cast

from uapi.UApiSchema import UApiSchema
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


if TYPE_CHECKING:
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration


def parse_uapi_schema(
    u_api_schema_document_name_to_pseudo_json: dict[str, list[object]]
) -> 'UApiSchema':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.ApplyErrorToParsedTypes import apply_error_to_parsed_types
    from uapi.internal.schema.CatchErrorCollisions import catch_error_collisions
    from uapi.internal.schema.FindMatchingSchemaKey import find_matching_schema_key
    from uapi.internal.schema.FindSchemaKey import find_schema_key
    from uapi.internal.schema.GetOrParseType import get_or_parse_type
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseErrorType import parse_error_type
    from uapi.internal.schema.ParseHeadersType import parse_headers_type
    from uapi.internal.types.UError import UError
    from collections import OrderedDict

    original_schema: dict[str, object] = {}
    parsed_types: dict[str, UType] = {}
    parse_failures: list[SchemaParseFailure] = []
    failed_types: set[str] = set()
    schema_keys_to_document_names: dict[str, str] = {}
    schema_keys_to_index: dict[str, int] = {}
    schema_keys: set[str] = set()

    ordered_document_names = sorted(
        list(u_api_schema_document_name_to_pseudo_json.keys()))

    for document_name in ordered_document_names:
        u_api_schema_pseudo_json = u_api_schema_document_name_to_pseudo_json[document_name]

        index = -1
        for definition in u_api_schema_pseudo_json:

            index += 1
            loop_path = [index]

            if not isinstance(definition, dict):
                this_parse_failures = get_type_unexpected_parse_failure(
                    document_name, cast(list[object], loop_path), definition, "Object")
                parse_failures.extend(this_parse_failures)
                continue

            def_ = definition

            try:
                schema_key = find_schema_key(document_name, def_, index)

                matching_schema_key = find_matching_schema_key(
                    schema_keys, schema_key)
                if matching_schema_key is not None:
                    other_path_index = schema_keys_to_index[matching_schema_key]
                    other_document_name = schema_keys_to_document_names[matching_schema_key]
                    final_path = loop_path + [schema_key]
                    parse_failures.append(
                        SchemaParseFailure(
                            document_name, cast(list[object], final_path),
                            "PathCollision",
                            {"document": other_document_name, "path": [other_path_index, matching_schema_key]})
                    )
                    continue

                schema_keys.add(schema_key)
                schema_keys_to_index[schema_key] = index
                schema_keys_to_document_names[schema_key] = document_name
                if not document_name.endswith('_'):
                    original_schema[schema_key] = def_

            except UApiSchemaParseError as e:
                parse_failures.extend(e.schema_parse_failures)
                continue

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    request_header_keys: set[str] = set()
    response_header_keys: set[str] = set()
    error_keys: set[str] = set()
    root_type_parameter_count = 0

    for schema_key in schema_keys:
        if schema_key.startswith("info."):
            continue
        elif schema_key.startswith("requestHeader."):
            request_header_keys.add(schema_key)
            continue
        elif schema_key.startswith("responseHeader."):
            response_header_keys.add(schema_key)
            continue
        elif schema_key.startswith("errors."):
            error_keys.add(schema_key)
            continue

        this_index = schema_keys_to_index[schema_key]
        document_name = schema_keys_to_document_names[schema_key]

        try:
            get_or_parse_type(
                document_name,
                [this_index],
                schema_key,
                root_type_parameter_count,
                u_api_schema_document_name_to_pseudo_json,
                schema_keys_to_document_names,
                schema_keys_to_index,
                parsed_types,
                parse_failures,
                failed_types,
            )
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    errors: list[UError] = []

    for this_key in error_keys:
        this_index = schema_keys_to_index[this_key]
        this_document_name = schema_keys_to_document_names[this_key]
        u_api_schema_pseudo_json = u_api_schema_document_name_to_pseudo_json[
            this_document_name]
        def_ = cast(dict[str, object],
                    u_api_schema_pseudo_json[this_index])

        try:
            error = parse_error_type(
                def_,
                this_document_name,
                u_api_schema_document_name_to_pseudo_json,
                this_key,
                this_index,
                schema_keys_to_document_names,
                schema_keys_to_index,
                parsed_types,
                parse_failures,
                failed_types,
            )
            errors.append(error)
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    try:
        catch_error_collisions(u_api_schema_document_name_to_pseudo_json,
                               error_keys, schema_keys_to_index, schema_keys_to_document_names)
    except UApiSchemaParseError as e:
        parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    for error in errors:
        try:
            apply_error_to_parsed_types(
                error, parsed_types, schema_keys_to_document_names, schema_keys_to_index)
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    request_headers: dict[str, UFieldDeclaration] = {}
    response_headers: dict[str, UFieldDeclaration] = {}

    for request_header_key in request_header_keys:
        this_index = schema_keys_to_index[request_header_key]
        this_document_name = schema_keys_to_document_names[request_header_key]
        u_api_schema_pseudo_json = u_api_schema_document_name_to_pseudo_json[
            this_document_name]
        def_ = cast(dict[str, object],
                    u_api_schema_pseudo_json[this_index])
        header_field = request_header_key[len("requestHeader."):]

        try:
            request_header_type = parse_headers_type(
                this_document_name,
                def_,
                request_header_key,
                header_field,
                this_index,
                u_api_schema_document_name_to_pseudo_json,
                schema_keys_to_document_names,
                schema_keys_to_index,
                parsed_types,
                parse_failures,
                failed_types,
            )
            request_headers[request_header_type.field_name] = request_header_type
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    for response_header_key in response_header_keys:
        this_index = schema_keys_to_index[response_header_key]
        this_document_name = schema_keys_to_document_names[response_header_key]
        u_api_schema_pseudo_json = u_api_schema_document_name_to_pseudo_json[
            this_document_name]
        def_ = cast(dict[str, object],
                    u_api_schema_pseudo_json[this_index])
        header_field = response_header_key[len("responseHeader."):]

        try:
            response_header_type = parse_headers_type(
                this_document_name,
                def_,
                response_header_key,
                header_field,
                this_index,
                u_api_schema_document_name_to_pseudo_json,
                schema_keys_to_document_names,
                schema_keys_to_index,
                parsed_types,
                parse_failures,
                failed_types,
            )
            response_headers[response_header_type.field_name] = response_header_type
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    final_original_schema = [original_schema[k]
                             for k in sorted(original_schema.keys(), key=lambda k: (not k.startswith("info."), k))]

    return UApiSchema(
        final_original_schema,
        parsed_types,
        request_headers,
        response_headers
    )
