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

from telepact import Client, Message, Serializer

from server import create_http_server, get_middleware_events, reset_middleware_events
from test_support import post_bytes, run_server, stop_server


async def run_example() -> None:
    server = create_http_server()
    thread = run_server(server)
    reset_middleware_events()
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'

        async def adapter(message: Message, serializer: Serializer) -> Message:
            request_bytes = serializer.serialize(message)
            response_bytes = await asyncio.to_thread(post_bytes, url, request_bytes)
            return serializer.deserialize(response_bytes)

        client = Client(adapter, Client.Options())

        me_response = await client.request(Message({
            '@auth_': {
                'Password': {
                    'username': 'admin',
                    'password': 'swordfish',
                },
            },
        }, {
            'fn.me': {},
        }))
        assert me_response.get_body_target() == 'Ok_'
        assert me_response.get_body_payload() == {
            'userId': 'user-123',
            'role': 'admin',
        }

        admin_report_response = await client.request(Message({
            '@auth_': {
                'Password': {
                    'username': 'viewer',
                    'password': 'opensesame',
                },
            },
        }, {
            'fn.adminReport': {},
        }))
        assert admin_report_response.get_body_target() == 'ErrorUnauthorized_'
        assert admin_report_response.get_body_payload() == {
            'message!': 'admin role required',
        }

        auth_failure_response = await client.request(Message({
            '@auth_': {
                'Password': {
                    'username': 'explode',
                    'password': 'boom',
                },
            },
        }, {
            'fn.me': {},
        }))
        assert auth_failure_response.get_body_target() == 'ErrorUnauthenticated_'
        assert auth_failure_response.get_body_payload() == {
            'message!': 'Valid authentication is required.',
        }

        assert get_middleware_events() == [
            {
                'event': 'middleware.identity',
                'function': 'fn.me',
                'userId': 'user-123',
                'role': 'admin',
            },
            {
                'event': 'middleware.identity',
                'function': 'fn.adminReport',
                'userId': 'user-456',
                'role': 'viewer',
            },
        ]
    finally:
        stop_server(server, thread)


def test_simple_auth_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
