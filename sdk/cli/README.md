# Telepact CLI

The CLI is a tool for various development jobs, such as fetching API schemas,
generating code, and starting up mock servers for testing purposes.

## Installation

```
pipx install telepact-cli
```

## Usage

```
telepact --help
```

### `telepact codegen`

```
telepact codegen --lang {java|py|ts} --out PATH \
								 [--schema-dir PATH | --schema-http-url URL] \
								 [--package PACKAGE]
```

Generate bindings from a schema directory or HTTP endpoint. Java targets must include `--package`.

### `telepact fetch`

```
telepact fetch --http-url URL --output-dir PATH
```

Fetch a remote Telepact API and save it as `api.telepact.json`.

### `telepact mock`

```
telepact mock (--http-url URL | --dir PATH)
							 [--port 8080] [--path /api]
							 [--generated-collection-length-min N]
							 [--generated-collection-length-max N]
							 [--disable-optional-field-generation]
							 [--disable-message-response-generation]
							 [--disable-random-optional-field-generation]
```

Serve a mock HTTP/WebSocket API based on a schema. Only one schema source (`--http-url` or `--dir`) may be provided.

### `telepact demo-server`

```
telepact demo-server [--port 8000]
```

Run the bundled calculator demo schema on `/api`.

### `telepact compare`

```
telepact compare --old-schema-dir PATH --new-schema-dir PATH
```

Exit with status `1` if backwards-incompatible changes are detected between schema directories.

