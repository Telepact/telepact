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

import argparse
import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import FunctionRouter, Message, Server, TelepactSchema

LEAD_BAKER_CREDENTIALS = {'username': 'lead-baker', 'password': 'opensesame'}
CASHIER_CREDENTIALS = {'username': 'cashier', 'password': 'knockknock'}
EXPLODING_CREDENTIALS = {'username': 'explode', 'password': 'boom'}

MIDDLEWARE_EVENTS: list[dict[str, object | None]] = []
schema = TelepactSchema.from_directory('api')
options = Server.Options()


class Unauthorized(Exception):
    pass


async def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    password = auth.get('Password') if isinstance(auth, dict) else None
    if not isinstance(password, dict):
        raise ValueError('missing or invalid bakery credentials')

    if password == EXPLODING_CREDENTIALS:
        raise RuntimeError('bakery auth backend unavailable')

    if password == LEAD_BAKER_CREDENTIALS:
        return {'@employeeId': 'baker-001', '@station': 'oven'}

    if password == CASHIER_CREDENTIALS:
        return {'@employeeId': 'cashier-002', '@station': 'counter'}

    raise ValueError('missing or invalid bakery credentials')


options.on_auth = on_auth


def _log_identity(request_message: Message) -> None:
    event = {
        'event': 'middleware.identity',
        'function': request_message.get_body_target(),
        'employeeId': request_message.headers.get('@employeeId'),
        'station': request_message.headers.get('@station'),
    }
    MIDDLEWARE_EVENTS.append(event)
    print(json.dumps(event, sort_keys=True), flush=True)


async def middleware(request_message: Message, function_router: FunctionRouter) -> Message:
    _log_identity(request_message)

    try:
        return await function_router.route(request_message)
    except Unauthorized as error:
        return Message({}, {
            'ErrorUnauthorized_': {
                'message!': str(error),
            },
        })


options.middleware = middleware


async def my_shift(_function_name: str, request_message: Message) -> Message:
    pastry = 'sesame loaf' if request_message.headers['@station'] == 'oven' else 'almond croissant'
    return Message({}, {
        'Ok_': {
            'employeeId': request_message.headers['@employeeId'],
            'station': request_message.headers['@station'],
            'pastry': pastry,
        },
    })


async def approve_special(_function_name: str, request_message: Message) -> Message:
    if request_message.headers.get('@station') != 'oven':
        raise Unauthorized('oven station required to approve the special')

    return Message({}, {
        'Ok_': {
            'message': 'special approved: cardamom morning bun',
        },
    })


function_router = FunctionRouter()
function_router.register_authenticated_routes({
    'fn.myShift': my_shift,
    'fn.approveSpecial': approve_special,
})
telepact_server = Server(schema, function_router, options)


def create_http_server(host: str = '127.0.0.1', port: int = 0) -> ThreadingHTTPServer:
    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != '/api/telepact':
                self.send_response(404)
                self.end_headers()
                return

            content_length = int(self.headers.get('Content-Length', '0'))
            request_bytes = self.rfile.read(content_length)
            response = asyncio.run(telepact_server.process(request_bytes))
            content_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(response.bytes)

        def log_message(self, format_string: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), RequestHandler)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8002)
    args = parser.parse_args()

    server = create_http_server(args.host, args.port)
    print(f'READY {server.server_address[1]}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
