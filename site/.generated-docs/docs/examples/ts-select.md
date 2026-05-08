# ts-select

Minimal TypeScript Telepact example that shows all three select targets in one request:

- `->` keeps only the `package` and `latestEvent` result fields
- `struct.Package` keeps only the `trackingId` field
- `union.DeliveryEvent` keeps only the `location` field on the `Dropoff` tag

Browse the files:

- [`api/select.telepact.yaml`](#api-select-telepact-yaml) - Telepact schema
- [`server.ts`](#server-ts) - server implementation
- [`test_example.ts`](#test-example-ts) - example test
- [`test_support.ts`](#test-support-ts) - test helpers
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

### package.json

```json
{
  "name": "telepact-example-ts-select",
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

import { createServer, IncomingMessage, Server as HttpServer, ServerResponse } from 'node:http';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { FunctionRouter, Message, Response, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

const files = new TelepactSchemaFiles('api', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
const options = new ServerOptions();
options.authRequired = false;

async function trackPackage(_functionName: string, _requestMessage: Message): Promise<Message> {
    return new Message({}, {
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
    });
}

const functionRouter = new FunctionRouter({ 'fn.trackPackage': trackPackage });
const telepactServer = new Server(schema, functionRouter, options);

function readRequestBytes(request: IncomingMessage): Promise<Uint8Array> {
    return new Promise((resolve, reject) => {
        const chunks: Buffer[] = [];
        request.on('data', (chunk) => {
            chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
        });
        request.on('end', () => resolve(new Uint8Array(Buffer.concat(chunks))));
        request.on('error', reject);
    });
}

function writeTelepactResponse(responseWriter: ServerResponse, response: Response): void {
    responseWriter.statusCode = 200;
    responseWriter.setHeader('Content-Type', '@bin_' in response.headers ? 'application/octet-stream' : 'application/json');
    responseWriter.end(Buffer.from(response.bytes));
}

export function createHttpServer(): HttpServer {
    return createServer((request, responseWriter) => {
        void (async () => {
            if (request.method !== 'POST' || request.url !== '/api/telepact') {
                responseWriter.statusCode = 404;
                responseWriter.end();
                return;
            }

            const requestBytes = await readRequestBytes(request);
            const response = await telepactServer.process(requestBytes);
            writeTelepactResponse(responseWriter, response);
        })().catch((error: unknown) => {
            responseWriter.statusCode = 500;
            responseWriter.end(String(error));
        });
    });
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
import test from 'node:test';
import { AddressInfo } from 'node:net';
import { createHttpServer } from './server.js';
import { postJson, runServer, stopServer } from './test_support.js';

test('select example runs end to end', async () => {
    const server = createHttpServer();
    await runServer(server);
    try {
        const address = server.address() as AddressInfo;
        const url = `http://127.0.0.1:${address.port}/api/telepact`;
        const fullPayload = await postJson(url, [
            {},
            {
                'fn.trackPackage': {},
            },
        ]);
        const selectedPayload = await postJson(url, [
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
        ]);

        assert.deepEqual(fullPayload, [
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
        ]);
        assert.deepEqual(selectedPayload, [
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
        ]);
        assert.notDeepEqual(selectedPayload, fullPayload);
    } finally {
        await stopServer(server);
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

import { Server as HttpServer } from 'node:http';

export async function runServer(server: HttpServer): Promise<void> {
    await new Promise<void>((resolve) => {
        server.listen(0, '127.0.0.1', () => resolve());
    });
}

export async function stopServer(server: HttpServer): Promise<void> {
    await new Promise<void>((resolve, reject) => {
        server.close((error) => {
            if (error) {
                reject(error);
                return;
            }
            resolve();
        });
    });
}

export async function postJson(url: string, body: unknown, headers: Record<string, string> = {}): Promise<any> {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...headers,
        },
        body: JSON.stringify(body),
    });
    return await response.json();
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
    "*.ts",
    "gen/**/*.ts"
  ]
}
```
