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
from contextlib import suppress

import websockets

from telepact import Client, Message, Serializer

from server import create_websocket_server


class PendingWebSocketTransport:
    def __init__(self, websocket: websockets.ClientConnection) -> None:
        self.websocket = websocket
        self.pending: dict[object, asyncio.Future[Message]] = {}
        self.receive_task: asyncio.Task[None] | None = None
        self.receive_order: list[object] = []
        self.send_order: list[object] = []
        self.send_lock = asyncio.Lock()
        self.serializer: Serializer | None = None
        self.next_request_number = 1

    async def adapter(self, message: Message, serializer: Serializer) -> Message:
        if self.receive_task is None:
            self.serializer = serializer
            self.receive_task = asyncio.create_task(self.receive_loop())

        request_headers = dict(message.headers)
        request_id = request_headers.setdefault('@id_', f'call-{self.next_request_number}')
        self.next_request_number += 1

        future = asyncio.get_running_loop().create_future()
        self.pending[request_id] = future
        self.send_order.append(request_id)

        try:
            async with self.send_lock:
                await self.websocket.send(serializer.serialize(Message(request_headers, message.body)))
            return await future
        finally:
            self.pending.pop(request_id, None)

    async def receive_loop(self) -> None:
        assert self.serializer is not None

        try:
            async for response_bytes in self.websocket:
                if isinstance(response_bytes, str):
                    response_bytes = response_bytes.encode('utf-8')

                response_message = self.serializer.deserialize(response_bytes)
                response_id = response_message.headers.get('@id_')
                response_future = self.pending.get(response_id)
                if response_future is None:
                    raise RuntimeError(f'unexpected response id: {response_id!r}')

                self.receive_order.append(response_id)
                if not response_future.done():
                    response_future.set_result(response_message)
        except Exception as exc:
            for response_future in self.pending.values():
                if not response_future.done():
                    response_future.set_exception(exc)

    async def close(self) -> None:
        if self.receive_task is None:
            return
        self.receive_task.cancel()
        with suppress(asyncio.CancelledError):
            await self.receive_task


async def run_example() -> None:
    server = await create_websocket_server()
    try:
        assert server.sockets is not None
        port = server.sockets[0].getsockname()[1]
        async with websockets.connect(f'ws://127.0.0.1:{port}/ws/telepact') as websocket:
            transport = PendingWebSocketTransport(websocket)
            client = Client(transport.adapter, Client.Options())

            slow_response_task = asyncio.create_task(client.request(Message({}, {
                'fn.greet': {'subject': 'slow', 'delayMs': 50},
            })))
            fast_response_task = asyncio.create_task(client.request(Message({}, {
                'fn.greet': {'subject': 'fast', 'delayMs': 0},
            })))

            slow_response, fast_response = await asyncio.gather(slow_response_task, fast_response_task)

            assert transport.send_order == ['call-1', 'call-2']
            assert transport.receive_order == ['call-2', 'call-1']
            assert slow_response.headers['@id_'] == 'call-1'
            assert fast_response.headers['@id_'] == 'call-2'
            assert slow_response.body['Ok_']['message'] == 'Hello slow from WebSocket!'
            assert fast_response.body['Ok_']['message'] == 'Hello fast from WebSocket!'

            await transport.close()
    finally:
        server.close()
        await server.wait_closed()


def test_websocket_request_ids_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
