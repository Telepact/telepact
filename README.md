# Introduction

jAPI (pronounced "Jay-Pee-Eye") stands for **J**SON **A**pplications
**P**rogrammer **I**nterface, and it is just that: an API expressed purely with
JSON. Programmers define their APIs with JSON, and interact with the API
strictly with JSON payloads that represent familiar programming concepts like
functions, arguments, and return values.

|                                                              | RESTful | gRPC | jAPI |
| ------------------------------------------------------------ | ------- | ---- | ---- |
| Serve API with a transport other than HTTP                   | ❌      | ❌   | ✅   |
| Define API decoupled from transport concepts                 | ❌      | ✅   | ✅   |
| Consume API without any required libraries                   | ✅      | ❌   | ✅   |
| Use JSON as a developer-friendly data serialization protocol | ✅      | ❌   | ✅   |
| Use compact and efficient data serialization protocols       | 🤔      | ✅   | ✅   |
| Consume API with type-safe generated code                    | 🤔      | ✅   | ✅   |
| Return variable payloads according to consumer needs         | 🤔      | ❌   | ✅   |

🤔 = Possible, but not consistently observed in the industry

## Why not RESTful APIs?

RESTful APIs are inherently HTTP APIs, and cannot be used with any other
networking transport (e.g. sockets, messaging). And unfortunately, HTTP concepts
unnecessarily become intertwined with the API itself, which often leads to
design inefficiencies where API design is stalled to answer HTTP-specific
questions, such as designing the url (and whether it should have interpolated
variables), supplying input via query parameter vs POST/PUT/PATCH body, or
choosing the appropriate HTTP method or status code.

## Why not gRPC?

gRPC APIs are also inherently tied to the HTTP transport, and similarly to
RESTful APIs, cannot be used with other networking transports. Although in
contrast to RESTful APIs, gRPC does properly decouple HTTP concepts from its API
definitions, simplifying the API design story. gRPC also uses a more efficient
serialization protocol than the typical RESTful API, but this protocol is used
exclusively and is largely inaccessible to API consumers unless they fully adopt
gRPC tooling client-side, which places an integration burden on consumers who
are not familiar with gRPC. Consumers of gRPC APIs must use a gRPC library in a
supported language, as well as build up tooling to generate their own client
code if their API provider doesn't offer a client library in their programming
language.

## Why jAPI?

### jAPI is portable

You can offer your API anywhere a JSON payload can be supplied. That could be an
HTTP URL, but it could also be a websocket, a topic for a message broker like
Kafka, the browser event loop, or even simple inter-process communication
interfaces like UNIX named pipes.

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
  that should be omitted by the API provider so as to further optimize network
  performance through reduced serialization.

Again, all of these features are opt-in client-side, provided to the consumer
through server-side jAPI libraries (which makes these features automatic without
any effort by the server-side implementation).
