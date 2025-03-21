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

from typing import Dict, List, Set, cast


def catch_header_collisions(
    telepact_schema_name_to_pseudo_json: Dict[str, List[object]],
    header_keys: Set[str],
    keys_to_index: Dict[str, int],
    schema_keys_to_document_names: Dict[str, str],
    document_names_to_json: Dict[str, str],
) -> None:
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure
    from ...internal.schema.GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json

    parse_failures = []

    header_keys_list = list(header_keys)
    header_keys_list.sort(key=lambda k: (
        schema_keys_to_document_names[k], keys_to_index[k]))

    for i in range(len(header_keys_list)):
        for j in range(i + 1, len(header_keys_list)):
            def_key = header_keys_list[i]
            other_def_key = header_keys_list[j]

            index = keys_to_index[def_key]
            other_index = keys_to_index[other_def_key]

            document_name = schema_keys_to_document_names[def_key]
            other_document_name = schema_keys_to_document_names[other_def_key]

            telepact_schema_pseudo_json = telepact_schema_name_to_pseudo_json[document_name]
            other_telepact_schema_pseudo_json = telepact_schema_name_to_pseudo_json[
                other_document_name]

            def_ = cast(dict[str, object], telepact_schema_pseudo_json[index])
            other_def = cast(dict[str, object],
                             other_telepact_schema_pseudo_json[other_index])

            header_def = cast(dict[str, object], def_[def_key])
            other_header_def = cast(
                dict[str, object], other_def[other_def_key])

            header_collisions = [
                k for k in header_def if k in other_header_def]
            for header_collision in header_collisions:
                this_path = [index, def_key, header_collision]
                this_document_json = document_names_to_json[document_name]
                this_location = get_path_document_coordinates_pseudo_json(
                    this_path, this_document_json)
                parse_failures.append(
                    SchemaParseFailure(
                        other_document_name,
                        [other_index, other_def_key, header_collision],
                        'PathCollision',
                        {'document': document_name, 'path': this_path,
                            'location': this_location},
                    )
                )

            res_header_def = cast(dict[str, object], def_['->'])
            other_res_header_def = cast(dict[str, object], other_def['->'])

            res_header_collisions = [
                k for k in res_header_def if k in other_res_header_def]
            for res_header_collision in res_header_collisions:
                this_path = [index, '->', res_header_collision]
                this_document_json = document_names_to_json[document_name]
                this_location = get_path_document_coordinates_pseudo_json(
                    this_path, this_document_json)
                parse_failures.append(
                    SchemaParseFailure(
                        other_document_name,
                        [other_index, '->', res_header_collision],
                        'PathCollision',
                        {'document': document_name, 'path': this_path,
                            'location': this_location},
                    )
                )

    if parse_failures:
        raise TelepactSchemaParseError(parse_failures, document_names_to_json)
