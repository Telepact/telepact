# py-websocket

Minimal Python Telepact example over WebSocket request/reply.

Browse the files:

- [`api/greet.telepact.yaml`](#api-greet-telepact-yaml) - Telepact schema
- [`server.py`](#server-py) - server implementation
- [`test_example.py`](#test-example-py) - example test
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
	@set -euo pipefail; $(MAKE) -C ../../lib/py; rm -rf .venv; uv venv --python python3.11 .venv; uv pip install --python $(PYTHON) pytest websockets==16.0.0 ../../lib/py/dist/*.tar.gz; $(PYTHON) -m pytest -q
```

### api/

#### api/greet.telepact.yaml

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

- fn.greet:
    subject: "string"
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

import websockets

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles

files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


async def greet(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    subject = argument['subject']
    return Message({}, {
        'Ok_': {
            'message': f'Hello {subject} from WebSocket!',
        },
    })


function_router = FunctionRouter({'fn.greet': greet})
telepact_server = Server(schema, function_router, options)


async def telepact_websocket(websocket: websockets.ServerConnection) -> None:
    request = getattr(websocket, 'request', None)
    if request is not None and getattr(request, 'path', '/ws/telepact') != '/ws/telepact':
        await websocket.close(code=1008, reason='unexpected path')
        return

    async for request_bytes in websocket:
        is_text = isinstance(request_bytes, str)
        if is_text:
            request_bytes = request_bytes.encode('utf-8')

        response = await telepact_server.process(request_bytes)
        if is_text:
            await websocket.send(response.bytes.decode('utf-8'))
        else:
            await websocket.send(response.bytes)


async def create_websocket_server(host: str = '127.0.0.1', port: int = 0):
    return await websockets.serve(telepact_websocket, host, port)
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

import asyncio
import json

import websockets

from server import create_websocket_server


async def run_example() -> None:
    server = await create_websocket_server()
    try:
        assert server.sockets is not None
        port = server.sockets[0].getsockname()[1]
        async with websockets.connect(f'ws://127.0.0.1:{port}/ws/telepact') as websocket:
            await websocket.send(json.dumps([{}, {'fn.greet': {'subject': 'Telepact'}}]))
            response = await websocket.recv()
            assert 'Hello Telepact from WebSocket!' in response
    finally:
        server.close()
        await server.wait_closed()


def test_websocket_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
```
