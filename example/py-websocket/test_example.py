#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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
