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

import websockets

from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


async def greet(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    await asyncio.sleep(argument['delayMs'] / 1000)
    subject = argument['subject']
    return Message({}, {
        'Ok_': {
            'message': f'Hello {subject} from WebSocket!',
        },
    })


telepact_server = Server(schema, {'fn.greet': greet}, options)


async def telepact_websocket(websocket: websockets.ServerConnection) -> None:
    request = getattr(websocket, 'request', None)
    path = None if request is None else getattr(request, 'path', None)
    if path is not None and path != '/ws/telepact':
        await websocket.close(code=1008, reason='unexpected path')
        return

    send_lock = asyncio.Lock()
    pending_tasks: set[asyncio.Task[None]] = set()

    async def handle_request(request_bytes: bytes | str) -> None:
        is_text = isinstance(request_bytes, str)
        if is_text:
            request_bytes = request_bytes.encode('utf-8')

        response = await telepact_server.process(request_bytes)
        payload = response.bytes.decode('utf-8') if is_text else response.bytes

        async with send_lock:
            await websocket.send(payload)

    try:
        async for request_bytes in websocket:
            task = asyncio.create_task(handle_request(request_bytes))
            pending_tasks.add(task)
            task.add_done_callback(pending_tasks.discard)
    finally:
        if pending_tasks:
            await asyncio.gather(*pending_tasks, return_exceptions=True)


async def create_websocket_server(host: str = '127.0.0.1', port: int = 0):
    return await websockets.serve(telepact_websocket, host, port)
