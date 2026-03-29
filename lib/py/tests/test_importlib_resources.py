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
