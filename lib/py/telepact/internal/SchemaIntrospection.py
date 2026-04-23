#!/usr/bin/env python3

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
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ..TelepactSchema import TelepactSchema


def get_index_entries(
    telepact_schema: 'TelepactSchema',
    include_internal: bool,
) -> list[dict[str, object]]:
    definitions = telepact_schema.full if include_internal else telepact_schema.original

    entries: list[dict[str, object]] = []
    for definition in definitions:
        definition_map = cast(dict[str, object], definition)
        schema_key = _get_schema_key(definition_map)
        if not schema_key.startswith('fn.') or schema_key.endswith('.->'):
            continue
        if not include_internal and schema_key.endswith('_'):
            continue

        entry: dict[str, object] = {'name': schema_key}
        if '///' in definition_map:
            entry['comment!'] = definition_map['///']
        entries.append(entry)

    return entries


def get_definition_closure(
    telepact_schema: 'TelepactSchema',
    name: str,
    include_internal: bool,
) -> list[object]:
    definitions_by_name = {
        _get_schema_key(cast(dict[str, object], definition)): cast(dict[str, object], definition)
        for definition in telepact_schema.full
    }
    root_definition = _get_root_definition(telepact_schema, name, include_internal)
    if root_definition is None:
        return []

    visited: set[str] = set()

    def visit(schema_key: str) -> None:
        if schema_key in visited:
            return

        definition = definitions_by_name.get(schema_key)
        if definition is None:
            return

        visited.add(schema_key)

        for referenced_schema_key in _get_definition_references(definition, definitions_by_name):
            visit(referenced_schema_key)

    visit(_get_schema_key(root_definition))

    return [
        definition
        for definition in telepact_schema.full
        if _get_schema_key(cast(dict[str, object], definition)) in visited
    ]


def _get_root_definition(
    telepact_schema: 'TelepactSchema',
    name: str,
    include_internal: bool,
) -> dict[str, object] | None:
    allowed_definitions = telepact_schema.full if include_internal else telepact_schema.original

    if not include_internal and name.endswith('_'):
        return None

    for definition in allowed_definitions:
        definition_map = cast(dict[str, object], definition)
        if _get_schema_key(definition_map) == name:
            return definition_map

    return None


def _get_definition_references(
    definition: dict[str, object],
    definitions_by_name: dict[str, dict[str, object]],
) -> set[str]:
    references: set[str] = set()
    schema_key = _get_schema_key(definition)

    for key, value in definition.items():
        if key == '///':
            continue

        if key == '_errors':
            if isinstance(value, str):
                for candidate in definitions_by_name.keys():
                    if re.fullmatch(value, candidate):
                        references.add(candidate)
            continue

        if key == schema_key:
            references.update(_get_type_expression_references(value, definitions_by_name))
            continue

        if key == '->':
            references.update(_get_type_expression_references(value, definitions_by_name))

    return references


def _get_type_expression_references(
    type_expression: object,
    definitions_by_name: dict[str, dict[str, object]],
) -> set[str]:
    references: set[str] = set()

    if isinstance(type_expression, str):
        schema_key = type_expression[:-1] if type_expression.endswith('?') else type_expression
        if schema_key in definitions_by_name:
            references.add(schema_key)
        return references

    if isinstance(type_expression, list):
        if _is_union_definition(type_expression):
            for tag_definition in type_expression:
                tag_map = cast(dict[str, object], tag_definition)
                for key, value in tag_map.items():
                    if key == '///':
                        continue
                    references.update(_get_type_expression_references(value, definitions_by_name))
        elif type_expression:
            references.update(_get_type_expression_references(type_expression[0], definitions_by_name))
        return references

    if isinstance(type_expression, dict):
        if set(type_expression.keys()) == {'string'}:
            references.update(_get_type_expression_references(type_expression['string'], definitions_by_name))
            return references

        for value in type_expression.values():
            references.update(_get_type_expression_references(value, definitions_by_name))

    return references


def _is_union_definition(type_expression: list[object]) -> bool:
    if not type_expression:
        return False

    for entry in type_expression:
        if not isinstance(entry, dict):
            return False

        non_comment_keys = [key for key in entry.keys() if key != '///']
        if len(non_comment_keys) != 1:
            return False

        if not isinstance(entry[non_comment_keys[0]], dict):
            return False

    return True


def _get_schema_key(definition: dict[str, object]) -> str:
    for key in definition.keys():
        if key not in {'///', '->', '_errors'}:
            return key

    raise ValueError(f'Schema entry has no schema key: {definition}')
