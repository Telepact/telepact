#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from __future__ import annotations

import websockets

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles

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


function_router = FunctionRouter({'fn.greet': greet})
telepact_server = Server(schema, function_router, options)


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
