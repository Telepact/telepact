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

from ...internal.schema.SchemaParseFailure import SchemaParseFailure


def get_type_unexpected_parse_failure(document_name: str, path: list[object], value: object, expected_type: str) -> list[SchemaParseFailure]:
    from ...internal.types.GetType import get_type

    actual_type = get_type(value)
    data: dict[str, object] = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        SchemaParseFailure(document_name, path, "TypeUnexpected", data)
    ]
