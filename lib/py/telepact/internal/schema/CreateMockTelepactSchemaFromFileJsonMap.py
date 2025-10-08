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
from ...MockTelepactSchema import MockTelepactSchema


def create_mock_telepact_schema_from_file_json_map(json_documents: dict[str, str]) -> 'MockTelepactSchema':
    from .GetMockTelepactJson import get_mock_telepact_json
    from .CreateTelepactSchemaFromFileJsonMap import create_telepact_schema_from_file_json_map

    final_json_documents = json_documents.copy()
    final_json_documents["mock_"] = get_mock_telepact_json()

    telepact_schema = create_telepact_schema_from_file_json_map(
        final_json_documents)

    return MockTelepactSchema(telepact_schema.original, telepact_schema.parsed, telepact_schema.parsed_request_headers, telepact_schema.parsed_response_headers)
