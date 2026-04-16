# 25. Managed auth

Sometimes the client is not going to handcraft `@auth_` at all. Cookies are the
common example.

This page shows the browser/session-cookie branch of Telepact's recommended auth
model. For the full canonical path, see the
[Auth Guide](../../03-build-clients-and-servers/05-auth.md).

## Install the Python library

```sh
pip install --pre telepact
```

## Use a session-shaped `union.Auth_`

```yaml
- union.Auth_:
    - Session:
        token: string
```

## Inject `@auth_` from the transport layer

Here is the key pattern:

```py
import asyncio
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        content_length = int(self.headers.get('Content-Length', '0'))
        request_bytes = self.rfile.read(content_length)
        session_token = read_session_cookie(self.headers.get('Cookie'))

        def update_headers(headers: dict[str, object]) -> None:
            if session_token is not None:
                headers['@auth_'] = {'Session': {'token': session_token}}

        response = asyncio.run(telepact_server.process(request_bytes, update_headers))
```

Now the rest of our auth story can stay the same:

- `union.Auth_` still defines the credential shape
- `on_auth` still validates it
- handlers still work with normalized identity headers

From the client's perspective, auth can be "managed" by the transport. That is a
nice fit for browser cookies, while still converging on the canonical `@auth_`
shape inside the Telepact server.

Next: [26. Schema evolution](./26-schema-evolution.md)
