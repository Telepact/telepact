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

from telepact import Message

from server import build_mock_server, create_client


async def run_example() -> None:
    mock_server = build_mock_server()
    client = create_client(mock_server)

    response = await client.request(Message(
        {'@id_': 'mock-call-1'},
        {'fn.lookupGreeting': {'locale': 'en-US'}},
    ))

    assert response.headers['@id_'] == 'mock-call-1'
    greeting = response.body['Ok_']['greeting']
    assert isinstance(greeting['message'], str)
    assert isinstance(greeting['excited'], bool)


def test_mock_server_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
