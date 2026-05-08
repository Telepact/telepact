# py-simple-auth

Minimal Python Telepact example that starts a minimum Python server for a bakery
shift board and shows a simple auth flow with hard-coded credentials.

It demonstrates three common auth patterns:

- `on_auth` normalizes a hard-coded username/password into internal headers like
  `@employeeId` and `@station`, and throws if authentication fails
- middleware logs those normalized identity headers and catches a custom
  `Unauthorized` exception to coerce it into `ErrorUnauthorized_`
- completion of `on_auth` means identity normalization succeeded for the
  authenticated route

Hard-coded credentials used by the example:

- `lead-baker` / `opensesame` -> `@employeeId=baker-001`, `@station=oven`
- `cashier` / `knockknock` -> `@employeeId=cashier-002`, `@station=counter`
- `explode` / `boom` -> throws in `on_auth`

Browse the files:

- [`api/auth.telepact.yaml`](#api-auth-telepact-yaml) - Telepact schema
- [`server.py`](#server-py) - minimum Python Telepact server
- [`test_example.py`](#test-example-py) - Python client exercising the auth flows
- [`test_support.py`](#test-support-py) - transport helpers
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
    - Password:
        username: "string"
        password: "string"
- fn.myShift: {}
  ->:
    - Ok_:
        employeeId: "string"
        station: "string"
        pastry: "string"
- fn.approveSpecial: {}
  ->:
    - Ok_:
        message: "string"
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

from __future__ import annotations

import argparse
import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import FunctionRouter, Message, Server, TelepactSchema

LEAD_BAKER_CREDENTIALS = {'username': 'lead-baker', 'password': 'opensesame'}
CASHIER_CREDENTIALS = {'username': 'cashier', 'password': 'knockknock'}
EXPLODING_CREDENTIALS = {'username': 'explode', 'password': 'boom'}

MIDDLEWARE_EVENTS: list[dict[str, object | None]] = []
schema = TelepactSchema.from_directory('api')
options = Server.Options()


class Unauthorized(Exception):
    pass


async def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    password = auth.get('Password') if isinstance(auth, dict) else None
    if not isinstance(password, dict):
        raise ValueError('missing or invalid bakery credentials')

    if password == EXPLODING_CREDENTIALS:
        raise RuntimeError('bakery auth backend unavailable')

    if password == LEAD_BAKER_CREDENTIALS:
        return {'@employeeId': 'baker-001', '@station': 'oven'}

    if password == CASHIER_CREDENTIALS:
        return {'@employeeId': 'cashier-002', '@station': 'counter'}

    raise ValueError('missing or invalid bakery credentials')


options.on_auth = on_auth


def _log_identity(request_message: Message) -> None:
    event = {
        'event': 'middleware.identity',
        'function': request_message.get_body_target(),
        'employeeId': request_message.headers.get('@employeeId'),
        'station': request_message.headers.get('@station'),
    }
    MIDDLEWARE_EVENTS.append(event)
    print(json.dumps(event, sort_keys=True), flush=True)


async def middleware(request_message: Message, function_router: FunctionRouter) -> Message:
    _log_identity(request_message)

    try:
        return await function_router.route(request_message)
    except Unauthorized as error:
        return Message({}, {
            'ErrorUnauthorized_': {
                'message!': str(error),
            },
        })


options.middleware = middleware


async def my_shift(_function_name: str, request_message: Message) -> Message:
    pastry = 'sesame loaf' if request_message.headers['@station'] == 'oven' else 'almond croissant'
    return Message({}, {
        'Ok_': {
            'employeeId': request_message.headers['@employeeId'],
            'station': request_message.headers['@station'],
            'pastry': pastry,
        },
    })


async def approve_special(_function_name: str, request_message: Message) -> Message:
    if request_message.headers.get('@station') != 'oven':
        raise Unauthorized('oven station required to approve the special')

    return Message({}, {
        'Ok_': {
            'message': 'special approved: cardamom morning bun',
        },
    })


function_router = FunctionRouter({
    'fn.myShift': my_shift,
    'fn.approveSpecial': approve_special,
})
telepact_server = Server(schema, function_router, options)


def get_middleware_events() -> list[dict[str, object | None]]:
    return [event.copy() for event in MIDDLEWARE_EVENTS]


def reset_middleware_events() -> None:
    MIDDLEWARE_EVENTS.clear()


def create_http_server(host: str = '127.0.0.1', port: int = 0) -> ThreadingHTTPServer:
    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != '/api/telepact':
                self.send_response(404)
                self.end_headers()
                return

            content_length = int(self.headers.get('Content-Length', '0'))
            request_bytes = self.rfile.read(content_length)
            response = asyncio.run(telepact_server.process(request_bytes))
            content_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(response.bytes)

        def log_message(self, format_string: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), RequestHandler)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8002)
    args = parser.parse_args()

    server = create_http_server(args.host, args.port)
    print(f'READY {server.server_address[1]}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
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

from __future__ import annotations

import asyncio

from telepact import Client, Message, Serializer

from server import create_http_server, get_middleware_events, reset_middleware_events
from test_support import post_bytes, run_server, stop_server


async def run_example() -> None:
    server = create_http_server()
    thread = run_server(server)
    reset_middleware_events()
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'

        async def adapter(message: Message, serializer: Serializer) -> Message:
            request_bytes = serializer.serialize(message)
            response_bytes = await asyncio.to_thread(post_bytes, url, request_bytes)
            return serializer.deserialize(response_bytes)

        client = Client(adapter, Client.Options())

        shift_response = await client.request(Message({
            '@auth_': {
                'Password': {
                    'username': 'lead-baker',
                    'password': 'opensesame',
                },
            },
        }, {
            'fn.myShift': {},
        }))
        assert shift_response.get_body_target() == 'Ok_'
        assert shift_response.get_body_payload() == {
            'employeeId': 'baker-001',
            'station': 'oven',
            'pastry': 'sesame loaf',
        }

        special_response = await client.request(Message({
            '@auth_': {
                'Password': {
                    'username': 'cashier',
                    'password': 'knockknock',
                },
            },
        }, {
            'fn.approveSpecial': {},
        }))
        assert special_response.get_body_target() == 'ErrorUnauthorized_'
        assert special_response.get_body_payload() == {
            'message!': 'oven station required to approve the special',
        }

        auth_failure_response = await client.request(Message({
            '@auth_': {
                'Password': {
                    'username': 'explode',
                    'password': 'boom',
                },
            },
        }, {
            'fn.myShift': {},
        }))
        assert auth_failure_response.get_body_target() == 'ErrorUnauthenticated_'
        assert auth_failure_response.get_body_payload() == {
            'message!': 'Valid authentication is required.',
        }

        assert get_middleware_events() == [
            {
                'event': 'middleware.identity',
                'function': 'fn.myShift',
                'employeeId': 'baker-001',
                'station': 'oven',
            },
            {
                'event': 'middleware.identity',
                'function': 'fn.approveSpecial',
                'employeeId': 'cashier-002',
                'station': 'counter',
            },
        ]
    finally:
        stop_server(server, thread)


def test_simple_auth_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
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


def post_bytes(url: str, request_bytes: bytes) -> bytes:
    request = urllib.request.Request(
        url,
        data=request_bytes,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(request) as response:
        return response.read()
```
