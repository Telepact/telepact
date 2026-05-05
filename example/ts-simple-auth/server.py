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

import argparse
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles

VALID_CREDENTIALS = {
    ('demo-user', 'demo-pass'): {
        '@userId': 'user-123',
        '@role': 'reader',
    },
    ('demo-admin', 'demo-pass'): {
        '@userId': 'admin-456',
        '@role': 'admin',
    },
}

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


async def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    credentials = auth.get('Credentials') if isinstance(auth, dict) else None
    username = credentials.get('username') if isinstance(credentials, dict) else None
    password = credentials.get('password') if isinstance(credentials, dict) else None
    if isinstance(username, str) and isinstance(password, str):
        return VALID_CREDENTIALS.get((username, password), {})
    return {}


options.on_auth = on_auth


async def me(function_name: str, request_message: Message) -> Message:
    _ = function_name
    return Message({}, {
        'Ok_': {
            'userId': str(request_message.headers['@userId']),
            'role': str(request_message.headers['@role']),
        },
    })


async def admin_report(function_name: str, request_message: Message) -> Message:
    _ = function_name
    if request_message.headers.get('@role') != 'admin':
        return Message({}, {
            'ErrorUnauthorized_': {
                'message!': 'admin role required',
            },
        })

    return Message({}, {
        'Ok_': {
            'summary': f"secret report for {request_message.headers['@userId']}",
        },
    })


async def middleware(request_message: Message, function_router: FunctionRouter) -> Message:
    if request_message.get_body_target() == 'fn.api_':
        return await function_router.route(request_message)

    if request_message.headers.get('@userId') is None or request_message.headers.get('@role') is None:
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'missing or invalid credentials',
            },
        })

    return await function_router.route(request_message)


options.middleware = middleware


function_router = FunctionRouter({
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
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()

    server = create_http_server(args.host, args.port)
    print(f'listening {server.server_address[1]}', flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
