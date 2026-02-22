# Example

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

