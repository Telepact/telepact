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

import os
from pathlib import Path
from typing import Dict

from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ...TelepactSchemaParseError import TelepactSchemaParseError
from .DocumentLocators import SchemaDocumentMap
from .ParseTelepactYaml import parse_telepact_yaml


def get_schema_file_map(directory: str) -> Dict[str, str]:
    final_json_documents: SchemaDocumentMap = SchemaDocumentMap()

    schema_parse_failures = []

    try:
        paths = [str(p) for p in Path(directory).rglob('*')]

        for path in paths:
            relative_path = os.path.relpath(path, directory)

            # Check if directory
            # If it is, add a SchemaParseFailure for DirectoryDisallowed
            if os.path.isdir(path):
                schema_parse_failures.append(SchemaParseFailure(relative_path, [], "DirectoryDisallowed", {}))
                final_json_documents[relative_path] = "[]"
                continue    

            with open(path, 'r') as file:
                content = file.read()
            if relative_path.endswith('.telepact.json'):
                final_json_documents[relative_path] = content
            elif relative_path.endswith('.telepact.yaml'):
                try:
                    canonical_json, locator = parse_telepact_yaml(content)
                    final_json_documents[relative_path] = canonical_json
                    if locator is not None:
                        final_json_documents.document_locators[relative_path] = locator
                except ValueError:
                    final_json_documents[relative_path] = '[]'
                    schema_parse_failures.append(SchemaParseFailure(relative_path, [], "JsonInvalid", {}))
            else:
                final_json_documents[relative_path] = content
                schema_parse_failures.append(SchemaParseFailure(relative_path, [], "FileNamePatternInvalid", {"expected": "*.telepact.json|*.telepact.yaml"}))
    except IOError as e:
        raise RuntimeError(e)

    if schema_parse_failures:
        raise TelepactSchemaParseError(schema_parse_failures, final_json_documents)

    return final_json_documents
