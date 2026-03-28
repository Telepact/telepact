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
