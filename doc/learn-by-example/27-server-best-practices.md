# 27. Best practices for server implementers

Let's finish by pulling the server-side lessons together.

## 1. Be explicit in the schema

If clients are expected to use a field, type, function, or header directly,
define it clearly in the schema and document it with `///`.

## 2. Use the best data shape, not a vague error

Prefer expressive data over HTTP-shaped habits:

- prefer optional fields over "404 not found"
- let Telepact handle request validation instead of inventing a generic "400"
- use function-specific errors for real business rules

The [FAQ](../faq.md) is worth reading end to end here.

## 3. Log on the server

Keep request lifecycle logging in middleware and error details in `on_error`.
Clients may only see `ErrorUnknown_`, so logs are where operational detail lives.

## 4. Favor backwards compatibility

Treat schema evolution as a normal part of development and check it with
`telepact compare`.

## 5. Let Telepact do the ecosystem work

Once the server uses a Telepact library correctly, clients can choose the level
of tooling they want:

- raw `curl`
- runtime clients
- field selection
- binary
- mocks
- code generation

That breadth is one of Telepact's best qualities: clients can start simple and
grow into richer tooling without the server changing its basic contract style.

Next: [Back to the start](./00-installation.md)
