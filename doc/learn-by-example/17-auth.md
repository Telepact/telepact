# 17. Auth

Let's finish by looking at Telepact's auth conventions.

## Start a fresh demo server

```sh
telepact demo-server --port 8020
```

First, ask for the public schema and look for `union.Auth_`:

```sh
curl -s http://127.0.0.1:8020/api -X POST -d '[{}, {"fn.api_": {}}]'
```

Schema excerpt:

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

That definition is our cue that auth-related errors may appear.

Now ask for internal definitions so we can see the auth header and shared auth
errors:

```sh
curl -s http://127.0.0.1:8020/api -X POST -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Schema excerpts:

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

Let's try calling `fn.logout` without `@auth_`:

```sh
curl -s http://127.0.0.1:8020/api -X POST -d '[{}, {"fn.logout": {"username": "alice"}}]'
```

```json
[{}, {"ErrorUnauthenticated_": {"message!": "Valid authentication is required."}}]
```

So this service wants credentials in `@auth_`. For this demo server, we can get
a session token from `fn.login`:

```sh
curl -s http://127.0.0.1:8020/api -X POST -d '[{}, {"fn.login": {"username": "alice"}}]'
```

```json
[{}, {"Ok_": {"token": "..."}}]
```

Then we send that token back through `@auth_`:

```sh
curl -s http://127.0.0.1:8020/api -X POST -d '[{"@auth_": {"Session": {"token": "<token-from-login>"}}}, {"fn.logout": {"username": "alice"}}]'
```

```json
[{}, {"Ok_": {}}]
```

This last page is a good reminder that server implementations own the actual
authentication and authorization policy. So we always need to read the schema
and docstrings for service-specific details. But across compliant Telepact
servers, auth data belongs in the `@auth_` header.

Next: [Back to the walkthrough index](./README.md)
