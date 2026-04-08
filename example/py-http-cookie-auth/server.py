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
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles

VALID_SESSION = 'demo-session'

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    if isinstance(auth, dict) and auth.get('sessionToken') == VALID_SESSION:
        return {'@userId': 'user-123'}
    return {}


options.on_auth = on_auth


async def me(function_name: str, request_message: Message) -> Message:
    if request_message.headers.get('@userId') != 'user-123':
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'missing or invalid session cookie',
            },
        })

    return Message({}, {
        'Ok_': {
            'userId': 'user-123',
        },
    })


telepact_server = Server(schema, {'fn.me': me}, options)


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


def create_http_server(host: str = '127.0.0.1', port: int = 0) -> ThreadingHTTPServer:
    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != '/api/telepact':
                self.send_response(404)
                self.end_headers()
                return

            content_length = int(self.headers.get('Content-Length', '0'))
            request_bytes = self.rfile.read(content_length)
            session_token = read_session_cookie(self.headers.get('Cookie'))

            def update_headers(headers: dict[str, object]) -> None:
                if session_token is not None:
                    headers['@auth_'] = {'sessionToken': session_token}

            response = asyncio.run(telepact_server.process(request_bytes, update_headers))
            content_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(response.bytes)

        def log_message(self, format_string: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), RequestHandler)
