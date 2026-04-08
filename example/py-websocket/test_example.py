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

import websockets

from server import build_telepact_server


async def run_example() -> None:
    telepact_server = build_telepact_server()

    async def handle_connection(connection: websockets.ServerConnection) -> None:
        async for request_bytes in connection:
            if isinstance(request_bytes, str):
                request_bytes = request_bytes.encode('utf-8')
            response = await telepact_server.process(request_bytes)
            await connection.send(response.bytes)

    websocket_server = await websockets.serve(handle_connection, '127.0.0.1', 0)
    try:
        port = websocket_server.sockets[0].getsockname()[1]
        async with websockets.connect(f'ws://127.0.0.1:{port}/ws/telepact') as websocket:
            await websocket.send('[{}, {"fn.greet": {"subject": "Telepact"}}]')
            response = await websocket.recv()
            if isinstance(response, bytes):
                response = response.decode('utf-8')
            assert 'Hello Telepact from WebSocket!' in response
    finally:
        websocket_server.close()
        await websocket_server.wait_closed()


def test_websocket_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
