# 25. Managed auth

Sometimes the client is not going to handcraft `@auth_` at all. Cookies are the
common example.

## Install the Python library

```sh
pip install --pre telepact
```

## Use a token-shaped `union.Auth_`

```yaml
- union.Auth_:
    - Token:
        token: string
```

## Inject `@auth_` from the transport layer

Capture the incoming cookie header in your HTTP adapter, then pass a callback to
`telepact_server.process(...)` that copies the session into `@auth_`.

Here is the key pattern:

```py
import asyncio
from http.cookies import SimpleCookie


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


def process_http_request(request_bytes: bytes, raw_cookie_header: str | None):
    def update_headers(headers: dict[str, object]) -> None:
        session_token = read_session_cookie(raw_cookie_header)
        if session_token is not None:
            headers['@auth_'] = {'Token': {'token': session_token}}

    return asyncio.run(telepact_server.process(request_bytes, update_headers))
```

Now the rest of our auth story can stay the same:

- `union.Auth_` still defines the credential shape
- `on_auth` still validates it
- handlers still work with normalized identity headers

From the client's perspective, auth can be "managed" by the transport. That is a
nice fit for browser cookies.

Next: [26. Schema evolution](./26-schema-evolution.md)
