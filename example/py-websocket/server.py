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

import websockets

from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


async def greet(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    subject = argument['subject']
    return Message({}, {
        'Ok_': {
            'message': f'Hello {subject} from WebSocket!',
        },
    })


telepact_server = Server(schema, {'fn.greet': greet}, options)


async def telepact_websocket(websocket: websockets.ServerConnection) -> None:
    request = getattr(websocket, 'request', None)
    if request is not None and getattr(request, 'path', '/ws/telepact') != '/ws/telepact':
        await websocket.close(code=1008, reason='unexpected path')
        return

    async for request_bytes in websocket:
        is_text = isinstance(request_bytes, str)
        if is_text:
            request_bytes = request_bytes.encode('utf-8')

        response = await telepact_server.process(request_bytes)
        if is_text:
            await websocket.send(response.bytes.decode('utf-8'))
        else:
            await websocket.send(response.bytes)


async def create_websocket_server(host: str = '127.0.0.1', port: int = 0):
    return await websockets.serve(telepact_websocket, host, port)
