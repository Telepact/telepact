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
import warnings
from pathlib import Path

from telepact_cli import resources


class _FakeResource:
    def __init__(self, text: str):
        self._text = text

    def read_text(self) -> str:
        return self._text


class _FakeTraversable:
    def __init__(self, text: str):
        self._text = text

    def joinpath(self, name: str) -> _FakeResource:
        assert name == 'calculator.telepact.yaml'
        return _FakeResource(self._text)


def test_calculator_schema_load_avoids_deprecation_warning(monkeypatch) -> None:
    schema_text = Path('telepact_cli/calculator.telepact.yaml').read_text()
    monkeypatch.setattr(resources.pkg_resources, 'files', lambda package: _FakeTraversable(schema_text))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always', DeprecationWarning)
        telepact_json = resources.load_calculator_telepact_json()

    schema = json.loads(telepact_json)
    assert any('fn.add' in entry for entry in schema)
    assert [warning for warning in caught if issubclass(warning.category, DeprecationWarning)] == []
