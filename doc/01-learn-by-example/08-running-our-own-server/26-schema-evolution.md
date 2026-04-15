# 26. Schema evolution

Telepact encourages us to evolve schemas carefully and keep them backwards
compatible.

## Install the CLI

```sh
uv tool install --prerelease=allow telepact-cli
```

## Create an old schema

`old/api.telepact.yaml`:

```yaml
- fn.hello:
    name: string
  ->:
    - Ok_:
        message: string
```

## Create a compatible new schema

`new-ok/api.telepact.yaml`:

```yaml
- fn.hello:
    name: string
    punctuation!: string
  ->:
    - Ok_:
        message: string
```

Compare them:

```sh
telepact compare --old-schema-dir ./old --new-schema-dir ./new-ok
```

That succeeds, because we only added an optional argument field.

## Create an incompatible new schema

`new-bad/api.telepact.yaml`:

```yaml
- fn.hello:
    name: integer
  ->:
    - Ok_:
        message: string
```

Compare again:

```sh
telepact compare --old-schema-dir ./old --new-schema-dir ./new-bad
```

Output:

```text
Backwards incompatible change(s) found:
 - Field 'name' in struct 'fn.hello' has changed type from 'string' to 'integer'
```

This is the workflow we want in server development: evolve the schema, then let
`telepact compare` keep us honest.

Next: [27. TDD with TestClient](./27-test-client-tdd.md)
