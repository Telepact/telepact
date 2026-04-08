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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles

VALID_SESSION = 'demo-session'

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False
options.on_auth = lambda headers: {'@userId': 'user-123'} if headers.get('@auth_', {}).get('sessionToken') == VALID_SESSION else {}


async def me(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    user_id = request_message.headers.get('@userId')
    if user_id != 'user-123':
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'missing or invalid session cookie',
            },
        })

    return Message({}, {
        'Ok_': {
            'userId': user_id,
        },
    })


telepact_server = Server(schema, {'fn.me': me}, options)


def read_cookie(cookie_header: str | None, name: str) -> str | None:
    if cookie_header is None:
        return None

    for entry in cookie_header.split(';'):
        key, _, value = entry.strip().partition('=')
        if key == name and value:
            return value

    return None


def create_http_server(host: str = '127.0.0.1', port: int = 0) -> ThreadingHTTPServer:
    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != '/api/telepact':
                self.send_response(404)
                self.end_headers()
                return

            content_length = int(self.headers.get('Content-Length', '0'))
            request_bytes = self.rfile.read(content_length)
            session_token = read_cookie(self.headers.get('Cookie'), 'session')

            def update_headers(headers: dict[str, object]) -> None:
                if session_token:
                    headers['@auth_'] = {'sessionToken': session_token}

            response = asyncio.run(telepact_server.process(request_bytes, update_headers))
            content_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(response.bytes)

        def log_message(self, format: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), RequestHandler)
