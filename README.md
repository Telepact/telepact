# Introduction

Telepact is an API ecosystem for bridging programs across inter-process
communication boundaries.

What makes Telepact different? It takes the differentiating features of the
industry's most popular API technologies, and combines them together through 3
key innovations:

1. **JSON as a Query Language** - API calls and `SELECT`-style queries are all
   achieved with JSON abstractions, giving first-class status to clients
   wielding only a JSON library
2. **Binary without code generation** - Binary protocols are established through
   runtime handshakes, rather than build-time code generation, offering binary
   efficiency to clients that want to avoid code generation toolchains
3. **Hypermedia without HTTP** - API calls can return functions with pre-filled
   arguments, approximating a link that can be followed, all achieved with pure
   JSON abstractions

For further reading, see [Motivation](./doc/motivation.md).

For explanations of various design decisions, see [the FAQ](./doc/faq.md).

For how-to guides, see the [API Schema Guide](./doc/schema-guide.md), as well as
the library and SDK docs:

-   [Library: Typescript](./lib/ts/README.md)
-   [Library: Python](./lib/py/README.md)
-   [Library: Java](./lib/java/README.md)

-   [SDK: CLI](./sdk/cli/README.md)
-   [SDK: Developer Console](./sdk/console/README.md)
-   [SDK: Prettier Plugin](./sdk/prettier/README.md)

# At a glance

Specify your API:

```sh
$ cat ./api/math.telepact.json
```

```json
[
    {
        "///": " Divide two integers, `x` and `y`. ",
        "fn.divide": {
            "x": "integer",
            "y": "integer"
        },
        "->": [
            {
                "Ok_": {
                    "result": "number"
                }
            },
            {
                "ErrorCannotDivideByZero": {}
            }
        ]
    }
]
```

Serve it with one of the Telepact libraries over a transport of your choice:

```sh
$ cat ./server.py
```

```py
from telepact import TelepactSchemaFiles, TelepactSchema, Server, Message
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

async def handler(req_msg):
    fn = req_msg.get_body_target()
    args = req_msg.body[fn]
    if fn == 'fn.divide':
        x = args['x']
        y = args['y']
        if y == 0:
            return Message({}, {'ErrorCannotDivideByZero': {}})

        result = x / y
        return Message({}, {'Ok_': {'result': result}})
    else:
        raise Exception('Unknown function')

options = Server.Options()
options.auth_required = False

schema_files = TelepactSchemaFiles('./api')
api = TelepactSchema.from_file_json_map(schema_files.filenames_to_json)
server = Server(api, handler, options)

async def http_handler(request):
    request_bytes = await request.body()
    response = await server.process(request_bytes)
    response_bytes = response.bytes
    media_type = 'application/octet-stream' if 'bin_' in response.headers else 'application/json'
    return Response(content=response_bytes, media_type=media_type)

routes = [
    Route('/api/telepact', endpoint=http_handler, methods=['POST']),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(routes=routes, middleware=middleware)

uvicorn.run(app, host='0.0.0.0', port=8000)
```

```sh
$ poetry add uvicorn starlette telepact
$ poetry run python ./server.py
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

Or clients can also leverage telepact tooling to:

-   Select less fields to reduce response sizes
-   Generate code to increase type safety
-   Use binary serialization to reduce request/response sizes

# Licensing

Telepact is licensed under the Apache License, Version 2.0. See
[LICENSE](LICENSE) for the full license text. See [NOTICE](NOTICE) for
additional information regarding copyright ownership.
