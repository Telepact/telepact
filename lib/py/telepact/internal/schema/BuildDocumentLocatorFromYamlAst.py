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

import json
from typing import Callable

import yaml


def _serialize_path(path: list[object]) -> str:
    return json.dumps(path, separators=(',', ':'))


def _coordinates_from_mark(mark: yaml.Mark | None) -> dict[str, object]:
    if mark is None:
        return {'row': 1, 'col': 1}
    return {'row': mark.line + 1, 'col': mark.column + 1}


def _build_locations_for_node(
    node: yaml.nodes.Node | None,
    path: list[object],
    locations: dict[str, dict[str, object]],
) -> None:
    if isinstance(node, yaml.nodes.SequenceNode):
        for index, item in enumerate(node.value):
            item_path = path + [index]
            locations[_serialize_path(item_path)] = _coordinates_from_mark(item.start_mark)
            _build_locations_for_node(item, item_path, locations)
        return

    if isinstance(node, yaml.nodes.MappingNode):
        for key_node, value_node in node.value:
            key = getattr(key_node, 'value', None)
            if not isinstance(key, str):
                continue

            key_path = path + [key]
            locations[_serialize_path(key_path)] = _coordinates_from_mark(key_node.start_mark)
            _build_locations_for_node(value_node, key_path, locations)


def _validate_no_duplicate_keys(node: yaml.nodes.Node | None) -> None:
    if isinstance(node, yaml.nodes.SequenceNode):
        for item in node.value:
            _validate_no_duplicate_keys(item)
        return

    if isinstance(node, yaml.nodes.MappingNode):
        seen_keys: set[str] = set()
        for key_node, value_node in node.value:
            key = str(getattr(key_node, 'value', ''))
            if key in seen_keys:
                raise ValueError('Duplicate YAML key')
            seen_keys.add(key)
            _validate_no_duplicate_keys(value_node)


def create_document_locator_from_yaml_text(text: str) -> Callable[[list[object]], dict[str, object]]:
    node = yaml.compose(text)
    if node is None:
        raise ValueError('YAML document cannot be empty')

    _validate_no_duplicate_keys(node)
    locations: dict[str, dict[str, object]] = {
        _serialize_path([]): _coordinates_from_mark(node.start_mark),
    }
    _build_locations_for_node(node, [], locations)

    return lambda path: locations.get(_serialize_path(path), {'row': 1, 'col': 1})
