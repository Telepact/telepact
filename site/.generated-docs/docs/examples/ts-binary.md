# ts-binary

Minimal TypeScript Telepact example that verifies binary negotiation.

Browse the files:

- [`api/binary.telepact.yaml`](#api-binary-telepact-yaml) - Telepact schema
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

### package.json

```json
{
  "name": "telepact-example-ts-binary",
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

import * as fs from 'node:fs';
import * as path from 'node:path';
import { FunctionRouter, Message, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

async function getNumbers(functionName: string, requestMessage: Message): Promise<Message> {
    const argument = requestMessage.body[functionName] as Record<string, number>;
    const limit = argument['limit'];
    return new Message({}, {
        'Ok_': {
            'values': Array.from({ length: limit }, (_value, index) => index + 1),
        },
    });
}

export function buildTelepactServer(): Server {
    const files = new TelepactSchemaFiles('api', fs, path);
    const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
    const options = new ServerOptions();
    options.authRequired = false;
    const functionRouter = new FunctionRouter({ 'fn.getNumbers': getNumbers });
    return new Server(schema, functionRouter, options);
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
import { Client, ClientOptions, Message, Serializer } from 'telepact';
import { buildTelepactServer } from './server.js';

test('binary example runs end to end', async () => {
    const telepactServer = buildTelepactServer();
    let sawBinaryResponse = false;

    const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
        const requestBytes = serializer.serialize(message);
        const response = await telepactServer.process(requestBytes);
        if ('@bin_' in response.headers) {
            sawBinaryResponse = true;
        }
        return serializer.deserialize(response.bytes);
    };

    const options = new ClientOptions();
    options.useBinary = true;
    options.alwaysSendJson = false;
    const client = new Client(adapter, options);

    for (let index = 0; index < 2; index += 1) {
        const response = await client.request(new Message({}, { 'fn.getNumbers': { 'limit': 3 } }));
        assert.deepEqual(response.body['Ok_']['values'], [1, 2, 3]);
    }

    assert.equal(sawBinaryResponse, true, 'expected at least one binary response');
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
    "*.ts",
    "gen/**/*.ts"
  ]
}
```
