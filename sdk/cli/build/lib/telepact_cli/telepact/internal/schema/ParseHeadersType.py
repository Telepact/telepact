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

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ..types.THeaders import THeaders


def parse_headers_type(path: list[object], headers_definition_as_parsed_json: dict[str, object], schema_key: str, ctx: 'ParseContext') -> 'THeaders':
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from ..types.TFieldDeclaration import TFieldDeclaration
    from ...internal.schema.ParseStructFields import parse_struct_fields
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure
    from ..types.THeaders import THeaders

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
            request_fields = parse_struct_fields(
                this_path, request_headers_def, True, ctx)

            # All headers are optional
            for field in request_fields:
                request_fields[field].optional = True

            request_headers.update(request_fields)
        except TelepactSchemaParseError as e:
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
            response_fields = parse_struct_fields(
                response_path, response_headers_def, True, ctx)

            # All headers are optional
            for field in response_fields:
                response_fields[field].optional = True

            response_headers.update(response_fields)
        except TelepactSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)
        except Exception as e:
            raise e

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, ctx.telepact_schema_document_names_to_json)

    return THeaders(schema_key, request_headers, response_headers)
