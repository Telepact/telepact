---
name: telepact-downstream-testing
description: Test code that consumes an external Telepact API by standing up a Telepact CLI mock server from the downstream schema. Use when Codex needs to validate a client integration against a downstream Telepact service, fetch `fn.api_` from a live server, run `telepact mock`, stub downstream behavior, or verify that requests are schema-correct before pointing code at the real dependency.
---

# Telepact Downstream Testing

Use this skill when the task is to test your code against a downstream Telepact API that your system consumes.

The default approach should be:

1. obtain the downstream schema through the Telepact CLI
2. run a Telepact mock server for that schema
3. point your code under test at the mock instead of the live dependency
4. use the mock to validate requests and produce schema-compliant responses

Important boundary:

- the CLI may contact the live downstream server to fetch its schema
- your test code should send downstream requests only to the mock

This is the preferred path because the mock server will:

- validate incoming requests against the downstream schema
- return type-compliant responses for the downstream API
- let tests override responses with explicit stubs when needed
- let tests verify that the expected downstream calls actually happened

For most downstream integrations, thorough tests against the mock can provide rigorous confidence that the real integration will succeed.

## Scope

This skill is for testing a consumer of a Telepact API, not for implementing the downstream server itself.

Use it when:

- your application calls an external Telepact API
- you want strong integration confidence without depending on a flaky or costly live server
- you need to validate request shapes against the real downstream schema
- you need deterministic downstream scenarios in tests

Do not default to ad hoc fake JSON servers when the dependency is already Telepact. Prefer the Telepact CLI mock path first.

## First Step

Classify which of these two setup modes fits better:

### Mode A: Fetch Then Mock

Use this when you want a checked-in or repeatable local schema snapshot.

1. fetch the schema from the live Telepact server
2. store it locally
3. run a mock from the saved schema directory

Commands:

```sh
telepact fetch --http-url http://downstream.example/api --output-dir test/downstream-api
telepact mock --dir test/downstream-api --port 8081
```

This is the best default for CI, reproducible local testing, and offline iteration.

### Mode B: Mock Directly From Live

Use this when you want the fastest path and do not need to persist the schema snapshot first.

Command:

```sh
telepact mock --http-url http://downstream.example/api --port 8081
```

This still fetches the schema through `fn.api_`, but it does so at mock startup time instead of storing it first.

## Core Recommendation

Point the code under test at the mock server, not at the live downstream service.

In tests, replace the downstream base URL so every downstream call hits the mock URL.

Do not split confidence across separate hand-written validators and fake payload generators if the Telepact mock can do both for you.

For example, if the real downstream is `http://downstream.example/api` and your mock is running at `http://localhost:8081/api`, test traffic should go to the mock:

```sh
curl http://localhost:8081/api \
  -H 'content-type: application/json' \
  --data '[{}, {"fn.ping_": {}}]'
```

After the mock is running, use the mock itself for discovery:

1. call `fn.ping_` on the mock to confirm your test target is reachable
2. call `fn.api_` on the mock with `{}` to inspect the user-facing downstream schema
3. call `fn.api_` on the mock with `{"includeInternal!": true}` to inspect the full schema including the mock control functions (e.g. `[{}, {"fn.api_": {"includeInternal!": true}}]`)

## Why The Mock Matters

The Telepact CLI mock is stronger than a generic fake server because it is schema-driven.

It gives you:

- request validation against the real downstream Telepact schema
- generated responses that are valid for the downstream result unions
- support for mock control functions such as `fn.createStub_`, `fn.verify_`, and `fn.verifyNoMoreInteractions_`

That means your tests can catch:

- wrong `fn.*` names
- wrong request field names
- missing required fields
- invalid headers
- incompatible response assumptions in your consumer

## Standard Workflow

1. Confirm the downstream API is actually Telepact.
2. Prefer `telepact fetch` plus `telepact mock --dir` if you want repeatable tests.
3. Otherwise use `telepact mock --http-url` for a quick schema-backed mock.
4. Start the mock server on a local port.
5. Configure your code under test to call the mock URL.
6. Use `fn.ping_` and `fn.api_` against the mock to confirm connectivity and inspect the API surface your tests will target.
7. Use `fn.api_` with `{"includeInternal!": true}` against the mock when you want the full available definitions, including mock control functions.
8. Run consumer tests against the mock.
9. Add stubs and verification calls for scenario-specific tests.
10. Keep one or two live smoke tests if needed, but do not rely on the live dependency for the main integration suite.

## Mock Controls

The mock server exposes extra Telepact functions for test control.

The most important ones are:

- `fn.createStub_`: force a specific downstream result for matching calls
- `fn.verify_`: assert that a matching downstream call happened
- `fn.verifyNoMoreInteractions_`: assert there were no unexpected extra downstream calls
- `fn.clearStubs_`: clear configured stubs
- `fn.clearCalls_`: clear recorded invocations

Use generated responses by default. Add explicit stubs only when the test needs a very specific downstream behavior.

### Typical Pattern

1. start with the schema-backed mock response generation
2. run the code under test
3. verify the downstream call shape with `fn.verify_`
4. add `fn.createStub_` only for scenarios where the generated response is not specific enough

This keeps tests close to the schema while still allowing targeted control.

## Confidence Model

Generated Telepact code is optional. It can improve compile-time ergonomics, but it is not the only way to get strong integration confidence.

If your tests:

- drive real consumer code
- hit a Telepact mock built from the actual downstream schema
- verify downstream calls
- cover the important success and error cases

then you can get confidence that is comparable in practice to many type-safe generated-client setups.

The key is that the mock is validating what your consumer actually sends and returning responses that remain schema-valid.

## Practical Guidance

- Prefer `telepact fetch` when you want schema changes to be explicit in version control.
- Prefer `telepact mock --http-url` when you are exploring quickly or debugging against the current live schema.
- Use `fn.api_` with `includeInternal!` against the mock when you want to enumerate all mock control functions available for testing.
- Keep the downstream mock running over HTTP or WebSocket at the same path shape your app already expects.
- Use stubs for named business scenarios, not as a blanket replacement for the mock's generated responses.
- Verify calls explicitly when the test needs to prove that the consumer sent the right request.

## Minimal Examples

Fetch a local snapshot and start a mock:

```sh
telepact fetch --http-url http://localhost:8000/api --output-dir test/downstream-api
telepact mock --dir test/downstream-api --port 8081
```

Start a mock directly from a live Telepact server:

```sh
telepact mock --http-url http://localhost:8000/api --port 8081
```

Then point your consumer at:

```text
http://localhost:8081/api
```

## Testing Rules

- Default to the Telepact CLI mock instead of a hand-written fake downstream server.
- Use the real downstream schema, fetched through `fn.api_`, whenever possible.
- Send test traffic to the mock, not to the live downstream service.
- Inspect mock capabilities such as `fn.createStub_` and `fn.verify_` by calling `fn.api_` with `{"includeInternal!": true}` on the mock.
- Treat request validation failures from the mock as real integration failures in your consumer code.
- Prefer schema-driven generated responses first, then add explicit stubs only where necessary.
- Verify downstream interactions when request shape or call count matters.
