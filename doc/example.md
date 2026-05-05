# Quickstart

The minimum Telepact API ecosystem is established by a server defining a
Telepact API schema, and serving it using one of the Telepact libraries.

Specify your API:

```sh
$ cat ./api/math.telepact.yaml
```

```yaml
- ///: Divide two integers, `x` and `y`.
  fn.divide:
    x: "integer"
    y: "integer"
  ->:
    - Ok_:
        result: "number"
    - ErrorCannotDivideByZero: {}
```

Serve it with one of the Telepact libraries over a transport of your choice.
For more concrete HTTP and WebSocket patterns, see the
[Transport Guide](./03-build-clients-and-servers/01-transports.md).

```sh
$ cat ./server.py
```

```py
from telepact import FunctionRouter, TelepactSchema, Server, Message
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
import uvicorn

async def divide(function_name, request_message):
    arguments = request_message.body[function_name]
    x = arguments['x']
    y = arguments['y']
    if y == 0:
        return Message({}, {'ErrorCannotDivideByZero': {}})

    result = x / y
    return Message({}, {'Ok_': {'result': result}})

options = Server.Options()

api = TelepactSchema.from_directory('./api')
function_router = FunctionRouter({'fn.divide': divide})
server = Server(api, function_router, options)

async def http_handler(request):
    request_bytes = await request.body()
    response = await server.process(request_bytes)
    response_bytes = response.bytes
    media_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'
    return Response(content=response_bytes, media_type=media_type)

routes = [
    Route('/api/telepact', endpoint=http_handler, methods=['POST']),
]

app = Starlette(routes=routes)

uvicorn.run(app, host='0.0.0.0', port=8000)
```

```sh
$ uv add uvicorn starlette telepact
$ uv run python ./server.py
```

Then tell your clients about your transport, and they can consume your API with
minimal tooling:

```
$ cat ./client.js
```

```js
let header = {};
let body = {
    "fn.divide": {
        x: 6,
        y: 3,
    }
};
let request = [header, body];
let response = await fetch(
    "http://localhost:8000/api/telepact",
    {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
    },
);
console.log(`Response: ${JSON.stringify(await response.json())}`);
```

```sh
$ node ./client.js
Response: [{},{"Ok_":{"result":2}}]
```

## Next steps

- [Transport Guide](./03-build-clients-and-servers/01-transports.md) for browser + Node HTTP and WebSocket patterns
- [Client Paths](./03-build-clients-and-servers/02-client-paths.md) for choosing between plain JSON, runtime libraries, and generated code
- [Auth Guide](./03-build-clients-and-servers/05-auth.md) when the API needs caller identity
- [Tooling Workflow](./03-build-clients-and-servers/04-tooling-workflow.md) for `fetch`, `compare`, `mock`, and `codegen`
- [Operating Boundary Guide](./04-operate/01-production-guide.md) for Telepact-specific compatibility and observability boundaries
- [Demos](../example/README.md) for runnable end-to-end examples
- [Docs home](./index.md) for the rest of the documentation map
