# ts-http-cookie-auth

Minimal TypeScript Telepact example that shows Telepact's recommended browser auth
flow:

- define a session credential in `union.Auth_`
- read the browser cookie at the HTTP boundary
- translate it into `@auth_`
- normalize it in `on_auth`

Browse the files:

- [`api/auth.telepact.yaml`](#api-auth-telepact-yaml) - Telepact schema
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

### package.json

```json
{
  "name": "telepact-example-ts-http-cookie-auth",
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

const VALID_SESSION = 'demo-session';

const files = new TelepactSchemaFiles('api', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
const options = new ServerOptions();
options.authRequired = false;
options.onAuth = async (headers: Record<string, any>): Promise<Record<string, any>> => {
    const auth = headers['@auth_'];
    const session = typeof auth === 'object' && auth !== null ? auth['Session'] : undefined;
    if (typeof session === 'object' && session !== null && session['token'] === VALID_SESSION) {
        return { '@userId': 'user-123' };
    }
    return {};
};

async function me(_functionName: string, requestMessage: Message): Promise<Message> {
    if (requestMessage.headers['@userId'] !== 'user-123') {
        return new Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'missing or invalid session cookie',
            },
        });
    }

    return new Message({}, {
        'Ok_': {
            'userId': 'user-123',
        },
    });
}

const functionRouter = new FunctionRouter({ 'fn.me': me });
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

export function readSessionCookie(cookieHeader: string | undefined): string | undefined {
    if (!cookieHeader) {
        return undefined;
    }

    for (const cookiePart of cookieHeader.split(';')) {
        const [name, ...valueParts] = cookiePart.trim().split('=');
        if (name === 'session') {
            return valueParts.join('=');
        }
    }

    return undefined;
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
            const sessionToken = readSessionCookie(request.headers.cookie);
            const response = await telepactServer.process(requestBytes, (headers: Record<string, any>) => {
                if (sessionToken !== undefined) {
                    headers['@auth_'] = { 'Session': { 'token': sessionToken } };
                }
            });
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

test('cookie auth example runs end to end', async () => {
    const server = createHttpServer();
    await runServer(server);
    try {
        const address = server.address() as AddressInfo;
        const url = `http://127.0.0.1:${address.port}/api/telepact`;

        const unauthenticated = await postJson(url, [
            {},
            {
                'fn.me': {},
            },
        ]);
        const unauthenticatedBody = unauthenticated[1] as Record<string, any>;
        assert.equal('Ok_' in unauthenticatedBody, false);
        assert.equal(Object.keys(unauthenticatedBody).some((key) => key.toLowerCase().includes('error')), true);

        const authenticated = await postJson(url, [
            {},
            {
                'fn.me': {},
            },
        ], { 'Cookie': 'session=demo-session' });
        assert.equal(authenticated[1]['Ok_']['userId'], 'user-123');
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
