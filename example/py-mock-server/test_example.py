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

import asyncio

from example import interact_with_mock_server


def test_mock_server_example_runs_end_to_end() -> None:
    response, verification = asyncio.run(interact_with_mock_server())

    assert response.body == {
        'Ok_': {
            'message': 'Hello from the mock server!',
        },
    }
    assert verification.body == {'Ok_': {}}
