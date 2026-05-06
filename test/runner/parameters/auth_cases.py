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

from pathlib import Path

from parameters.schema_loader import load_schema_definitions


def _schema_key(definition: dict[str, object]) -> str:
    for key in definition:
        if key not in {'///', '->', '_errors'} and not key.startswith('$'):
            return key
    raise AssertionError(f'No schema key found in {definition}')


def _load_sorted_schema(*relative_paths: str) -> list[dict[str, object]]:
    root = Path(__file__).resolve().parents[3]
    definitions: list[dict[str, object]] = []
    for relative_path in relative_paths:
        definitions.extend(load_schema_definitions(root / relative_path))

    return sorted(
        definitions,
        key=lambda definition: (not _schema_key(definition).startswith('info.'), _schema_key(definition)),
    )


_AUTH_FULL_SCHEMA = _load_sorted_schema(
    'test/runner/schema/auth/auth.telepact.json',
    'common/auth.telepact.yaml',
    'common/internal.telepact.yaml',
)

_AUTH_PUBLIC_SCHEMA = _load_sorted_schema(
    'test/runner/schema/auth/auth.telepact.json',
    'common/auth.telepact.yaml',
)


cases = {
    'auth': [
        [[{}, {'fn.test': {}}], [{}, {'ErrorUnauthenticated_': {'message!': 'Valid authentication is required.'}}]],
        [[{'+auth_': {'Token': {'token': 'ok'}}}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
        [[{'+auth_': {'Token': {'token': 'unauthenticated'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthenticated_': {'message!': 'Valid authentication is required.'}}]],
        [[{'+auth_': {'Token': {'token': 'unauthorized'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthorized_': {'message!': 'a'}}]],
        [[{}, {'fn.api_': {}}], [{}, {'Ok_': {'api': _AUTH_PUBLIC_SCHEMA}}]],
        [[{}, {'fn.api_': {'includeInternal!': True}}], [{}, {'Ok_': {'api': _AUTH_FULL_SCHEMA}}]],
        [[{'+auth_': {'Token': {'token': 'unauthenticated'}}}, {'fn.api_': {}}], [{}, {'Ok_': {'api': _AUTH_PUBLIC_SCHEMA}}]],
        [[{'+auth_': {'Token': {'token': 'unauthorized'}}}, {'fn.api_': {'includeInternal!': True}}], [{}, {'Ok_': {'api': _AUTH_FULL_SCHEMA}}]],
   ]
}
