#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING, cast

from ...TelepactSchema import TelepactSchema
from .SchemaParseFailure import SchemaParseFailure

import json


if TYPE_CHECKING:
    from ..types.TType import TType
    from ..types.TFieldDeclaration import TFieldDeclaration


def parse_telepact_schema(
    telepact_schema_document_names_to_json: dict[str, str],
) -> 'TelepactSchema':
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from .ApplyErrorToParsedTypes import apply_error_to_parsed_types
    from .CatchErrorCollisions import catch_error_collisions
    from .FindMatchingSchemaKey import find_matching_schema_key
    from .FindSchemaKey import find_schema_key
    from .GetOrParseType import get_or_parse_type
    from .GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from .ParseErrorType import parse_error_type
    from .ParseHeadersType import parse_headers_type
    from .ParseContext import ParseContext
    from .GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json
    from ..types.TError import TError
    from collections import OrderedDict
    from ..types.THeaders import THeaders
    from .CatchHeaderCollisions import catch_header_collisions

    original_schema: dict[str, object] = {}
    parsed_types: dict[str, TType] = {}
    fn_error_regexes: dict[str, str] = {}
    parse_failures: list[SchemaParseFailure] = []
    failed_types: set[str] = set()
    schema_keys_to_document_names: dict[str, str] = {}
    schema_keys_to_index: dict[str, int] = {}
    schema_keys: set[str] = set()

    ordered_document_names = sorted(
        list(telepact_schema_document_names_to_json.keys()))

    telepact_schema_document_name_to_pseudo_json: dict[str, list[object]] = {}

    for document_name, telepact_schema_json in telepact_schema_document_names_to_json.items():
        try:
            telepact_schema_pseudo_json_init = json.loads(telepact_schema_json)
        except json.JSONDecodeError as e:
            raise TelepactSchemaParseError(
                [SchemaParseFailure(document_name, [], "JsonInvalid", {})], telepact_schema_document_names_to_json) from e

        if not isinstance(telepact_schema_pseudo_json_init, list):
            this_parse_failure = get_type_unexpected_parse_failure(
                document_name, [], telepact_schema_pseudo_json_init, "Array"
            )
            raise TelepactSchemaParseError(
                this_parse_failure, telepact_schema_document_names_to_json)

        telepact_schema_document_name_to_pseudo_json[document_name] = telepact_schema_pseudo_json_init

    for document_name in ordered_document_names:
        telepact_schema_pseudo_json = telepact_schema_document_name_to_pseudo_json[document_name]

        index = -1
        for definition in telepact_schema_pseudo_json:

            index += 1
            loop_path = [index]

            if not isinstance(definition, dict):
                this_parse_failures = get_type_unexpected_parse_failure(
                    document_name, cast(list[object], loop_path), definition, "Object")
                parse_failures.extend(this_parse_failures)
                continue

            def_ = definition

            try:
                schema_key = find_schema_key(
                    document_name, def_, index, telepact_schema_document_names_to_json)

                matching_schema_key = find_matching_schema_key(
                    schema_keys, schema_key)
                if matching_schema_key is not None:
                    other_path_index = schema_keys_to_index[matching_schema_key]
                    other_document_name = schema_keys_to_document_names[matching_schema_key]
                    final_path = loop_path + [schema_key]
                    final_other_path = [other_path_index, matching_schema_key]
                    document_json = telepact_schema_document_names_to_json[other_document_name]
                    other_location_pseudo_json = get_path_document_coordinates_pseudo_json(
                        final_other_path, document_json)
                    parse_failures.append(
                        SchemaParseFailure(
                            document_name, cast(list[object], final_path),
                            "PathCollision",
                            {
                                "document": other_document_name,
                                "path": final_other_path,
                                "location": other_location_pseudo_json})
                    )
                    continue

                schema_keys.add(schema_key)
                schema_keys_to_index[schema_key] = index
                schema_keys_to_document_names[schema_key] = document_name
                if document_name == 'auto_' or document_name == 'auth_' or not document_name.endswith('_'):
                    original_schema[schema_key] = def_

            except TelepactSchemaParseError as e:
                parse_failures.extend(e.schema_parse_failures)
                continue

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, telepact_schema_document_names_to_json)

    header_keys: set[str] = set()
    error_keys: set[str] = set()

    for schema_key in schema_keys:
        if schema_key.startswith("info."):
            continue
        elif schema_key.startswith("headers."):
            header_keys.add(schema_key)
            continue
        elif schema_key.startswith("errors."):
            error_keys.add(schema_key)
            continue

        this_index = schema_keys_to_index[schema_key]
        document_name = schema_keys_to_document_names[schema_key]

        try:
            get_or_parse_type(
                [this_index],
                schema_key,
                ParseContext(
                    document_name,
                    telepact_schema_document_name_to_pseudo_json,
                    telepact_schema_document_names_to_json,
                    schema_keys_to_document_names,
                    schema_keys_to_index,
                    parsed_types,
                    fn_error_regexes,
                    parse_failures,
                    failed_types
                )
            )
        except TelepactSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, telepact_schema_document_names_to_json)

    errors: list[TError] = []

    for this_key in error_keys:
        this_index = schema_keys_to_index[this_key]
        this_document_name = schema_keys_to_document_names[this_key]
        telepact_schema_pseudo_json = telepact_schema_document_name_to_pseudo_json[
            this_document_name]
        def_ = cast(dict[str, object],
                    telepact_schema_pseudo_json[this_index])

        try:
            error = parse_error_type(
                [this_index],
                def_,
                this_key,
                ParseContext(
                    this_document_name,
                    telepact_schema_document_name_to_pseudo_json,
                    telepact_schema_document_names_to_json,
                    schema_keys_to_document_names,
                    schema_keys_to_index,
                    parsed_types,
                    fn_error_regexes,
                    parse_failures,
                    failed_types
                )
            )
            errors.append(error)
        except TelepactSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, telepact_schema_document_names_to_json)

    try:
        catch_error_collisions(telepact_schema_document_name_to_pseudo_json,
                               error_keys, schema_keys_to_index, schema_keys_to_document_names, telepact_schema_document_names_to_json)
    except TelepactSchemaParseError as e:
        parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, telepact_schema_document_names_to_json)

    for error in errors:
        try:
            apply_error_to_parsed_types(
                error, parsed_types, schema_keys_to_document_names, schema_keys_to_index, telepact_schema_document_names_to_json, fn_error_regexes)
        except TelepactSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    headers: list[THeaders] = []

    for header_key in header_keys:
        this_index = schema_keys_to_index[header_key]
        this_document_name = schema_keys_to_document_names[header_key]
        telepact_schema_pseudo_json = telepact_schema_document_name_to_pseudo_json[
            this_document_name]
        def_ = cast(dict[str, object],
                    telepact_schema_pseudo_json[this_index])
        try:
            header_type = parse_headers_type(
                [this_index],
                def_,
                header_key,
                ParseContext(
                    this_document_name,
                    telepact_schema_document_name_to_pseudo_json,
                    telepact_schema_document_names_to_json,
                    schema_keys_to_document_names,
                    schema_keys_to_index,
                    parsed_types,
                    fn_error_regexes,
                    parse_failures,
                    failed_types
                )
            )
            headers.append(header_type)
        except TelepactSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, telepact_schema_document_names_to_json)

    try:
        catch_header_collisions(telepact_schema_document_name_to_pseudo_json, header_keys,
                                schema_keys_to_index, schema_keys_to_document_names, telepact_schema_document_names_to_json)
    except TelepactSchemaParseError as e:
        parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, telepact_schema_document_names_to_json)

    request_headers: dict[str, TFieldDeclaration] = {}
    response_headers: dict[str, TFieldDeclaration] = {}

    for header in headers:
        request_headers.update(header.request_headers)
        response_headers.update(header.response_headers)

    final_original_schema = [original_schema[k]
                             for k in sorted(original_schema.keys(), key=lambda k: (not k.startswith("info."), k))]

    return TelepactSchema(
        final_original_schema,
        parsed_types,
        request_headers,
        response_headers
    )
