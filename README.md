# Introduction

jAPI (pronounced "Jay-Pee-Eye") or **J**SON **A**pplication **P**rogramming
**I**nterface is an API expressed purely with JSON. Familiar API concepts, such
as function calls and return values, are represented entirely with JSON
payloads. Consequently, A jAPI can satisfy API needs across not only HTTP, but
any inter-process communication boundary.

Wherever JSON can go, a jAPI can be served 🚀

HTTP client example (with `cURL`):

```bash
$ export URL=http://example.com/api/v1
$ curl -X '["function.add", {"Authorization": "Bearer <token>"}, {"x": 1, "y": 2}]' $URL
["function.add", {}, {"result": 3}]
$ curl -X '["function.sub", {"Authorization": "Bearer <token>"}, {"x": 1, "y": 2}]' $URL
["function.sub", {}, {"result": -1}]
```

Websocket client example (with `python`):

```python
# japi_ws.py

import sys
import json
from websocket import create_connection
ws = create_connection('ws://example.com/api/v1')
ws.send(sys.argv[1])
print('{}'.format((ws.recv())))
```

```
$ python japi_ws.py '["function.add", {"Authorization": "Bearer <token>"}, {"x": 1, "y": 2}]'
["function.add", {}, {"result": 3}]
$ python japi_ws.py '["function.sub", {"Authorization": "Bearer <token>"}, {"x": 1, "y": 2}]'
["function.add", {}, {"result": -1}]
```

# Motivation

| Capability                                                   | RESTful | gRPC | jAPI |
| ------------------------------------------------------------ | ------- | ---- | ---- |
| Serve API with a transport other than HTTP                   | ❌      | ❌   | ✅   |
| Define API decoupled from transport concepts                 | ❌      | ✅   | ✅   |
| Consume API without any required libraries                   | ✅      | ❌   | ✅   |
| Consume API with type-safe generated code                    | 🤔      | ✅   | ✅   |
| Serve API with type-safe generated code                      | 🤔      | ✅   | ✅   |
| Use JSON as a developer-friendly data serialization protocol | ✅      | ❌   | ✅   |
| Use compact and efficient data serialization protocols       | 🤔      | ✅   | ✅   |
| Return variable payloads according to consumer needs         | 🤔      | ❌   | ✅   |

🤔 = Possible, but not consistently observed in practice

## Why not RESTful APIs?

RESTful APIs are inherently HTTP APIs and cannot be used with any other
networking transport (e.g. sockets, messaging). And unfortunately, HTTP concepts
unnecessarily become intertwined with the API itself, which often leads to
design inefficiencies where API design is stalled to answer HTTP-specific
questions, such as determining the right url structure, the right query
parameters, the right HTTP method, the right HTTP status code, and many others.

## Why not gRPC?

gRPC APIs are also inherently tied to the HTTP transport, and similarly to
RESTful APIs, cannot be used with other networking transports. Although in
contrast to RESTful APIs, gRPC does properly decouple HTTP concepts from its API
definitions, simplifying the API design story. gRPC also uses a more efficient
serialization protocol than the typical RESTful API, but this protocol is used
exclusively and is largely inaccessible to API consumers. So in practice,
consumers must fully adopt gRPC tooling client-side, which places an integration
burden on consumers who are not familiar with gRPC. Consumers will be required
to use a supported language of gRPC, and will likely need to build up tooling to
generate their own client code if their API provider doesn't offer a readily
accessible client library.

## Why jAPI?

### jAPI is portable

You can offer your API anywhere a JSON payload can be supplied. That could be an
HTTP URL, a websocket, a topic for a message broker like Kafka, the browser
event loop, or even simple inter-process communication interfaces like UNIX
named pipes.

### jAPI is flexible

Server-side jAPI tooling allows you to offer a range of consumer experiences,
from simple to advanced, all computed at runtime without any server-side
configuration. At its simplest variation, consumers are not required to use any
jAPI libraries; they can simply use the native JSON and networking capabilities
of their preferred programming language and/or industry standard library and
craft JSON payloads according to your API specification.

But from there, consumers can also opt-in to several features including:

- jAPI client libraries that help facilitate crafting of JSON payloads
- Type safety with client-side generated code
- Swapping out of JSON for an efficient binary protocol to improve API speed
- "Slicing" data returned from an API, where the consumer indicates data fields
  that should be omitted by the API provider so as to further optimize speed
  through reduced serialization.

Again, all of these features are opt-in client-side, provided to the consumer
through server-side jAPI libraries, which makes these features automatic without
any effort by the server-side implementation.

## More FAQ

### Why force servers to perform output validation? Wouldn't it be better to give clients malformed data so that they are at least empowered to adapt?

jAPI automatically performs validation of function outputs (as well as errors)
against the API description, and there is no setting for servers to turn off
this behavior.

This design decision is intentional. It helps maintain the high standard of type
safety in the jAPI ecosystem by preventing API providers from indulging in the
plausible deniability of claiming malformed data is just an inconvenience and
are instead forced to deal with a hard failure through bug reports. Hard
failures also help draw attention to type safety deficits early in the
development phase.

Clients who are uniquely vulnerable to hard server failures and who find it
advantageous to receive the malformed data anyway and adapt on-the-fly are able
to turn off this output validation by submitting their requests with the
`{"_unsafe":true}` header.

## Glossary

- **Body** - A structured JSON object containing the primary data payload of the
  jAPI Message.

- **Client** - An entity consuming a jAPI.

- **Input** - The body of a `function.*`-targeted jAPI Message sent from the
  Client.

- **Headers** - An unstructured JSON object consisting of metadata about a jAPI
  Message.

- **Message** - The JSON payload sent over the IPC boundary, comprised of a
  single JSON array with 3 elements: (1) the target, (2) headers, (3) body.

- **Output** - The body of a `function.*`-targeted jAPI Message sent from the
  Server.

- **Server** - An entity providing an implementation of a jAPI and adhering to
  the jAPI specification.

- **Target** - A reference to a top-level definition in the jAPI description of
  the jAPI server.

# Navigation

- [Specification](SPECIFICATION.md)
