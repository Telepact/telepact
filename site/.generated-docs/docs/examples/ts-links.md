# ts-links

Minimal TypeScript Telepact example that returns a prepopulated function-type link.

Browse the files:

- [`api/links.telepact.yaml`](#api-links-telepact-yaml) - Telepact schema
- [`server.ts`](#server-ts) - server implementation
- [`test_example.ts`](#test-example-ts) - example test
- [`test_support.ts`](#test-support-ts) - test helpers
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

### package.json

```json
{
  "name": "telepact-example-ts-links",
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

async function createIssueLink(functionName: string, requestMessage: Message): Promise<Message> {
    const argument = requestMessage.body[functionName] as Record<string, string>;
    const title = argument['title'];
    return new Message({}, {
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
    });
}

async function getFollowUp(functionName: string, requestMessage: Message): Promise<Message> {
    const argument = requestMessage.body[functionName] as Record<string, string>;
    const followUpId = argument['id'];
    return new Message({}, {
        'Ok_': {
            'summary': `Followed up on ${followUpId}`,
        },
    });
}

const functionRouter = new FunctionRouter({
    'fn.createIssueLink': createIssueLink,
    'fn.getFollowUp': getFollowUp,
});
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

const INDEX_MESSAGE_BODY = 1;

test('links example runs end to end', async () => {
    const server = createHttpServer();
    await runServer(server);
    try {
        const address = server.address() as AddressInfo;
        const url = `http://127.0.0.1:${address.port}/api/telepact`;
        const payload = await postJson(url, [
            {},
            {
                'fn.createIssueLink': {
                    'title': 'Ship docs',
                },
            },
        ]);

        const nextCall = payload[INDEX_MESSAGE_BODY]['Ok_']['next!'];
        const followUpPayload = await postJson(url, [
            {},
            nextCall,
        ]);

        assert.equal(followUpPayload[INDEX_MESSAGE_BODY]['Ok_']['summary'], 'Followed up on follow-up-1');
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
