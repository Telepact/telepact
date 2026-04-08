# 17. Auth

Let's finish by looking at how Telepact surfaces auth.

The demo server defines this credential union:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]' | python -m json.tool
```

```json
{
  "union.Auth_": [
    {
      "Ephemeral": {
        "username": "string"
      }
    },
    {
      "Session": {
        "token": "string"
      }
    }
  ]
}
```

When `union.Auth_` exists, we should expect auth-related behavior around the
`@auth_` header. If we include internal definitions, we can see that directly:

```json
{
  "headers.Auth_": {
    "@auth_": "union.Auth_"
  },
  "->": {}
}
```

```json
{
  "errors.Auth_": [
    {
      "ErrorUnauthenticated_": {
        "message!": "string"
      }
    },
    {
      "ErrorUnauthorized_": {
        "message!": "string"
      }
    }
  ]
}
```

Let's try `fn.logout` without auth:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.logout": {"username": "auth-guide"}}]' | python -m json.tool
```

```json
[
  {},
  {
    "ErrorUnauthenticated_": {
      "message!": "Valid authentication is required."
    }
  }
]
```

The schema told us this server supports a session token flow, so let's get one
from `fn.login`:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.login": {"username": "auth-guide"}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "token": "<random string>"
    }
  }
]
```

Now let's use that token in `@auth_` and call `fn.logout` again:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Session": {"token": "<token-from-login>"}}}, {"fn.logout": {"username": "auth-guide"}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

This demo server happens to offer both `Ephemeral` and `Session` auth. Another
Telepact server might define `union.Auth_` differently, so we always need to read
the schema and its docstrings for the server-specific policy. But across
compliant Telepact servers, auth-related data travels in `@auth_`.

Next, let's keep going with the broader reference docs, especially the
[Production Guide](../production-guide.md) and [Schema Guide](../schema-guide.md).
