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

In a real repository, you would usually compare the checked-in schema directory
from Git instead of hand-made `old` and `new-*` folders. For example, to compare
the current branch against `origin/main`:

```sh
old_dir="$(mktemp -d)"
new_dir="$(mktemp -d)"

git archive origin/main api | tar -x -C "$old_dir"
git archive HEAD api | tar -x -C "$new_dir"

telepact compare \
  --old-schema-dir "$old_dir/api" \
  --new-schema-dir "$new_dir/api"
```

Replace `api` with the schema directory your project checks in.

Next: [27. TDD with TestClient](./27-test-client-tdd.md)
