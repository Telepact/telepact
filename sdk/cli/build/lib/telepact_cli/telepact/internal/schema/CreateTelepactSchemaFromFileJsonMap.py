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
import json
import re

if TYPE_CHECKING:
    from ...TelepactSchema import TelepactSchema


def create_telepact_schema_from_file_json_map(json_documents: dict[str, str]) -> 'TelepactSchema':
    from .ParseTelepactSchema import parse_telepact_schema
    from .GetInternalTelepactJson import get_internal_telepact_json
    from .GetAuthTelepactJson import get_auth_telepact_json
    from .DocumentLocators import copy_document_locators

    final_json_documents = copy_document_locators(json_documents, dict(json_documents))
    internal_json = get_internal_telepact_json()
    if not _has_bundled_definitions(json_documents, "internal_", internal_json):
        final_json_documents["internal_"] = internal_json

    # Determine if we need to add the auth schema
    auth_json = get_auth_telepact_json()
    for json in json_documents.values():
        regex = re.compile(r'"union\.Auth_"\s*:')
        matcher = regex.search(json)
        if matcher:
            if not _has_bundled_definitions(json_documents, "auth_", auth_json):
                final_json_documents["auth_"] = auth_json
            break

    return parse_telepact_schema(final_json_documents)


def _has_bundled_definitions(json_documents: dict[str, str], bundled_document_name: str, bundled_json: str) -> bool:
    bundled_keys = _collect_schema_keys({bundled_document_name: bundled_json})
    if bundled_keys is None:
        return False

    provided_keys = _collect_schema_keys(json_documents)
    if provided_keys is None:
        return False

    return bundled_keys.issubset(provided_keys)


def _collect_schema_keys(json_documents: dict[str, str]) -> set[str] | None:
    from .FindSchemaKey import find_schema_key

    schema_keys: set[str] = set()

    for document_name, document_json in json_documents.items():
        try:
            pseudo_json = json.loads(document_json)
        except json.JSONDecodeError:
            return None

        if not isinstance(pseudo_json, list):
            return None

        for index, definition in enumerate(pseudo_json):
            if not isinstance(definition, dict):
                continue

            try:
                schema_keys.add(find_schema_key(document_name, definition, index, json_documents))
            except Exception:
                return None

    return schema_keys
