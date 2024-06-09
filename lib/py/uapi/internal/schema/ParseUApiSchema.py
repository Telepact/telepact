from typing import list, dict, object, Union, Set, TYPE_CHECKING

from uapi.UApiSchema import UApiSchema
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


if TYPE_CHECKING:
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration


def parse_uapi_schema(
    u_api_schema_pseudo_json: list[object],
    type_extensions: dict[str, 'UType'],
    path_offset: int
) -> 'UApiSchema':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.ApplyErrorToParsedTypes import apply_error_to_parsed_types
    from uapi.internal.schema.CatchErrorCollisions import catch_error_collisions
    from uapi.internal.schema.FindMatchingSchemaKey import find_matching_schema_key
    from uapi.internal.schema.FindSchemaKey import find_schema_key
    from uapi.internal.schema.GetOrParseType import get_or_parse_type
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.OffsetSchemaIndex import offset_schema_index
    from uapi.internal.schema.ParseErrorType import parse_error_type
    from uapi.internal.schema.ParseHeadersType import parse_headers_type

    parsed_types: dict[str, UType] = {}
    parse_failures: list[SchemaParseFailure] = []
    failed_types: Set[str] = set()
    schema_keys_to_index: dict[str, int] = {}
    schema_keys: Set[str] = set()
    error_indices: Set[int] = set()

    index = -1
    for definition in u_api_schema_pseudo_json:
        index += 1
        loop_path = [index]

        if not isinstance(definition, dict):
            this_parse_failures = get_type_unexpected_parse_failure(
                loop_path, definition, "Object")
            parse_failures.extend(this_parse_failures)
            continue

        def_ = definition

        try:
            schema_key = find_schema_key(def_, index)
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)
            continue

        if schema_key == "errors":
            error_indices.add(index)
            continue

        ignore_if_duplicate = def_.get("_ignoreIfDuplicate", False)
        matching_schema_key = find_matching_schema_key(schema_keys, schema_key)
        if matching_schema_key is not None:
            if not ignore_if_duplicate:
                other_path_index = schema_keys_to_index[matching_schema_key]
                final_path = loop_path + [schema_key]
                parse_failures.append(
                    SchemaParseFailure(
                        final_path,
                        "PathCollision",
                        {"other": [other_path_index, matching_schema_key]},
                        schema_key,
                    )
                )
            continue

        schema_keys.add(schema_key)
        schema_keys_to_index[schema_key] = index

    if parse_failures:
        offset_parse_failures = offset_schema_index(
            parse_failures, path_offset, schema_keys_to_index, error_indices)
        raise UApiSchemaParseError(offset_parse_failures)

    request_header_keys: Set[str] = set()
    response_header_keys: Set[str] = set()
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

        this_index = schema_keys_to_index[schema_key]

        try:
            get_or_parse_type(
                [this_index],
                schema_key,
                root_type_parameter_count,
                u_api_schema_pseudo_json,
                schema_keys_to_index,
                parsed_types,
                type_extensions,
                parse_failures,
                failed_types,
            )
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        offset_parse_failures = offset_schema_index(
            parse_failures, path_offset, schema_keys_to_index, error_indices)
        raise UApiSchemaParseError(offset_parse_failures)

    try:
        catch_error_collisions(u_api_schema_pseudo_json,
                               error_indices, schema_keys_to_index)

        for this_index in error_indices:
            def_ = u_api_schema_pseudo_json[this_index]

            try:
                error = parse_error_type(
                    def_,
                    u_api_schema_pseudo_json,
                    this_index,
                    schema_keys_to_index,
                    parsed_types,
                    type_extensions,
                    parse_failures,
                    failed_types,
                )
                apply_error_to_parsed_types(
                    this_index, error, parsed_types, schema_keys_to_index)
            except UApiSchemaParseError as e:
                parse_failures.extend(e.schema_parse_failures)

    except UApiSchemaParseError as e:
        parse_failures.extend(e.schema_parse_failures)

    request_headers: dict[str, UFieldDeclaration] = {}
    response_headers: dict[str, UFieldDeclaration] = {}

    try:
        for request_header_key in request_header_keys:
            this_index = schema_keys_to_index[request_header_key]
            def_ = u_api_schema_pseudo_json[this_index]
            header_field = request_header_key[len("requestHeader."):]

            try:
                request_header_type = parse_headers_type(
                    def_,
                    request_header_key,
                    header_field,
                    this_index,
                    u_api_schema_pseudo_json,
                    schema_keys_to_index,
                    parsed_types,
                    type_extensions,
                    parse_failures,
                    failed_types,
                )
                request_headers[request_header_type.field_name] = request_header_type
            except UApiSchemaParseError as e:
                parse_failures.extend(e.schema_parse_failures)

        for response_header_key in response_header_keys:
            this_index = schema_keys_to_index[response_header_key]
            def_ = u_api_schema_pseudo_json[this_index]
            header_field = response_header_key[len("responseHeader."):]

            try:
                response_header_type = parse_headers_type(
                    def_,
                    response_header_key,
                    header_field,
                    this_index,
                    u_api_schema_pseudo_json,
                    schema_keys_to_index,
                    parsed_types,
                    type_extensions,
                    parse_failures,
                    failed_types,
                )
                response_headers[response_header_type.field_name] = response_header_type
            except UApiSchemaParseError as e:
                parse_failures.extend(e.schema_parse_failures)

    except UApiSchemaParseError as e:
        parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        offset_parse_failures = offset_schema_index(
            parse_failures, path_offset, schema_keys_to_index, error_indices)
        raise UApiSchemaParseError(offset_parse_failures)

    return UApiSchema(
        u_api_schema_pseudo_json,
        parsed_types,
        request_headers,
        response_headers,
        type_extensions,
    )
