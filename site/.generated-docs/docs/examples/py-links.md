# py-links

Minimal Python Telepact example that returns a prepopulated function-type link.

Browse the files:

- [`api/links.telepact.yaml`](#api-links-telepact-yaml) - Telepact schema
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

#### api/links.telepact.yaml

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

- ///: A structure that can point to a follow-up function call.
  struct.Todo:
    title: "string"
- ///: Fetch the next step after creating a todo.
  fn.getFollowUp:
    id: "string"
  ->:
    - Ok_:
        summary: "string"
- ///: Create a todo and return a link to the next step.
  fn.createIssueLink:
    title: "string"
  ->:
    - Ok_:
        todo: "struct.Todo"
        next!: "fn.getFollowUp"
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


async def create_issue_link(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    title = argument['title']
    return Message({}, {
        'Ok_': {
            'todo': {
                'title': title,
            },
            'next!': {
                'fn.getFollowUp': {
                    'id': 'follow-up-1',
                },
            },
        },
    })


async def get_follow_up(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    follow_up_id = argument['id']
    return Message({}, {
        'Ok_': {
            'summary': f'Followed up on {follow_up_id}',
        },
    })


function_router = FunctionRouter({
    'fn.createIssueLink': create_issue_link,
    'fn.getFollowUp': get_follow_up,
})
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


INDEX_MESSAGE_BODY = 1


def test_links_example_runs_end_to_end() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'
        payload = post_json(url, [
            {},
            {
                'fn.createIssueLink': {
                    'title': 'Ship docs',
                },
            },
        ])

        next_call = payload[INDEX_MESSAGE_BODY]['Ok_']['next!']
        follow_up_payload = post_json(url, [
            {},
            next_call,
        ])

        assert follow_up_payload[INDEX_MESSAGE_BODY]['Ok_']['summary'] == 'Followed up on follow-up-1'
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
