# py-select

Minimal Python Telepact example that shows all three select targets in one request:

- `->` keeps only the `package` and `latestEvent` result fields
- `struct.Package` keeps only the `trackingId` field
- `union.DeliveryEvent` keeps only the `location` field on the `Dropoff` tag

Browse the files:

- [`api/select.telepact.yaml`](#api-select-telepact-yaml) - Telepact schema
- [`server.py`](#server-py) - server implementation
- [`test_example.py`](#test-example-py) - example test
- [`test_support.py`](#test-support-py) - test helpers
- [`Makefile`](#makefile) - local run target

Run it:

```bash
make run
```

The request uses the runtime-supported `@select_` shape:

```json
[
  {
    "@select_": {
      "->": {
        "Ok_": ["package", "latestEvent"]
      },
      "struct.Package": ["trackingId"],
      "union.DeliveryEvent": {
        "Dropoff": ["location"]
      }
    }
  },
  {
    "fn.trackPackage": {}
  }
]
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

#### api/select.telepact.yaml

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

- struct.Package:
    trackingId: "string"
    recipient: "string"
    city: "string"
- union.DeliveryEvent:
    - Dropoff:
        location: "string"
        signedBy: "string"
    - Locker:
        lockerCode: "string"
        pickupBy: "string"
- fn.trackPackage: {}
  ->:
    - Ok_:
        package: "struct.Package"
        latestEvent: "union.DeliveryEvent"
        note: "string"
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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


async def track_package(_function_name: str, _request_message: Message) -> Message:
    return Message({}, {
        'Ok_': {
            'package': {
                'trackingId': 'PKG-42',
                'recipient': 'Ada Lovelace',
                'city': 'London',
            },
            'latestEvent': {
                'Dropoff': {
                    'location': 'Front desk',
                    'signedBy': 'M. Singh',
                },
            },
            'note': 'Left with building reception.',
        },
    })


function_router = FunctionRouter({'fn.trackPackage': track_package})
telepact_server = Server(schema, function_router, options)


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

        def log_message(self, format: str, *args: object) -> None:
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


def test_select_example_runs_end_to_end() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'
        full_payload = post_json(url, [
            {},
            {
                'fn.trackPackage': {},
            },
        ])
        selected_payload = post_json(url, [
            {
                '@select_': {
                    '->': {
                        'Ok_': ['package', 'latestEvent'],
                    },
                    'struct.Package': ['trackingId'],
                    'union.DeliveryEvent': {
                        'Dropoff': ['location'],
                    },
                },
            },
            {
                'fn.trackPackage': {},
            },
        ])

        assert full_payload == [
            {},
            {
                'Ok_': {
                    'package': {
                        'trackingId': 'PKG-42',
                        'recipient': 'Ada Lovelace',
                        'city': 'London',
                    },
                    'latestEvent': {
                        'Dropoff': {
                            'location': 'Front desk',
                            'signedBy': 'M. Singh',
                        },
                    },
                    'note': 'Left with building reception.',
                },
            },
        ]
        assert selected_payload == [
            {},
            {
                'Ok_': {
                    'package': {
                        'trackingId': 'PKG-42',
                    },
                    'latestEvent': {
                        'Dropoff': {
                            'location': 'Front desk',
                        },
                    },
                },
            },
        ]
        assert selected_payload != full_payload
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
