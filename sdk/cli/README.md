# Telepact CLI

The CLI is a tool for various development jobs, such as fetching API schemas,
starting schema-backed mock servers for testing purposes, and optionally
generating code.

## Installation

```
uv tool install --prerelease=allow telepact-cli
```

Published PyPI releases are currently prereleases. To pin a specific CLI
release, use the exact version from
[doc/04-operate/03-versions.md](https://github.com/Telepact/telepact/blob/main/doc/04-operate/03-versions.md).

## Usage

### `telepact --help`
```
Usage: telepact [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  codegen      Generate code bindings for a Telepact API schema.
  compare      Compare two Telepact API schemas for backwards compatibility.
  demo-server  Start a demo Telepact server.
  fetch        Fetch a Telepact API schema to store locally.
  mock         Start a mock server for a Telepact API schema.
```

### `telepact codegen --help`
```
Usage: telepact codegen [OPTIONS]

  Generate code bindings for a Telepact API schema.

Options:
  --schema-http-url TEXT  telepact schema directory
  --schema-dir TEXT       telepact schema directory
  --lang TEXT             Language target (one of "java", "py", "ts", or "go")
                          [required]
  --out TEXT              Output directory  [required]
  --package TEXT          Package name (required when --lang is "java" or "go")
  --help                  Show this message and exit.
```

### `telepact compare --help`
```
Usage: telepact compare [OPTIONS]

  Compare two Telepact API schemas for backwards compatibility.

Options:
  --new-schema-dir TEXT  New telepact schema directory  [required]
  --old-schema-dir TEXT  Old telepact schema directory  [required]
  --help                 Show this message and exit.
```

### `telepact fetch --help`
```
Usage: telepact fetch [OPTIONS]

  Fetch a Telepact API schema to store locally.

Options:
  --http-url TEXT    HTTP URL of a Telepact API  [required]
  --output-dir TEXT  Directory of Telepact schemas  [required]
  --help             Show this message and exit.
```

### `telepact mock --help`
```
Usage: telepact mock [OPTIONS]

  Start a mock server for a Telepact API schema.

Options:
  --http-url TEXT                 HTTP URL of a Telepact API
  --dir TEXT                      Directory of Telepact schemas
  --port INTEGER                  Port to run the mock server on
  --path TEXT                     Path to expose the mock API (default: /api)
  --generated-collection-length-min INTEGER
                                  Minimum length of generated collections
  --generated-collection-length-max INTEGER
                                  Maximum length of generated collections
  --disable-optional-field-generation
                                  Disable generation of optional fields
                                  (enabled by default)
  --disable-message-response-generation
                                  Disable generation of message responses
                                  (enabled by default)
  --disable-random-optional-field-generation
                                  Disable randomization of optional field
                                  generation (enabled by default)
  --help                          Show this message and exit.
```

NOTE: The `mock` command is an empowering development tool for clients. You do
not need to develop against a live server; you can use the `mock` command to
set up a "middle-man" server that will validate requests for schema compliance
and return schema-compliant auto-generated responses (which can be overridden
with manual stubs if desired.)
