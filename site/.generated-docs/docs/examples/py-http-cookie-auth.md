# py-http-cookie-auth

Minimal Python Telepact example that shows Telepact's recommended browser auth
flow:

- define a session credential in `union.Auth_`
- read the browser cookie at the HTTP boundary
- translate it into `@auth_`
- normalize it in `on_auth`

Browse the files:

- [`api/auth.telepact.yaml`](#api-auth-telepact-yaml) - Telepact schema
- [`server.py`](#server-py) - server implementation
- [`test_example.py`](#test-example-py) - example test
- [`test_support.py`](#test-support-py) - test helpers
- [`Makefile`](#makefile) - local run target

Run it:

```bash
make run
```

## Source Files

### Makefile

```bash
#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

SHELL := /bin/bash
PYTHON := .venv/bin/python

.PHONY: run

run:
	@set -euo pipefail; $(MAKE) -C ../../lib/py; rm -rf .venv; uv venv --python python3.11 .venv; uv pip install --python $(PYTHON) pytest ../../lib/py/dist/*.tar.gz; $(PYTHON) -m pytest -q
```

### api/

#### api/auth.telepact.yaml

```yaml
#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

- union.Auth_:
    - Session:
        token: "string"
- fn.me: {}
  ->:
    - Ok_:
        userId: "string"
```

### server.py

```python
#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

import asyncio
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles

VALID_SESSION = 'demo-session'

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


async def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    session = auth.get('Session') if isinstance(auth, dict) else None
    if isinstance(session, dict) and session.get('token') == VALID_SESSION:
        return {'@userId': 'user-123'}
    return {}


options.on_auth = on_auth


async def me(function_name: str, request_message: Message) -> Message:
    if request_message.headers.get('@userId') != 'user-123':
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'missing or invalid session cookie',
            },
        })

    return Message({}, {
        'Ok_': {
            'userId': 'user-123',
        },
    })


function_router = FunctionRouter({'fn.me': me})
telepact_server = Server(schema, function_router, options)


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


def create_http_server(host: str = '127.0.0.1', port: int = 0) -> ThreadingHTTPServer:
    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != '/api/telepact':
                self.send_response(404)
                self.end_headers()
                return

            content_length = int(self.headers.get('Content-Length', '0'))
            request_bytes = self.rfile.read(content_length)
            session_token = read_session_cookie(self.headers.get('Cookie'))

            def update_headers(headers: dict[str, object]) -> None:
                if session_token is not None:
                    headers['@auth_'] = {'Session': {'token': session_token}}

            response = asyncio.run(telepact_server.process(request_bytes, update_headers))
            content_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(response.bytes)

        def log_message(self, format_string: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), RequestHandler)
```

### test_example.py

```python
#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from server import create_http_server
from test_support import post_json, run_server, stop_server


def test_cookie_auth_example_runs_end_to_end() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'

        unauthenticated = post_json(url, [
            {},
            {
                'fn.me': {},
            },
        ])
        unauthenticated_body = unauthenticated[1]
        assert 'Ok_' not in unauthenticated_body
        assert any('error' in key.lower() for key in unauthenticated_body)

        authenticated = post_json(url, [
            {},
            {
                'fn.me': {},
            },
        ], headers={'Cookie': 'session=demo-session'})
        assert authenticated[1]['Ok_']['userId'] == 'user-123'
    finally:
        stop_server(server, thread)
```

### test_support.py

```python
#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer


def run_server(server: ThreadingHTTPServer) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def stop_server(server: ThreadingHTTPServer, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def post_json(url: str, body: list[object], *, headers: dict[str, str] | None = None) -> list[object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json', **(headers or {})},
        method='POST',
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode('utf-8'))
```
