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

from typing import Callable


DocumentLocator = Callable[[list[object]], dict[str, object]]


class SchemaDocumentMap(dict[str, str]):
    document_locators: dict[str, DocumentLocator]

    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)
        self.document_locators = {}


def ensure_schema_document_map(document_names_to_json: dict[str, str]) -> SchemaDocumentMap:
    if isinstance(document_names_to_json, SchemaDocumentMap):
        return document_names_to_json

    mapped = SchemaDocumentMap(document_names_to_json)
    locators = getattr(document_names_to_json, 'document_locators', None)
    if isinstance(locators, dict):
        mapped.document_locators = dict(locators)
    return mapped


def set_document_locators(document_names_to_json: dict[str, str], document_locators: dict[str, DocumentLocator]) -> None:
    mapped = ensure_schema_document_map(document_names_to_json)
    mapped.document_locators = dict(document_locators)


def get_document_locators(document_names_to_json: dict[str, str]) -> dict[str, DocumentLocator]:
    mapped = ensure_schema_document_map(document_names_to_json)
    return mapped.document_locators


def copy_document_locators(src: dict[str, str], dst: dict[str, str]) -> SchemaDocumentMap:
    mapped = ensure_schema_document_map(dst)
    mapped.document_locators = dict(getattr(src, 'document_locators', {}))
    return mapped


def resolve_document_coordinates(path: list[object], document_name: str, document_names_to_json: dict[str, str]) -> dict[str, object]:
    from .GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json

    locator = getattr(document_names_to_json, 'document_locators', {}).get(document_name)
    if locator is not None:
        return locator(path)

    return get_path_document_coordinates_pseudo_json(path, document_names_to_json.get(document_name, '[]'))
