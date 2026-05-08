# py-binary

Minimal Python Telepact example that verifies binary negotiation.

Browse the files:

- [`api/binary.telepact.yaml`](#api-binary-telepact-yaml) - Telepact schema
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
	@set -euo pipefail; $(MAKE) -C ../../lib/py; rm -rf .venv; uv venv --python python3.11 .venv; uv pip install --python $(PYTHON) pytest ../../lib/py/dist/*.tar.gz; $(PYTHON) -m pytest -q
```

### api/

#### api/binary.telepact.yaml

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

- fn.getNumbers:
    limit: "integer"
  ->:
    - Ok_:
        values: ["integer"]
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

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles


async def get_numbers(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    limit = argument['limit']
    return Message({}, {
        'Ok_': {
            'values': list(range(1, limit + 1)),
        },
    })


def build_telepact_server() -> Server:
    files = TelepactSchemaFiles('api')
    schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
    options = Server.Options()
    options.auth_required = False
    function_router = FunctionRouter({'fn.getNumbers': get_numbers})
    return Server(schema, function_router, options)
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

from telepact import Client, Message, Serializer

from server import build_telepact_server


async def run_example() -> None:
    telepact_server = build_telepact_server()
    saw_binary_response = False

    async def adapter(message: Message, serializer: Serializer) -> Message:
        nonlocal saw_binary_response
        request_bytes = serializer.serialize(message)
        response = await telepact_server.process(request_bytes)
        if '@bin_' in response.headers:
            saw_binary_response = True
        return serializer.deserialize(response.bytes)

    options = Client.Options()
    options.use_binary = True
    options.always_send_json = False
    client = Client(adapter, options)

    for _ in range(2):
        response = await client.request(Message({}, {'fn.getNumbers': {'limit': 3}}))
        assert response.body['Ok_']['values'] == [1, 2, 3]

    assert saw_binary_response, 'expected at least one binary response'


def test_binary_example_runs_end_to_end() -> None:
    asyncio.run(run_example())
```
