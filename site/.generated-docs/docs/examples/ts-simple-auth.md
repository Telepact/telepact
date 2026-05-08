# ts-simple-auth

Minimal TypeScript Telepact client example that starts a minimum Python bakery
server and shows a simple auth flow with hard-coded credentials.

It demonstrates the same auth boundary as the Python example:

- `on_auth` maps a hard-coded username/password from `@auth_` into normalized
  identity headers, and throws if authentication fails
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
- [`test_example.ts`](#test-example-ts) - TypeScript client exercising the auth flows
- [`test_support.ts`](#test-support-ts) - Python server process and transport helpers
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

.PHONY: run clean

run:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/py; \
	$(MAKE) -C ../../lib/ts; \
	rm -rf .venv node_modules dist telepact.tgz; \
	uv venv --python python3.11 .venv; \
	uv pip install --python $(PYTHON) ../../lib/py/dist/*.tar.gz; \
	cp ../../lib/ts/dist-tgz/*.tgz telepact.tgz; \
	npm install --ignore-scripts --no-package-lock; \
	npm run build; \
	npm test

clean:
	@rm -rf .venv dist node_modules telepact.tgz
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

### package.json

```json
{
  "name": "telepact-example-ts-simple-auth",
  "private": true,
  "scripts": {
    "build": "tsc",
    "test": "node --test dist/test_example.js"
  },
  "dependencies": {
    "telepact": "file:telepact.tgz"
  },
  "devDependencies": {
    "@types/node": "^25.0.3",
    "typescript": "^5.9.2"
  },
  "type": "module"
}
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

### test_example.ts

```typescript
//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import assert from 'node:assert/strict';
import test from 'node:test';
import { Client, ClientOptions, Message, Serializer } from 'telepact';
import { postBytes, startPythonServer, stopPythonServer, waitForLog } from './test_support.js';

test('simple auth example runs end to end against the python server', async () => {
    const server = await startPythonServer();
    try {
        const url = `http://127.0.0.1:${server.port}/api/telepact`;
        const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
            const requestBytes = serializer.serialize(message);
            const responseBytes = await postBytes(url, requestBytes);
            return serializer.deserialize(responseBytes);
        };
        const client = new Client(adapter, new ClientOptions());

        const shiftResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'lead-baker',
                    'password': 'opensesame',
                },
            },
        }, {
            'fn.myShift': {},
        }));
        assert.equal(shiftResponse.getBodyTarget(), 'Ok_');
        assert.deepEqual(shiftResponse.getBodyPayload(), {
            'employeeId': 'baker-001',
            'station': 'oven',
            'pastry': 'sesame loaf',
        });

        const specialResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'cashier',
                    'password': 'knockknock',
                },
            },
        }, {
            'fn.approveSpecial': {},
        }));
        assert.equal(specialResponse.getBodyTarget(), 'ErrorUnauthorized_');
        assert.deepEqual(specialResponse.getBodyPayload(), {
            'message!': 'oven station required to approve the special',
        });

        const authFailureResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'explode',
                    'password': 'boom',
                },
            },
        }, {
            'fn.myShift': {},
        }));
        assert.equal(authFailureResponse.getBodyTarget(), 'ErrorUnauthenticated_');
        assert.deepEqual(authFailureResponse.getBodyPayload(), {
            'message!': 'Valid authentication is required.',
        });

        await waitForLog(server, '"employeeId": "baker-001", "event": "middleware.identity", "function": "fn.myShift", "station": "oven"');
        await waitForLog(server, '"employeeId": "cashier-002", "event": "middleware.identity", "function": "fn.approveSpecial", "station": "counter"');
    } finally {
        await stopPythonServer(server);
    }
});
```

### test_support.ts

```typescript
//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { ChildProcessWithoutNullStreams, spawn } from 'node:child_process';
import { once } from 'node:events';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export type PythonServer = {
    process: ChildProcessWithoutNullStreams;
    port: number;
    stdout(): string;
    stderr(): string;
};

function delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function startPythonServer(): Promise<PythonServer> {
    const here = path.dirname(fileURLToPath(import.meta.url));
    const cwd = path.resolve(here, '..');
    const python = path.join(cwd, '.venv', 'bin', 'python');
    const script = path.join(cwd, 'server.py');
    const child = spawn(python, ['-u', script, '--port', '0'], { cwd }) as ChildProcessWithoutNullStreams;

    let stdout = '';
    let stderr = '';

    child.stdout.setEncoding('utf8');
    child.stdout.on('data', (chunk: string) => {
        stdout += chunk;
    });

    child.stderr.setEncoding('utf8');
    child.stderr.on('data', (chunk: string) => {
        stderr += chunk;
    });

    const startedAt = Date.now();
    while (Date.now() - startedAt < 10000) {
        const ready = stdout.match(/READY (\d+)/);
        if (ready) {
            return {
                process: child,
                port: Number(ready[1]),
                stdout: () => stdout,
                stderr: () => stderr,
            };
        }
        if (child.exitCode !== null) {
            throw new Error(`python server exited early: ${stderr || stdout}`);
        }
        await delay(50);
    }

    child.kill('SIGTERM');
    await once(child, 'exit');
    throw new Error(`timed out waiting for python server: ${stderr || stdout}`);
}

export async function stopPythonServer(server: PythonServer): Promise<void> {
    if (server.process.exitCode !== null) {
        return;
    }

    server.process.kill('SIGTERM');
    await once(server.process, 'exit');
}

export async function waitForLog(server: PythonServer, text: string): Promise<void> {
    const startedAt = Date.now();
    while (Date.now() - startedAt < 10000) {
        if (server.stdout().includes(text)) {
            return;
        }
        if (server.process.exitCode !== null) {
            throw new Error(`python server exited while waiting for log: ${server.stderr() || server.stdout()}`);
        }
        await delay(50);
    }

    throw new Error(`timed out waiting for log ${JSON.stringify(text)} in ${server.stdout()}`);
}

export async function postBytes(url: string, requestBytes: Uint8Array): Promise<Uint8Array> {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: Buffer.from(requestBytes),
    });
    return new Uint8Array(await response.arrayBuffer());
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": [
      "ES2022",
      "DOM"
    ],
    "rootDir": ".",
    "outDir": "dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": [
    "*.ts"
  ]
}
```
