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

    if function_name == 'fn.greet':
        subject = arguments['subject']
        return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})

    raise Exception('Function not found')

options = Server.Options()
server = Server(schema, handler, options)

# Wire up request/response bytes from your transport of choice
response_bytes = server.process(request_bytes)
```

Client:

```py
async def adapter(m: Message, s: Serializer) -> Message:
    request_bytes = s.serialize(m)

    # Wire up request/response bytes to your transport of choice

    return s.deserialize(response_bytes)

options = Client.Options()
client = Client(adapter, options)
```

For more concrete usage examples,
[see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/py/telepact_test/test_server.py).
