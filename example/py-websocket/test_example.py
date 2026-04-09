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
import json

import websockets

from server import create_websocket_server


async def run_example() -> None:
    server = await create_websocket_server()
    try:
        assert server.sockets is not None
        port = server.sockets[0].getsockname()[1]
        async with websockets.connect(f'ws://127.0.0.1:{port}/ws/telepact') as websocket:
            await websocket.send(json.dumps([{}, {'fn.greet': {'subject': 'Telepact'}}]))
            response = await websocket.recv()
            assert 'Hello Telepact from WebSocket!' in response
    finally:
        server.close()
        await server.wait_closed()


def test_websocket_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
