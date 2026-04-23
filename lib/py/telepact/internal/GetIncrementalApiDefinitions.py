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

from .GetApiDefinitionsWithExamples import _get_schema_key

if TYPE_CHECKING:
    from ..TelepactSchema import TelepactSchema


_ENTRYPOINT_PREFIXES = ('info.', 'headers.', 'errors.', 'fn.')
_CUSTOM_TYPE_PREFIXES = ('fn.', 'struct.', 'union.', 'headers.', 'errors.', 'info.', '_ext.')


def get_api_entrypoint_definitions(
    telepact_schema: 'TelepactSchema',
    include_internal: bool,
) -> list[object]:
    definitions = telepact_schema.full if include_internal else telepact_schema.original
    return [
        definition
        for definition in definitions
        if _get_schema_key(cast(dict[str, object], definition)).startswith(_ENTRYPOINT_PREFIXES)
    ]


def get_api_definitions_by_schema_key(
    telepact_schema: 'TelepactSchema',
    schema_key: str,
    include_internal: bool,
) -> list[object] | None:
    definitions = telepact_schema.full if include_internal else telepact_schema.original
    definitions_by_key = {
        _get_schema_key(cast(dict[str, object], definition)): cast(dict[str, object], definition)
        for definition in definitions
    }
    if schema_key not in definitions_by_key:
        return None

    included_schema_keys: set[str] = set()
    pending_schema_keys: list[str] = [schema_key]

    while pending_schema_keys:
        current_schema_key = pending_schema_keys.pop()
        if current_schema_key in included_schema_keys:
            continue
        current_definition = definitions_by_key.get(current_schema_key)
        if current_definition is None:
            continue

        included_schema_keys.add(current_schema_key)
        pending_schema_keys.extend([
            referenced_schema_key
            for referenced_schema_key in _get_referenced_schema_keys(current_definition, definitions_by_key)
            if referenced_schema_key not in included_schema_keys
        ])

    return [
        definition
        for definition in definitions
        if _get_schema_key(cast(dict[str, object], definition)) in included_schema_keys
    ]


def _get_referenced_schema_keys(
    definition: dict[str, object],
    definitions_by_key: dict[str, dict[str, object]],
) -> list[str]:
    references: set[str] = set()

    for key, value in definition.items():
        if key in {'///', '_errors'}:
            continue
        _collect_referenced_schema_keys(value, definitions_by_key, references)

    errors_regex = definition.get('_errors')
    if isinstance(errors_regex, str):
        regex = re.compile(errors_regex)
        references.update([
            schema_key
            for schema_key in definitions_by_key.keys()
            if regex.match(schema_key)
        ])

    return sorted(references)


def _collect_referenced_schema_keys(
    value: object,
    definitions_by_key: dict[str, dict[str, object]],
    references: set[str],
) -> None:
    if isinstance(value, str):
        schema_key = value[:-1] if value.endswith('?') else value
        if schema_key.startswith(_CUSTOM_TYPE_PREFIXES) and schema_key in definitions_by_key:
            references.add(schema_key)
        return

    if isinstance(value, list):
        for entry in value:
            _collect_referenced_schema_keys(entry, definitions_by_key, references)
        return

    if isinstance(value, dict):
        for key, entry in value.items():
            if key == '///':
                continue
            _collect_referenced_schema_keys(entry, definitions_by_key, references)
