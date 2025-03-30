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
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure


def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: list['SchemaParseFailure'], telepact_document_name_to_json: dict[str, str]) -> list[dict[str, object]]:
    from ...internal.schema.GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json
    pseudo_json_list = []
    for f in schema_parse_failures:
        location = get_path_document_coordinates_pseudo_json(
            f.path, telepact_document_name_to_json[f.document_name])
        pseudo_json: dict[str, object] = {}
        pseudo_json["document"] = f.document_name
        pseudo_json["location"] = location
        pseudo_json["path"] = f.path
        pseudo_json["reason"] = {f.reason: f.data}
        pseudo_json_list.append(dict(pseudo_json))
    return pseudo_json_list
