# Docs

Welcome to the Telepact docs. Use this page to find the guides, references, and
tools you need to design, serve, and operate a Telepact API.

To learn how to write Telepact APIs, start with the
[API Schema Guide](./schema-guide.md). A
[JSON Schema](../common/json-schema.json) is available for validation. For
transport wiring patterns and concrete HTTP/WebSocket examples, see the
[Transport Guide](./transports.md). For deployment, rollout, compatibility,
auth, and observability guidance, see the
[Production Guide](./production-guide.md). For runnable end-to-end examples,
see the [Examples landing page](../example/README.md). For debugging
local/runtime failures, see the [Runtime Error Guide](./runtime-errors.md).

To learn how to serve a Telepact API, see the specific library docs:
- [Typescript](../lib/ts/README.md)
- [Python](../lib/py/README.md)
- [Java](../lib/java/README.md)
- [Go](../lib/go/README.md)

For development assistance, see the SDK tool docs:
- [CLI](../sdk/cli/README.md)
    - Conveniently retreive API schemas from running live Telepact servers, and
      use schemas to create mock servers and generate code bindings, all from
      the command line
- [Browser Console](../sdk/console/README.md)
    - Develop against a live Telepact server by reading rendered docs, drafting
      requests, and submitting live requests with json-friendly editors
- [Prettier Plugin](../sdk/prettier/README.md)
    - Consistently format your Telepact api schemas, especially the doc-strings

Find the latest versions of all libraries and sdks [here](./versions.md). That
page tracks published registry versions, which may lag the source tree between
releases.

For further reading, see [Motivation](./motivation.md).

Telepact does have a few unorthodox design decisions. To be best informed, you
should read the explanations in [the FAQ](./faq.md).
