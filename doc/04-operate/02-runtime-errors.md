# Runtime Error Guide

Telepact keeps wire compatibility and local diagnostics separate.

- On the wire, server-side unexpected failures still become `ErrorUnknown_`.
- Locally, Telepact libraries now try to classify failures so application logs
  and caught exceptions say whether the problem came from parsing, validation,
  serialization, transport, or user server logic (middleware / function routes).

## Failure Categories

| Category | What it means | Typical local signal |
| --- | --- | --- |
| `parse` | The server could not decode the incoming request bytes into a Telepact message. | `telepact request parsing failed while decoding the incoming message` |
| `validation` | A message was decoded, but Telepact rejected headers or body data against the schema. | `telepact response validation failed ...` or `telepact response header validation failed ...` |
| `serialization` | Telepact could not serialize or deserialize a message at the library boundary. | `telepact serialization failed ...` or `telepact client serialization or deserialization failed` |
| `transport` | The client adapter timed out or failed while talking to the remote service. | `telepact client transport failed` or `telepact client transport timed out ...` |
| `handler` | User server middleware or function-route code threw while handling a valid request message. | `telepact handler failed while handling fn.someCall` |

## Server-Side Behavior

For server code:

- invalid requests still return schema-level errors such as
  `ErrorInvalidRequestBody_` and `ErrorInvalidRequestHeaders_`
- invalid handler responses still return
  `ErrorInvalidResponseBody_` or `ErrorInvalidResponseHeaders_`
- unexpected handler or serialization failures still return `ErrorUnknown_`

When that happens, treat the `caseId` in `ErrorUnknown_` as a correlation ID:
log it on the server next to the real exception details, then use it to match a
client-side error report back to the corresponding server-side log entry.

The main change is the local callback surface:

- `options.onError` receives contextual errors instead of raw implementation
  exceptions where practical
- response-validation failures are reported to `onError` before Telepact returns
  the corresponding invalid-response union on the wire

## Client-Side Behavior

For client code:

- adapter timeouts and transport failures are categorized as `transport`
- serializer failures before request send or while decoding a response are
  categorized as `serialization`
- the original cause remains attached where the language runtime supports it

## Language Notes

- TypeScript: `TelepactError` exposes `kind` and preserves `cause` when
  available.
- Python: `TelepactError` and `SerializationError` carry `kind`, `cause`, and
  `context` attributes.
- Java: `TelepactError#getKind()` and `SerializationError#getContext()` expose
  the broad diagnostic category.
- Go: public client errors use `TelepactError` with `errors.Is` / `errors.As`
  support via `Unwrap()`. Internal server callbacks receive wrapped `error`
  messages with the same category wording.

## Debugging Rule Of Thumb

1. If the wire response is `ErrorInvalid*`, fix the schema mismatch first.
2. If the wire response is `ErrorUnknown_`, capture the client-visible `caseId`
   and match it against the same `caseId` in server logs; the local Telepact
   error should usually tell you whether the root cause was middleware /
   function-route code or serialization.
3. If the client raised before any response arrived, check whether the local
   error is `transport` or `serialization`.
