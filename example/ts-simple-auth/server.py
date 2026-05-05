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

ADMIN_CREDENTIALS = {'username': 'admin', 'password': 'swordfish'}
VIEWER_CREDENTIALS = {'username': 'viewer', 'password': 'opensesame'}
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
        return {}

    if password == EXPLODING_CREDENTIALS:
        raise RuntimeError('auth backend unavailable')

    if password == ADMIN_CREDENTIALS:
        return {'@userId': 'user-123', '@role': 'admin'}

    if password == VIEWER_CREDENTIALS:
        return {'@userId': 'user-456', '@role': 'viewer'}

    return {}


options.on_auth = on_auth


def _log_identity(request_message: Message) -> None:
    event = {
        'event': 'middleware.identity',
        'function': request_message.get_body_target(),
        'userId': request_message.headers.get('@userId'),
        'role': request_message.headers.get('@role'),
    }
    MIDDLEWARE_EVENTS.append(event)
    print(json.dumps(event, sort_keys=True), flush=True)


async def middleware(request_message: Message, function_router: FunctionRouter) -> Message:
    _log_identity(request_message)

    user_id = request_message.headers.get('@userId')
    role = request_message.headers.get('@role')
    if not isinstance(user_id, str) or not isinstance(role, str):
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'missing or invalid credentials',
            },
        })

    try:
        return await function_router.route(request_message)
    except Unauthorized as error:
        return Message({}, {
            'ErrorUnauthorized_': {
                'message!': str(error),
            },
        })


options.middleware = middleware


async def me(_function_name: str, request_message: Message) -> Message:
    return Message({}, {
        'Ok_': {
            'userId': request_message.headers['@userId'],
            'role': request_message.headers['@role'],
        },
    })


async def admin_report(_function_name: str, request_message: Message) -> Message:
    if request_message.headers.get('@role') != 'admin':
        raise Unauthorized('admin role required')

    return Message({}, {
        'Ok_': {
            'message': 'sensitive admin report',
        },
    })


function_router = FunctionRouter()
function_router.register_authenticated_routes({
    'fn.me': me,
    'fn.adminReport': admin_report,
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
