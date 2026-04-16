# 21. Code generation

Telepact also lets us generate bindings straight from a running service or from
a checked-in schema.

## When code generation is worth it

Code generation is the right upgrade when:

- a supported language already has a Telepact runtime library
- the schema is shared widely enough to treat bindings as a real project asset
- raw `Message` construction is starting to feel repetitive

For TypeScript in particular, generated bindings turn stringly-typed function
names and hand-built payloads into a client API that follows the schema.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Generate TypeScript bindings

The generated TypeScript source still depends on the normal `telepact` npm
package at runtime:

```sh
npm install telepact
mkdir -p ./src/gen
telepact codegen --schema-http-url http://localhost:8000/api --lang ts --out ./src/gen
```

That gives us local source files we can import from our application. The CLI is
just the generator; the runtime package for Node is still `telepact`.

## Manual client vs generated TypeScript client

Without code generation, we stay close to raw Telepact messages:

```ts
import { Client, Message } from "telepact";

const response = await client.request(
    new Message({}, { "fn.add": { x: 2, y: 3 } }),
);
```

That is still valid and often a good fit for simple integrations.

With generated bindings, we keep the same runtime client but call a typed API:

```ts
import { TypedClient, add } from "./gen/genTypes.js";

const typedClient = new TypedClient(client);
const response = await typedClient.add({}, add.Input.from({ x: 2, y: 3 }));
const tagged = response.body.getTaggedValue();
if (tagged.tag === "Ok_") {
    console.log(tagged.value.result());
}
```

The value of codegen is not a different transport or protocol. The value is a
better application-facing API on top of the existing Telepact runtime.

## Generate Python bindings too

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
2. generate bindings from that schema
3. use them with the Telepact runtime library for your language

In practice, many teams first `fetch` a schema, then `mock` and `codegen` from
that checked-in copy so the whole workflow stays reproducible in CI and local
development.

Next: [22. Minimum server](../08-running-our-own-server/22-minimum-server.md)
