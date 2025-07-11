# Introduction

Telepact is an API ecosystem for bridging programs across inter-process
communication boundaries.

What makes Telepact different? It brings together 3 previously incompatible
ideas:
1. **JSON Abstractions** - API clients can use their favorite industry standard JSON library to interface with an API server
2. **Hypermedia** - API servers can incorporate API references in responses to create "links" across its API, without HTTP
3. **Binary** - Clients can optionally enable efficient binary serialization while still preserving simple JSON abstractions

For further reading, see [Motivation](./doc/motivation.md).

For explanations of various design decisions, see [the FAQ](./doc/faq.md).

## At a glance

Specify your API:
```sh
$ cat ./api/math.telepact.json
```
```json
[
   {
      "///": " Add two integers, `x` and `y`. ",
      "fn.divide": {
         "x": ["integer"],
         "y": ["integer"]
      },
      "->": [
         {
            "Ok_": {
               "result": ["integer"]
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

def handler(req_msg):
    fn = req_msg.body.keys()[0]
    args = req_msg.body[fn]
    if fn == 'fn.divide':
        x = args['x']
        y = args['y']
        if y == 0:
            return Message({}, {'ErrorCannotDivideByZero': {}})

        result = x / y
        return Message({}, {'Ok_': {'result': result}})
    else:
        raise Error('Unknown function')

options = Server.Options()
options.auth_required = False

schema_files = TelepactSchemaFiles('./api')
api = TelepactSchema.from_file_json_map(schema_files)
server = Server(api, handler, options)

from fastpi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

@app.post('/api/telepact')
async def telepact_handler(request):
    request_bytes = await request.body()
    response_bytes = await server.process(request_bytes)
    return Response(content=response_bytes, media_type='application/octet-stream')
```
```sh
$ uvicorn server:app --port 8000
```

Then tell your clients about your transport, and they can consume your API with minimal tooling:
```
$ cat ./client.js
```
```js
let request = [
    {},
    {
        'fn.divide': {
            'x': 6,
            'y': 3
        }
    }
];
var response = fetch('http://localhost:8000/api/telepact', { method: 'POST' }, JSON.stringify(request));
console.log(`Response: ${await response.json()}`);
```
```sh
$ node ./client.js
Response: [{}, {"Ok_": {"result": 2}}]
```

Or clients can also leverage telepact tooling to:
- Slice responses to reduce response sizes
- Generate code to increase type safety
- Use binary serialization to reduce request/response sizes


# Development

The Telepact project is structed as a monorepo.

- `common` - files commonly used across the Telepact ecosystem
- `bind` - contains lightweight wrapper libraries that use bindings to
   expose a formal Telepact implementation in a language not yet targetted by
   a formal Telepact implementation.
- `lib` - contains all formal library implementations of Telepact in various
   programming languages
- `test` - contains the test framework that enforces the Telepact specification
   on all implementations found in `lib`
- `sdk` - contains various programs that assist developing in the Telepact
   ecosystem
- `tool` - contains various programs that assist the development of the
   Telepact project

# Licensing
Telepact is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for 
the full license text. See [NOTICE](NOTICE) for additional information regarding 
copyright ownership.
