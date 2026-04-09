# 17. Auth

Let's finish by looking at Telepact's auth convention.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect the public auth type:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

Relevant excerpt:

```json
{
  "union.Auth_": [
    {"Ephemeral": {"username": "string"}},
    {"Session": {"token": "string"}}
  ]
}
```

A useful rule of thumb is: if `union.Auth_` exists in the schema, we should
expect auth-related errors to be possible.

Now let's include internal definitions too:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Relevant excerpts:

```json
{
  "headers.Auth_": {
    "@auth_": "union.Auth_"
  }
}
```

```json
{
  "errors.Auth_": [
    {"ErrorUnauthenticated_": {"message!": "string"}},
    {"ErrorUnauthorized_": {"message!": "string"}}
  ]
}
```

Let's call `fn.logout` without auth first:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.logout": {"username": "demo-user"}}]'
```

```json
[{}, {"ErrorUnauthenticated_": {"message!": "Valid authentication is required."}}]
```

The schema already told us what to do next. This server's `union.Auth_` says a
session token is one valid credential shape, and this particular server happens
to expose a `fn.login` function that gives us one.

Let's log in, capture the token, and then send it back in `@auth_`:

```sh
TOKEN=$(curl -s http://localhost:8000/api \
  --data '[{}, {"fn.login": {"username": "demo-user"}}]' \
  | python -c 'import json,sys; print(json.load(sys.stdin)[1]["Ok_"]["token"])')

curl -s http://localhost:8000/api \
  --data "[{\"@auth_\": {\"Session\": {\"token\": \"$TOKEN\"}}}, {\"fn.logout\": {\"username\": \"demo-user\"}}]"
```

```json
[{}, {"Ok_": {}}]
```

Server implementations own the policy details around authentication and
authorization, so we need to watch the schema and docstrings closely. But on
compliant Telepact services, auth-related data still flows through the
conventional `@auth_` header.

Next: [Back to the guide](./README.md)
