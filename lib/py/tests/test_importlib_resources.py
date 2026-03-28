import warnings

from telepact.internal.schema.GetAuthTelepactJson import get_auth_telepact_json
from telepact.internal.schema.GetInternalTelepactJson import get_internal_telepact_json
from telepact.internal.schema.GetMockTelepactJson import get_mock_telepact_json


def test_schema_resources_load_without_deprecation_warnings() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always', DeprecationWarning)
        payloads = [
            get_internal_telepact_json(),
            get_auth_telepact_json(),
            get_mock_telepact_json(),
        ]

    assert all(payload.strip() for payload in payloads)
    assert [warning for warning in caught if issubclass(warning.category, DeprecationWarning)] == []
