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
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


async def handler(request_message: Message) -> Message:
    if request_message.get_body_target() != 'fn.issueLink':
        raise RuntimeError(f'Unknown function: {request_message.get_body_target()}')

    title = request_message.get_body_payload()['title']
    return Message({}, {
        'Ok_': {
            'todo': {
                'title': title,
            },
            'next!': {
                'fn.followUp': {
                    'id': 'follow-up-1',
                },
            },
        },
    })


telepact_server = Server(schema, handler, options)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != '/healthz':
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'ok')

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

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    server = ThreadingHTTPServer(('127.0.0.1', port), RequestHandler)
    print(f'py-links listening on http://127.0.0.1:{port}')
    server.serve_forever()
