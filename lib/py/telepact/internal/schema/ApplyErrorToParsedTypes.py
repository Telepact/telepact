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

import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..types.VError import VError
    from ..types.VStruct import VStruct
    from ..types.VType import VType
    from ..types.VUnion import VUnion


def apply_error_to_parsed_types(error: 'VError', parsed_types: dict[str, 'VType'], schema_keys_to_document_names: dict[str, str], schema_keys_to_index: dict[str, int], document_names_to_json: dict[str, str]) -> None:
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json
    from ..types.VFn import VFn

    parse_failures = []

    error_key = error.name
    error_index = schema_keys_to_index[error_key]
    document_name = schema_keys_to_document_names[error_key]

    for parsed_type_name, parsed_type in parsed_types.items():
        if not isinstance(parsed_type, VFn):
            continue
        f = parsed_type

        fn_name = f.name

        regex = re.compile(f.errors_regex)

        fn_result = f.result
        fn_result_tags = fn_result.tags
        error_errors = error.errors
        error_tags = error_errors.tags

        matcher = regex.match(error_key)
        if not matcher:
            continue

        for error_tag_name, error_tag in error_tags.items():
            new_key = error_tag_name

            if new_key in fn_result_tags:
                other_path_index = schema_keys_to_index[fn_name]
                error_tag_index = error.errors.tag_indices[new_key]
                other_document_name = schema_keys_to_document_names[fn_name]
                fn_error_tag_index = f.result.tag_indices[new_key]
                other_final_path = [other_path_index,
                                    "->", fn_error_tag_index, new_key]
                other_document_json = document_names_to_json[other_document_name]
                other_location_pseudo_json = get_path_document_coordinates_pseudo_json(
                    other_final_path, other_document_json)
                parse_failures.append(SchemaParseFailure(
                    document_name,
                    [error_index, error_key,
                     error_tag_index, new_key],
                    "PathCollision",
                    {"document": other_document_name,
                     "path": other_final_path,
                        "location": other_location_pseudo_json}
                ))
            fn_result_tags[new_key] = error_tag

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, document_names_to_json)
