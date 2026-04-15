# 24. Server auth

Now let's add an explicit auth story to our own server.

## Install the Python library

```sh
pip install --pre telepact
```

## Extend the minimum server schema

Starting from [22. Minimum server](./22-minimum-server.md), update
`api/hello.telepact.yaml` to add `union.Auth_` and a protected function:

```yaml
- union.Auth_:
    - Password:
        password: string

- fn.secret: {}
  ->:
    - Ok_:
        message: string
```

## Add auth handling in `server.py`

In `server.py`, keep the same `schema`, `function_router`, and HTTP handler shape
from lesson 22, then add `on_auth` and a protected `secret` handler:

```py
from telepact import Message, Server

options = Server.Options()


def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    if auth == {'Password': {'password': 'swordfish'}}:
        return {'@role': 'admin'}
    return {}


options.on_auth = on_auth


async def secret(function_name: str, request_message: Message) -> Message:
    if request_message.headers.get('@role') != 'admin':
        return Message({}, {'ErrorUnauthenticated_': {'message!': 'missing or invalid credentials'}})
    return Message({}, {'Ok_': {'message': 'welcome'}})
```

The important shape here is:

1. read credentials from `@auth_`
2. validate them in `on_auth`
3. return identity or authorization headers for later handlers

## Call it

Without auth:

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.secret": {}}]'
```

With auth:

```sh
curl -s localhost:8002/api/telepact -d '[{"@auth_": {"Password": {"password": "swordfish"}}}, {"fn.secret": {}}]'
```

This keeps the auth policy in the schema and the authentication logic in one
clear place.

Next: [25. Managed auth](./25-managed-auth.md)
