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
import urllib.request

from telepact import Client, Message, Serializer

from server import create_http_server
from test_support import run_server, stop_server


async def send_request(url: str, request_bytes: bytes) -> bytes:
    def send() -> bytes:
        request = urllib.request.Request(
            url,
            data=request_bytes,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(request) as response:
            return response.read()

    return await asyncio.to_thread(send)


async def run_example(url: str) -> None:
    async def adapter(message: Message, serializer: Serializer) -> Message:
        response_bytes = await send_request(url, serializer.serialize(message))
        return serializer.deserialize(response_bytes)

    client = Client(adapter, Client.Options())

    unauthenticated = await client.request(Message({}, {
        'fn.me': {},
    }))
    assert unauthenticated.body['ErrorUnauthenticated_']['message!'] == 'missing or invalid credentials'

    reader = await client.request(Message({
        '@auth_': {
            'Credentials': {
                'username': 'demo-user',
                'password': 'demo-pass',
            },
        },
    }, {
        'fn.me': {},
    }))
    assert reader.body['Ok_']['userId'] == 'user-123'
    assert reader.body['Ok_']['role'] == 'reader'

    unauthorized = await client.request(Message({
        '@auth_': {
            'Credentials': {
                'username': 'demo-user',
                'password': 'demo-pass',
            },
        },
    }, {
        'fn.adminReport': {},
    }))
    assert unauthorized.body['ErrorUnauthorized_']['message!'] == 'admin role required'

    admin = await client.request(Message({
        '@auth_': {
            'Credentials': {
                'username': 'demo-admin',
                'password': 'demo-pass',
            },
        },
    }, {
        'fn.adminReport': {},
    }))
    assert admin.body['Ok_']['summary'] == 'secret report for admin-456'


def test_simple_auth_example_runs_end_to_end() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'
        asyncio.run(run_example(url))
    finally:
        stop_server(server, thread)
