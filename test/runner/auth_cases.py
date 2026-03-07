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
from pathlib import Path


def _schema_key(definition: dict[str, object]) -> str:
    for key in definition:
        if key not in {'///', '->', '_errors'}:
            return key
    raise AssertionError(f'No schema key found in {definition}')


def _load_sorted_schema(*relative_paths: str) -> list[dict[str, object]]:
    root = Path(__file__).resolve().parents[2]
    definitions: list[dict[str, object]] = []
    for relative_path in relative_paths:
        with (root / relative_path).open() as stream:
            definitions.extend(json.load(stream))

    return sorted(
        definitions,
        key=lambda definition: (not _schema_key(definition).startswith('info.'), _schema_key(definition)),
    )


_AUTH_FULL_SCHEMA = _load_sorted_schema(
    'test/runner/schema/auth/auth.telepact.json',
    'common/auth.telepact.json',
    'common/internal.telepact.json',
)


cases = {
    'auth': [
        [[{'@ok_': {}}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
        [[{'@result': {'ErrorUnauthenticated_': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthenticated_': {'message!': 'a'}}]],
        [[{'@result': {'ErrorUnauthorized_': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthorized_': {'message!': 'a'}}]],
        [[{}, {'fn.api_': {}}], [{}, {'Ok_': {'api': [{'info.AuthExample': {}}, {'///': ' A standard error. ', 'errors.Auth_': [{'///': ' The credentials in the `_auth` header were missing or invalid. ', 'ErrorUnauthenticated_': {'message!': 'string'}}, {'///': ' The credentials in the `_auth` header were insufficient to run the function. ', 'ErrorUnauthorized_': {'message!': 'string'}}]}, {'fn.test': {}, '->': [{'Ok_': {}}]}, {'///': [' The `@auth_` header is the conventional location for sending credentials to     ', ' the server for the purpose of authentication and authorization.                 '], 'headers.Auth_': {'@auth_': 'struct.Auth_'}, '->': {}}, {'struct.Auth_': {'token': 'string'}}]}}]],
        [[{}, {'fn.api_': {'includeInternal!': True}}], [{}, {'Ok_': {'api': _AUTH_FULL_SCHEMA}}]],
   ]
}
