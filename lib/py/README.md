## Telepact Library for Python

### Installation

```
pip install --pre telepact
```

Published PyPI releases are currently prereleases. To pin a specific release,
use the exact version from [doc/versions.md](https://github.com/Telepact/telepact/blob/main/doc/versions.md).

### Usage

API:

```yaml
- fn.greet:
    subject: string
  ->:
    Ok_:
      message: string
```

Server:

```py
from telepact import Client, Message, Serializer, Server, TelepactSchema, TelepactSchemaFiles

files = TelepactSchemaFiles('/directory/containing/api/files')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)

# The schema directory may contain multiple *.telepact.yaml and
# *.telepact.json files. Subdirectories are rejected.

async def middleware(request_message: 'Message', function_router: telepact.FunctionRouter) -> 'Message':
    function_name = request_message.get_body_target()
    arguments = request_message.get_body_payload()

    try:
        # Early in the handler, perform any pre-flight "middleware" operations, such as
        # authentication, tracing, or logging.
        log.info("Function started", {'function': function_name})

        # Dispatch request to appropriate function handling code.
        # (This example uses manual dispatching, but you can also use a more advanced pattern.)
        if function_name == 'fn.greet':
            subject = arguments['subject']
            return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})

        return await function_router.route(request_message)
    finally:
        # At the end the handler, perform any post-flight "middleware" operations
        log.info("Function finished", {'function': function_name})


options = Server.Options()
options.middleware = middleware
# Set this to False when your schema does not define union.Auth_.
options.auth_required = False
function_router = telepact.FunctionRouter()
server = Server(schema, function_router, options)


# Wire up request/response bytes from your transport of choice
async def transport_handler(request_bytes: bytes) -> bytes:
    response = await server.process(request_bytes)
    return response.bytes

transport.receive(transport_handler)
```

Client:

```py
async def adapter(m: Message, s: Serializer) -> Message:
    request_bytes = s.serialize(m)

    # Wire up request/response bytes to your transport of choice
    response_bytes = await transport.send(request_bytes)

    return s.deserialize(response_bytes)

options = Client.Options()
client = Client(adapter, options)

# Inside your async application code:
request = Message({}, {'fn.greet': {'subject': 'World'}})
response = await client.request(request)
if response.get_body_target() == 'Ok_':
    ok_payload = response.get_body_payload()
    print(ok_payload['message'])
else:
    raise RuntimeError(f"Unexpected response: {response.body}")
```

For more concrete usage examples,
[see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/py/telepact_test/test_server.py).
