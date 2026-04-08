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

from telepact import Client, Message, Serializer

from server import build_telepact_server


async def assert_binary_negotiation() -> None:
    server = build_telepact_server()
    requests: asyncio.Queue[bytes | None] = asyncio.Queue()
    responses: asyncio.Queue[bytes] = asyncio.Queue()
    saw_binary_response = False

    async def server_loop() -> None:
        nonlocal saw_binary_response
        while True:
            request_bytes = await requests.get()
            if request_bytes is None:
                return

            response = await server.process(request_bytes)
            if '@bin_' in response.headers:
                saw_binary_response = True
            await responses.put(response.bytes)

    async def adapter(message: Message, serializer: Serializer) -> Message:
        await requests.put(serializer.serialize(message))
        response_bytes = await responses.get()
        return serializer.deserialize(response_bytes)

    client_options = Client.Options()
    client_options.use_binary = True
    client_options.always_send_json = False
    client = Client(adapter, client_options)

    server_task = asyncio.create_task(server_loop())
    try:
        for _ in range(2):
            response = await client.request(Message({}, {'fn.getNumbers': {'limit': 3}}))
            assert response.body['Ok_']['values'] == [1, 2, 3]
    finally:
        await requests.put(None)
        await server_task

    assert saw_binary_response


def test_binary_example_negotiates_binary_after_the_initial_request() -> None:
    asyncio.run(assert_binary_negotiation())
