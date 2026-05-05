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
    return next(key for key in definition.keys() if key not in {'///', '->', '_errors'} and not key.startswith('@'))


def _load_sorted_schema(*relative_paths: str) -> list[dict[str, object]]:
    root = Path(__file__).resolve().parents[3]
    definitions: list[dict[str, object]] = []

    for relative_path in relative_paths:
        definitions.extend(load_schema_definitions(root / relative_path))

    return sorted(definitions, key=lambda definition: (not _schema_key(definition).startswith('info.'), _schema_key(definition)))


_MOCKGEN_FULL_SCHEMA = _load_sorted_schema(
    'test/runner/schema/mockgen/mockgen.telepact.json',
    'common/internal.telepact.yaml',
    'common/mock-internal.telepact.yaml',
)


cases = {
    'simple': [
        [[{}, {'fn.api_': {'includeInternal!': True}}], [{}, {'Ok_': {'api': _MOCKGEN_FULL_SCHEMA}}]],
        [[{}, {'fn.setRandomSeed_': {'seed': 4}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.clearStubs_': {}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.clearCalls_': {}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.test': {}}], [{}, {'ErrorNoMatchingStub_': {}}]],
        [[{}, {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {}}}}}], [{}, {'Ok_': {}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.example': {}, '->': {'Ok_': {}}}}}, 'data': {'field1': 'epsilon', 'field2': 424973015}, 'genericData': {'Two': {'field2A': 'mu', 'field2B': True}}, 'select': {'->': {'Ok_': ['createStub', 'data']}}, 'verify': {'fn.verify_': {'call': {'fn.example': {'arg1': 'alpha'}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.example': {'arg1': 'psi'}, '->': {'Ok_': {'result': []}}}}}, 'data': {'field1': True, 'field2': 652711277}, 'genericData': {'Two': {'field2A': 'upsilon', 'field2B': False}}, 'select': {'struct.Data': ['field1', 'field2'], 'union.GenericData': {'One': [], 'Two': ['field2A']}}, 'verify': {'fn.verify_': {'call': {'fn.example': {'arg1': 'omega'}}}}}}]],
        [[{}, {'fn.test': {}}], [{}, {'Ok_': {'createStub': {'fn.createStub_': {'stub': {'fn.test': {}, '->': {'Ok_': {'data': {'field1': 'kappa'}, 'select': {'->': {'Ok_': ['data', 'genericData', 'verify']}, 'struct.Data': ['field1', 'field2']}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}}}}, 'data': {'field1': 1154191355, 'field2': 738514090}, 'genericData': {'One': {'field1A': 'beta', 'field1B': 1273685929}}, 'select': {'struct.Data': ['field2']}, 'verify': {'fn.verify_': {'call': {'fn.test': {}}}}}}]],
    ],
}
