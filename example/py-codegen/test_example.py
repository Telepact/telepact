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

from gen.gen_types import TypedClient, add
from server import build_telepact_server


async def run_example() -> None:
    telepact_server = build_telepact_server()

    async def adapter(message: Message, serializer: Serializer) -> Message:
        request_bytes = serializer.serialize(message)
        response = await telepact_server.process(request_bytes)
        return serializer.deserialize(response.bytes)

    raw_client = Client(adapter, Client.Options())
    client = TypedClient(raw_client)

    response = await client.add({}, add.Input.from_(x=2, y=3))
    assert response.body.pseudo_json == {'Ok_': {'result': 5}}


def test_codegen_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
