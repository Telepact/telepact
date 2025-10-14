## Telepact

### Installation

```
pip install telepact
```

### Usage

API:

```json
[
    {
        "fn.greet": {
            "subject": "string"
        },
        "->": {
            "Ok_": {
                "message": "string"
            }
        }
    }
]
```

Server:

```py

files = TelepactSchemaFiles('/directory/containing/api/files')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)

async def handler(request_message: 'Message') -> 'Message':
    function_name = request_message.body.keys[0]
    arguments = request_message.body[function_name]

    try:
        # Early in the handler, perform any pre-flight "middleware" operations, such as
        # authentication, tracing, or logging.
        log.info("Function started", {'function': function_name})

        # Dispatch request to appropriate function handling code.
        # (This example uses manual dispatching, but you can also use a more advanced pattern.)
        if function_name == 'fn.greet':
            subject = arguments['subject']
            return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})

        raise Exception('Function not found')
    finally:
        # At the end the handler, perform any post-flight "middleware" operations
        log.info("Function finished", {'function': function_name})


options = Server.Options()
server = Server(schema, handler, options)


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
```

For more concrete usage examples,
[see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/py/telepact_test/test_server.py).
