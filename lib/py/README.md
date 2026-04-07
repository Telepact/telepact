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

async def greet(_headers: dict[str, object], arguments: dict[str, object]) -> 'Message':
    subject = arguments['subject']
    return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})


async def middleware(request_message: 'Message', function_router) -> 'Message':
    function_name = request_message.get_body_target()
    try:
        log.info("Function started", {'function': function_name})
        return await function_router.route(request_message)
    finally:
        log.info("Function finished", {'function': function_name})


options = Server.Options()
# Set this to False when your schema does not define union.Auth_.
options.auth_required = False
options.middleware = middleware
server = Server(schema, {'fn.greet': greet}, options)


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
