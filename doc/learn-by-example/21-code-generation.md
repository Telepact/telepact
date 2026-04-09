# 21. Code generation

Telepact also lets us generate bindings straight from a running service.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Generate Python bindings

```sh
mkdir -p ./gen
telepact codegen --schema-http-url http://localhost:8000/api --lang py --out ./gen
```

That creates Python code from the live schema. No server-managed artifact bundle
is needed; we simply point the generator at the service we want to integrate
with.

## Generated code still uses the Telepact Python library

Install the runtime:

```sh
pip install --pre telepact requests
```

## Use the generated bindings

```py
import asyncio
import requests

from telepact import Client, Message, Serializer
from gen.gen_types import TypedClient, add


async def adapter(message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(message)
    response = requests.post('http://localhost:8000/api', data=request_bytes, timeout=5)
    return serializer.deserialize(response.content)


async def main() -> None:
    raw_client = Client(adapter, Client.Options())
    client = TypedClient(raw_client)

    response = await client.add({}, add.Input.from_(x=2, y=3))
    print(response.body.pseudo_json)


asyncio.run(main())
```

Example output:

```text
{'Ok_': {'result': 5}}
```

So codegen is very lightweight:

1. point at a Telepact server
2. generate bindings
3. use them with the Telepact runtime library

Next: [22. Minimum server](./22-minimum-server.md)
