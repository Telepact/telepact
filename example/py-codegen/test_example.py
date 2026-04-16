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

from __future__ import annotations

import asyncio
import threading
import urllib.request

from telepact import Client, Message, Serializer

from gen.gen_types import TypedClient, greet
from server import create_http_server


def run_server(server) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def stop_server(server, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def post_bytes(url: str, request_bytes: bytes) -> bytes:
    request = urllib.request.Request(
        url,
        data=request_bytes,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(request) as response:
        return response.read()


async def run_example() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'

        async def adapter(message: Message, serializer: Serializer) -> Message:
            request_bytes = serializer.serialize(message)
            response_bytes = await asyncio.to_thread(post_bytes, url, request_bytes)
            return serializer.deserialize(response_bytes)

        client = TypedClient(Client(adapter, Client.Options()))
        response = await client.greet(
            {'x-request-id': 'req-1'},
            greet.Input.from_(subject='Telepact'),
        )

        ok = response.body.get_tagged_value()
        assert ok.tag == 'Ok_'
        assert ok.value.message() == 'Hello Telepact from generated code!'
        assert response.headers == {'x-request-id': 'req-1'}
    finally:
        stop_server(server, thread)


def test_codegen_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
