# FAQ

## Why have both optional and nullable fields?

Telepact allows API designers to mark a field as optional (the field might be
omitted) as well as mark the field type as nullable (the field might appear with
a null value).

These design options are both present to maximize the design expressiveness of
the API. Telepact leverages optionality to accomplish the expressiveness of
`undefined` in languages like TypeScript. While `null` is a value that can be
passed around like a string or number, `undefined` or optionality can not be
passed around but is rather an incidental property of the shape of the data
itself. This is especially useful in update APIs where, for example, if you want
to erase just one field of a model, where null can be used to indicate the
erasure of data, and optionality can be used to omit all fields except the one
field you want to erase.

## Why can I not define nullable arrays or objects?

Nullability is indicated on base types by appending type strings with `?`, but
since collection types are defined with native JSON array and object syntax,
using `[]` and `{}` respectively, there is no way to append `?` to these
expressions since free `?` characters are not legal JSON syntax.

This apparent design constraint, albeit coincidental, aligns with Telepact's
design goals of expressibility without redundant design options. In Telepact,
null represents "empty" (while optional represents "unknown"). Since array and
object collection types can already express "emptiness," nullability is
unnecessary.

## Why is there nothing like a standard 404 Not Found error?

Telepact provides several standard errors to represent common integration
issues, such as request and response incompatibilities and
authentication/authorization errors, all reminisicent of the 400, 500, 401 and
403 error codes, respectively, but there is no standard error that approximates
404 Not Found.

Instead, API designers are encouraged to abstract concepts as data whenever
possible, and the 404 Not Found use-case can be trivially represented with an
empty optional value.

## But the given 400-like Bad Request errors are too precise. Why is a more general-purpose "Bad Request" error not available?

Telepact has several errors to communicate request invalidity with respect to
the API schema, but there is no out-of-the-box "Bad Request" error that a server
can raise from some custom validation logic in the server handler.

Overly generalized abstractions, such as a catch-all "Bad Request", are
unpreferred in Telepact in precise of rigid data types. Where necessary, all
"Bad Request" use-cases can be enumerated in function results alongside the
`Ok_` tag. API designers are encouraged to prefer data abstractions over errors
wherever possible, such as preferring empty optionals over "Not Found" errors.

## Why do functions in Telepact not support positional arguments?

Telepact functions are automatically associated with an argument struct and a
result struct that API designers can use to define arguments and return values,
respectively. The arguments being supplied via the argument struct will be
inherently unordered due to the nature of JSON objects, and there is no way to
approximate traditional positional arguments at the root of the Request Message
Body.

This design decision is intentional. Positional arguments are a significant risk
that provoke backwards incompatible changes through seemingly innocent API
changes, such as changing the order of arguments or appending new arguments.
This problem is especially pronounced in generated code for many programming
languages. By making the design entry point a struct, API designers are
predisposed for backwards-compatible changes like appending optional struct
fields.

## Why is there no Enum type as seen in C or Java?

Telepact achieves enumerated types with unions, which are very similar to enums
as seen in C or Java, except that a struct is automatically attached to each
value. The traditional enum can be approximated by simply leaving all union
structs blank.

## Why force servers to perform response validation?

Telepact automatically performs validation of responses against the Telepact
schema, and there is no setting for servers to turn off this behavior.

This design decision is intentional. It helps maintain the high standard of type
safety in the Telepact ecosystem by denying API providers the option of
categorizing malformed data as an inconvenience and are instead forced to deal
with hard failures through bug reports. Hard failures also help draw attention
to type safety deficits early in the development phase.

Clients who are uniquely vulnerable to hard server failures and who find it
advantageous to receive the malformed data anyway are able to turn off this
response validation by submitting their requests with the `{"@unsafe_":true}`
header.

## If all I want is compact binary serialization, why not just use gRPC?

Telepact and gRPC both have compact binary serialization for drastically
improved efficiency over conventional serialization such as JSON. However,
Telepact brings a critical new innovation to the space of RPC and binary
serialization in that it _does not leak the ABI into the API_.

ABI, or Application _Binary_ Interface, is the actual interface between RPC
clients and servers using such compact serialization protocols. The data passing
through this interface is unreadable due to conventional json keys being encoded
as numbers. Because an encoding is in play, clients and servers need to agree on
what numbers represent which fields all throughout the API. gRPC and other
conventional RPC frameworks accomplish this by having the clients and servers
both base their field ids on the same information during code generation by
leaking these ABI field ids into the API schema itself. Unfortunately, this adds
an unusual cognitive burden for developers designing such APIs, because they now
need to guard against interface drift between the API and the ABI, typically by
complying with a set of policies concerning how those field ids are defined and
how they can change.

Telepact breaks free from the conventional practice of defining and maintaining
field ids, and instead accomplishes client and server agreement over field ids
through a client-server handshake at runtime. In consequence, Telepact boasts a
far simpler developer experience during the API design phase as well as the
unique privilege of allowing clients to leverage binary serialization without
generated code.

## Why can't I have other non-error result union values?

The only required tag for the function result union is `Ok_`. All other tags in
the result union that are not `Ok_` are, by definition, "not okay", and will be
interpreted as an error in all circumstances. API designers are encouraged to
prefix additional result union tags with `Error` or equivalent to improve
readability and recognition of errors.

## Why can't I associate a union tag to something besides a struct?

A designer might want to treat a union tag like a struct field, and associate
any data type with a tag. However, in Telepact, all tags in unions are
associated with a struct, which means you can't associate union tags with
simpler data types, like booleans or strings.

This restriction is in place to uphold Telepact's value of prioritizing
effective software evolution. Unions, like functions, are entrypoints to unique
execution paths in software, so if software evolves such that an execution path
requires a new "argument" like a integer, that requirement will percolate up to
the entrypoint. If the proverbial API designer chose to associate the union tag
directly to a boolean, the API would require a breaking change in the form of
creating another tag to make room for this new integer "argument" to sit next to
the original boolean. In contrast, Telepact establishing the expectation that
all union tags are associated with structs means the backwards compatible option
of adding a new struct field is always available to software designers dealing
with the needs of evolving software.

## Why can I not omit fn.\* fields using the `"@select_"` header?

The `"@select_"` header is used to omit fields from structs, which includes
union structs, but not the argument struct included with function definitions.

The function type exists so that API providers may incorporate "links" into
their API design, such that the appearance of a function type payload can simply
be copied and pasted verbatim into the body a new message. Tooling like the
Telepact console specifically utilizes this technique to allow end-users to
"click through" graphs designed by the API provider.

Omitting fields in the argument struct disrupts the API provider's ability to
established well-defined links, and consequently, the `"@select_"` header is
disallowed from omitting fields in function argument structs.
