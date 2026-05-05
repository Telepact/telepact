# 20. Automatic binary negotiation

Earlier we negotiated binary by hand. Now let's let the Python client do it.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Install what this example needs

```sh
pip install --pre telepact requests
```

## Write a binary-enabled client

```py
import asyncio
import requests

from telepact import Client, Message, Serializer


async def main() -> None:
    calls = []

    async def adapter(message: Message, serializer: Serializer) -> Message:
        request_bytes = serializer.serialize(message)
        response = requests.post('http://localhost:8000/api', data=request_bytes, timeout=5)
        decoded = serializer.deserialize(response.content)
        calls.append({
            'request_headers': dict(message.headers),
            'request_len': len(request_bytes),
            'response_headers': dict(decoded.headers),
            'response_len': len(response.content),
        })
        return decoded

    options = Client.Options()
    options.use_binary = True
    options.always_send_json = False

    client = Client(adapter, options)

    for _ in range(2):
        await client.request(Message({}, {'fn.getVariables': {}}))

    for index, call in enumerate(calls, start=1):
        print(f'call {index}: {call}')


asyncio.run(main())
```

Run it:

```sh
python client.py
```

Example output:

```text
call 1: {'request_headers': {'+time_': 5000, '+bin_': []}, 'request_len': 56, 'response_headers': {'+enc_': {...}, '+bin_': [900069279]}, 'response_len': 480}
call 2: {'request_headers': {'+time_': 5000, '+bin_': [900069279]}, 'request_len': 27, 'response_headers': {'+bin_': [900069279]}, 'response_len': 25}
```

Three nice things happened for us:

1. the client automatically started the binary handshake
2. it cached the negotiated checksum and reused it
3. it sent `+time_` for us so the server can understand the client's timeout

This is the normal way to use binary with Telepact. If the schema changes, the
runtime client can re-negotiate instead of forcing us through a codegen ABI
pipeline.

Next: [21. Code generation](../07-code-generation/21-code-generation.md)
