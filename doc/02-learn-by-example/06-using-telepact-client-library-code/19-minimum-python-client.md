# 19. Minimum Python client

Now let's stop hand-writing JSON and let the Telepact Python library help us.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Install what this example needs

```sh
pip install --pre telepact requests
```

## Write a minimum client

```py
import asyncio
import requests

from telepact import Client, Message, Serializer


async def adapter(message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(message)
    response = requests.post('http://localhost:8000/api', data=request_bytes, timeout=5)
    return serializer.deserialize(response.content)


async def main() -> None:
    client = Client(adapter, Client.Options())

    await client.request(Message({}, {'fn.saveVariable': {'name': 'x', 'value': 5}}))
    response = await client.request(Message({}, {'fn.export': {}}))

    blob = response.body['Ok_']['blob']
    print(type(blob).__name__)
    print(len(blob))
    print(blob[:8].hex())


asyncio.run(main())
```

Run it:

```sh
python client.py
```

Example output:

```text
bytes
293
82a9766172696162
```

The important part is that `blob` is already Python `bytes`. We did not manually
JSON-encode the message, and we did not manually Base64-decode the wire value.

Next: [20. Automatic binary negotiation](20-automatic-binary-negotiation.md)
