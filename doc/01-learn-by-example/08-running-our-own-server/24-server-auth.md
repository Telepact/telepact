# 24. Server auth

Now let's add one piece of Telepact's auth convention to our own server.
For the full canonical path, see the
[Auth Guide](../../03-build-clients-and-servers/05-auth.md).

## Install the Python library

```sh
pip install --pre telepact
```

## Add `union.Auth_` to the schema

```yaml
- union.Auth_:
    - Password:
        password: string

- fn.secret: {}
  ->:
    - Ok_:
        message: string
```

## Implement `on_auth`

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
3. return normalized identity or authorization headers for later handlers

That normalization step is the core Telepact server-side auth pattern.

## Call it

Without auth:

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.secret": {}}]'
```

With auth:

```sh
curl -s localhost:8002/api/telepact -d '[{"@auth_": {"Password": {"password": "swordfish"}}}, {"fn.secret": {}}]'
```

This keeps the public credential shape in the schema and the auth normalization
logic in one clear place.

Next: [25. Managed auth](./25-managed-auth.md)
