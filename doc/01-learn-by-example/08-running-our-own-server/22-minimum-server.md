# 22. Minimum server

Now let's build our own Telepact server.

## Install the Python library

```sh
pip install --pre telepact
```

## Create a schema

Create `api/hello.telepact.yaml`:

```yaml
- info.Hello: {}

- fn.hello:
    name: string
  ->:
    - Ok_:
        message: string
```

## Create a tiny HTTP server

Create `server.py`:

```py
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import FunctionRouter, Message, Server, TelepactSchema


schema = TelepactSchema.from_directory('./api')

options = Server.Options()


async def hello(function_name: str, request_message: Message) -> Message:
    name = request_message.body[function_name]['name']
    return Message({}, {'Ok_': {'message': f'Hello, {name}!'}})


function_router = FunctionRouter()
function_router.register_unauthenticated_routes({'fn.hello': hello})
telepact_server = Server(schema, function_router, options)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != '/api/telepact':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', '0'))
        request_bytes = self.rfile.read(content_length)
        response = asyncio.run(telepact_server.process(request_bytes))

        content_type = 'application/octet-stream' if '.bin_' in response.headers else 'application/json'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(response.bytes)

    def log_message(self, format_string: str, *args: object) -> None:
        return


ThreadingHTTPServer(('127.0.0.1', 8002), Handler).serve_forever()
```

## Run it

```sh
python server.py
```

## Call it with `curl`

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.hello": {"name": "Telepact"}}]'
```

```json
[{}, {"Ok_": {"message": "Hello, Telepact!"}}]
```

Even this tiny server already gives clients the standard Telepact experience:
`fn.ping_`, `fn.api_`, validation, select, binary, codegen, and mocking.

Next: [23. Logging](./23-logging.md)
