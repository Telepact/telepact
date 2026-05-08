# ts-websocket

Minimal TypeScript Telepact example over WebSocket request/reply.

Browse the files:

- [`api/greet.telepact.yaml`](#api-greet-telepact-yaml) - Telepact schema
- [`server.ts`](#server-ts) - server implementation
- [`test_example.ts`](#test-example-ts) - example test
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

.PHONY: run clean

run:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/ts; \
	rm -rf node_modules dist telepact.tgz; \
	cp ../../lib/ts/dist-tgz/*.tgz telepact.tgz; \
	npm install --ignore-scripts --no-package-lock; \
	npm run build; \
	npm test

clean:
	@rm -rf dist node_modules telepact.tgz
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

### package.json

```json
{
  "name": "telepact-example-ts-websocket",
  "private": true,
  "scripts": {
    "build": "tsc",
    "test": "node --test dist/test_example.js"
  },
  "dependencies": {
    "telepact": "file:telepact.tgz",
    "ws": "^8.20.0"
  },
  "devDependencies": {
    "@types/node": "^25.0.3",
    "typescript": "^5.9.2",
    "@types/ws": "^8.18.1"
  },
  "type": "module"
}
```

### server.ts

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

import * as fs from 'node:fs';
import * as path from 'node:path';
import { once } from 'node:events';
import { FunctionRouter, Message, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';
import { WebSocket, WebSocketServer } from 'ws';
import type { RawData } from 'ws';

const files = new TelepactSchemaFiles('api', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
const options = new ServerOptions();
options.authRequired = false;

async function greet(functionName: string, requestMessage: Message): Promise<Message> {
    const argument = requestMessage.body[functionName] as Record<string, string>;
    const subject = argument['subject'];
    return new Message({}, {
        'Ok_': {
            'message': `Hello ${subject} from WebSocket!`,
        },
    });
}

const functionRouter = new FunctionRouter({ 'fn.greet': greet });
const telepactServer = new Server(schema, functionRouter, options);

function rawDataToBytes(data: RawData): Uint8Array {
    if (typeof data === 'string') {
        return new TextEncoder().encode(data);
    }
    if (data instanceof ArrayBuffer) {
        return new Uint8Array(data);
    }
    if (Array.isArray(data)) {
        return new Uint8Array(Buffer.concat(data));
    }
    return new Uint8Array(data);
}

export async function createWebSocketServer(host = '127.0.0.1', port = 0): Promise<WebSocketServer> {
    const server = new WebSocketServer({ host, port, path: '/ws/telepact' });
    server.on('connection', (websocket: WebSocket) => {
        websocket.on('message', (data: RawData, isBinary: boolean) => {
            void (async () => {
                const response = await telepactServer.process(rawDataToBytes(data));
                if (isBinary) {
                    websocket.send(response.bytes);
                    return;
                }
                websocket.send(Buffer.from(response.bytes).toString('utf-8'));
            })().catch((error: unknown) => {
                websocket.close(1011, String(error));
            });
        });
    });
    await once(server, 'listening');
    return server;
}
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
import { once } from 'node:events';
import { AddressInfo } from 'node:net';
import test from 'node:test';
import { WebSocket } from 'ws';
import { createWebSocketServer } from './server.js';

test('websocket example runs end to end', async () => {
    const server = await createWebSocketServer();
    try {
        const address = server.address() as AddressInfo;
        const websocket = new WebSocket(`ws://127.0.0.1:${address.port}/ws/telepact`);
        await once(websocket, 'open');
        websocket.send(JSON.stringify([{}, { 'fn.greet': { 'subject': 'Telepact' } }]));
        const [response] = await once(websocket, 'message');
        const responseText = typeof response === 'string' ? response : response.toString('utf-8');
        assert.match(responseText, /Hello Telepact from WebSocket!/);
        websocket.close();
        await once(websocket, 'close');
    } finally {
        await new Promise<void>((resolve, reject) => {
            server.close((error?: Error) => {
                if (error) {
                    reject(error);
                    return;
                }
                resolve();
            });
        });
    }
});
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
