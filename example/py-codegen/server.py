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

from telepact import FunctionRouter, Server, TelepactSchema, TypedMessage

from gen.gen_types import TypedServerHandler, greet

schema = TelepactSchema.from_directory('api')
options = Server.Options()


class GreetingHandler(TypedServerHandler):

    async def greet(self, headers: dict[str, object], input: greet.Input) -> TypedMessage[greet.Output]:
        return TypedMessage(
            {},
            greet.Output.from_Ok_(message=f'Hello {input.subject()} from generated code!'),
        )


function_router = FunctionRouter()
function_router.register_unauthenticated_routes(GreetingHandler().function_routes())
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
            content_type = 'application/octet-stream' if '+bin_' in response.headers else 'application/json'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(response.bytes)

        def log_message(self, format: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), RequestHandler)
