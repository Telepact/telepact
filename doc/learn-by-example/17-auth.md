# 17. Auth

Let's finish by looking at Telepact's auth convention.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Find the auth model in the schema

First, the public schema shows the auth payload itself:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

```jsonc
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

When `union.Auth_` exists, we should expect auth-related errors somewhere in the service.

Now let's ask for the internal view too:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

```jsonc
{
  "headers.Auth_": {
    "@auth_": "union.Auth_"
  },
  "->": {},
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

## Try `fn.logout` without auth

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.logout": {"username": "shared"}}]'
```

```json
[{}, {"ErrorUnauthenticated_": {"message!": "Valid authentication is required."}}]
```

The schema told us why: this service expects credentials in the `@auth_` header.

## Log in, then send `@auth_`

Get a token:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.login": {"username": "bob"}}]'
```

```json
[{}, {"Ok_": {"token": "<token>"}}]
```

Now use that token in `@auth_`:

```sh
curl http://localhost:8000/api -X POST --data '[{"@auth_": {"Session": {"token": "<token>"}}}, {"fn.logout": {"username": "bob"}}]'
```

```json
[{}, {"Ok_": {}}]
```

This login/logout flow is specific to this demo server. Other Telepact services can define different auth functions and policies, so let's read the docstrings and schema carefully. But for compliant Telepact auth, the credentials always travel through `@auth_`.

Next: [Back to the guide index](./README.md)
