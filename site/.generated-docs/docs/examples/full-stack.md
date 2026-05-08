# full-stack

A runnable Telepact example with a Python backend and a TypeScript browser
frontend.

This example is intentionally broader than the minimal demos. It demonstrates the
production-boundary concerns from
[`doc/operate/production-guide.md`](../concepts.md#operating-boundary-guide):

- HTTP-only session cookies stay at the transport boundary and are translated into
  `@auth_`
- `on_auth` normalizes identity into internal headers such as `@userId` and `@role`
- Telepact hooks emit request IDs, per-function metrics, and structured events
  without logging whole request payloads
- authorization stays in the handler that owns the admin-only business rule
- unexpected bugs still return `ErrorUnknown_` with a client-visible `caseId`
- `schema-baseline/` gives you a checked-in schema snapshot to compare during
  contract changes

## Layout

- [`api/dashboard.telepact.yaml`](#api-dashboard-telepact-yaml) - current
  checked-in Telepact schema
- [`schema-baseline/dashboard.telepact.yaml`](#schema-baseline-dashboard-telepact-yaml)
  - baseline schema snapshot for compatibility checks
- [`server/app.py`](#server-app-py) - Python HTTP adapter that serves the app
  and Telepact endpoint
- [`server/telepact_app.py`](#server-telepact-app-py) - Telepact server hooks,
  auth normalization, metrics, and handlers
- [`client/src/main.ts`](#client-src-main-ts) - Vite-powered TypeScript browser
  UI entry point
- [`client/src/app.html`](#client-src-app-html) - browser UI markup
- [`client/tests/e2e.spec.ts`](#client-tests-e2e-spec-ts) - Playwright end-to-end
  coverage

## Run it

```bash
make run
```

That target rebuilds the local Telepact Python and TypeScript packages, installs
browser dependencies, builds the browser app, and runs the Playwright end-to-end
suite against the Python server.

## Inspect schema compatibility

If you already have the `telepact` CLI installed, compare the current schema with
its checked-in baseline:

```bash
telepact compare --old-schema-dir ./schema-baseline --new-schema-dir ./api
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
PYTHON := server/.venv/bin/python

.PHONY: run clean

run:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/py; \
	$(MAKE) -C ../../lib/ts; \
	rm -rf server/.venv client/node_modules client/dist client/playwright-report client/test-results client/telepact.tgz; \
	uv venv --python python3.11 server/.venv; \
	uv pip install --python $(PYTHON) ../../lib/py/dist/*.tar.gz; \
	cp ../../lib/ts/dist-tgz/*.tgz client/telepact.tgz; \
	(cd client && npm install --ignore-scripts --no-package-lock); \
	(cd client && npm run build); \
	(cd client && npx playwright install chromium); \
	(cd client && npm test)

clean:
	@rm -rf server/.venv client/node_modules client/dist client/playwright-report client/test-results client/telepact.tgz
```

### api/

#### api/dashboard.telepact.yaml

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

- ///: Browser session credentials translated from HTTP cookies.
  union.Auth_:
    - Session:
        token: "string"
- ///: Return the normalized caller identity after transport auth extraction.
  fn.me: {}
  ->:
    - Ok_:
        userId: "string"
        role: "string"
        displayName: "string"
- ///: Return an admin-only operational summary.
  fn.adminReport: {}
  ->:
    - Ok_:
        requestCount: "integer"
        unauthorizedCount: "integer"
        unknownErrorCount: "integer"
        lastRequestId: "string?"
- ///: Force an unexpected server bug to demonstrate ErrorUnknown_ handling.
  fn.triggerFailure: {}
  ->:
    - Ok_:
        message: "string"
```

### client/

#### client/index.html

```html
<!--|                                                                            |-->
<!--|  Copyright The Telepact Authors                                            |-->
<!--|                                                                            |-->
<!--|  Licensed under the Apache License, Version 2.0 (the "License");           |-->
<!--|  you may not use this file except in compliance with the License.          |-->
<!--|  You may obtain a copy of the License at                                   |-->
<!--|                                                                            |-->
<!--|  https://www.apache.org/licenses/LICENSE-2.0                               |-->
<!--|                                                                            |-->
<!--|  Unless required by applicable law or agreed to in writing, software       |-->
<!--|  distributed under the License is distributed on an "AS IS" BASIS,         |-->
<!--|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  |-->
<!--|  See the License for the specific language governing permissions and       |-->
<!--|  limitations under the License.                                            |-->
<!--|                                                                            |-->

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Telepact full-stack example</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

#### client/package.json

```json
{
  "name": "telepact-example-full-stack-client",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "build": "tsc && vite build",
    "test": "playwright test"
  },
  "dependencies": {
    "telepact": "file:telepact.tgz"
  },
  "devDependencies": {
    "@playwright/test": "^1.55.1",
    "typescript": "^5.9.3",
    "vite": "^8.0.8"
  }
}
```

#### client/playwright.config.ts

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

import { defineConfig } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const serverPython = path.resolve(__dirname, '../server/.venv/bin/python');
const serverEntrypoint = path.resolve(__dirname, '../server/app.py');
const port = 4173;
const TEST_TIMEOUT_MS = 60 * 1000;

export default defineConfig({
  testDir: './tests',
  timeout: TEST_TIMEOUT_MS,
  use: {
    baseURL: `http://127.0.0.1:${port}`,
  },
  webServer: {
    command: `${serverPython} ${serverEntrypoint} --host 127.0.0.1 --port ${port}`,
    port,
    reuseExistingServer: !process.env.CI,
  },
});
```

#### client/src/app.html

```html
<!--|                                                                            |-->
<!--|  Copyright The Telepact Authors                                            |-->
<!--|                                                                            |-->
<!--|  Licensed under the Apache License, Version 2.0 (the "License");           |-->
<!--|  you may not use this file except in compliance with the License.          |-->
<!--|  You may obtain a copy of the License at                                   |-->
<!--|                                                                            |-->
<!--|  https://www.apache.org/licenses/LICENSE-2.0                               |-->
<!--|                                                                            |-->
<!--|  Unless required by applicable law or agreed to in writing, software       |-->
<!--|  distributed under the License is distributed on an "AS IS" BASIS,         |-->
<!--|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  |-->
<!--|  See the License for the specific language governing permissions and       |-->
<!--|  limitations under the License.                                            |-->
<!--|                                                                            |-->

<section class="hero">
  <span class="pill">Python backend + TypeScript browser frontend</span>
  <h1>Telepact full-stack production-boundary demo</h1>
  <p>
    This browser app talks to a Python Telepact server over HTTP. The server extracts a session
    cookie into <code>@auth_</code>, normalizes identity with <code>on_auth</code>, emits
    Telepact-aware metrics and logs, attaches request IDs, keeps auth decisions near the handlers,
    and surfaces unexpected failures as <code>ErrorUnknown_</code> with a <code>caseId</code>.
  </p>
</section>
<section class="grid">
  <div class="stack">
    <div class="card">
      <h2>Session controls</h2>
      <div class="actions">
        <button id="sign-in-user">Sign in as reader</button>
        <button id="sign-in-admin">Sign in as admin</button>
        <button id="logout" class="secondary">Sign out</button>
      </div>
      <div class="status-line">
        <span class="pill" id="session-pill">session: anonymous</span>
        <span class="pill" id="health-pill">server: loading</span>
      </div>
    </div>
    <div class="card">
      <h2>Telepact functions</h2>
      <div class="actions">
        <button id="call-me">Who am I?</button>
        <button id="call-admin">Load admin report</button>
        <button id="call-failure" class="secondary">Trigger server bug</button>
      </div>
      <div class="status-line">
        <span class="pill" id="request-pill">request id: pending</span>
        <span class="pill" id="outcome-pill">outcome: none</span>
      </div>
    </div>
    <div class="card">
      <h2>What this example demonstrates</h2>
      <ul class="note-list">
        <li>transport-specific cookie extraction stays at the HTTP edge</li>
        <li><code>on_auth</code> normalizes identity into internal Telepact headers</li>
        <li>request IDs, per-function metrics, and structured events come from Telepact hooks</li>
        <li><code>ErrorUnauthorized_</code> stays close to the admin-only business rule</li>
        <li>
          <code>ErrorUnknown_</code> still keeps the wire response generic while exposing a
          <code>caseId</code>
        </li>
        <li>
          schema compatibility is tracked with the checked-in <code>schema-baseline/</code> snapshot
        </li>
      </ul>
    </div>
  </div>
  <div class="stack">
    <div class="card">
      <h2>Latest Telepact response</h2>
      <div class="output"><pre id="response-output">Waiting for a browser action…</pre></div>
    </div>
    <div class="card">
      <div class="actions" style="justify-content: space-between; align-items: center;">
        <h2 style="margin-bottom: 0;">Operational snapshot</h2>
        <button id="refresh-ops" class="secondary">Refresh ops snapshot</button>
      </div>
      <div class="output"><pre id="ops-output">Loading…</pre></div>
    </div>
  </div>
</section>
```

#### client/src/main.ts

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

import './style.css';
import appHtml from './app.html?raw';
import { Client, ClientOptions, Message, type Serializer } from 'telepact';

type JsonObject = Record<string, unknown>;

type SnapshotResponse = {
  metrics: JsonObject;
  recentEvents: Array<JsonObject>;
};

const app = document.querySelector<HTMLDivElement>('#app');
if (app === null) {
  throw new Error('missing #app root');
}

app.innerHTML = appHtml;

const sessionPill = must<HTMLSpanElement>('#session-pill');
const healthPill = must<HTMLSpanElement>('#health-pill');
const requestPill = must<HTMLSpanElement>('#request-pill');
const outcomePill = must<HTMLSpanElement>('#outcome-pill');
const responseOutput = must<HTMLPreElement>('#response-output');
const opsOutput = must<HTMLPreElement>('#ops-output');
const buttons = Array.from(document.querySelectorAll<HTMLButtonElement>('button'));

let currentSession = 'anonymous';

function must<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (element === null) {
    throw new Error(`missing element: ${selector}`);
  }
  return element;
}

function pretty(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

function setBusy(isBusy: boolean): void {
  for (const button of buttons) {
    button.disabled = isBusy;
  }
}

async function requestTelepact(body: JsonObject): Promise<void> {
  setBusy(true);
  requestPill.textContent = 'request id: waiting for server';

  try {
    let echoedRequestId = 'missing';
    const client = new Client(async (message: Message, serializer: Serializer): Promise<Message> => {
      const requestBytes = serializer.serialize(message);
      const requestBody = new Uint8Array(requestBytes.byteLength);
      requestBody.set(requestBytes);
      const response = await fetch('/api/telepact', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: requestBody.buffer,
      });
      echoedRequestId = response.headers.get('X-Request-ID') ?? 'missing';
      const responseBytes = new Uint8Array(await response.arrayBuffer());
      return serializer.deserialize(responseBytes);
    }, new ClientOptions());

    const response = await client.request(new Message({}, body));
    const outcome = response.getBodyTarget();
    requestPill.textContent = `request id: ${echoedRequestId}`;
    outcomePill.textContent = `outcome: ${outcome}`;
    responseOutput.textContent = pretty({
      requestId: echoedRequestId,
      session: currentSession,
      body: response.body,
    });
  } catch (error: unknown) {
    outcomePill.textContent = 'outcome: transport failure';
    responseOutput.textContent = pretty({
      error: String(error),
    });
  } finally {
    await refreshOpsSnapshot();
    setBusy(false);
  }
}

async function setSession(path: '/session/user' | '/session/admin' | '/session/logout', label: string): Promise<void> {
  setBusy(true);
  try {
    const response = await fetch(path, {
      method: 'POST',
      credentials: 'include',
    });
    const payload = await response.json();
    currentSession = label;
    sessionPill.textContent = `session: ${label}`;
    responseOutput.textContent = pretty(payload);
    outcomePill.textContent = 'outcome: session updated';
    await refreshOpsSnapshot();
  } finally {
    setBusy(false);
  }
}

async function refreshOpsSnapshot(): Promise<void> {
  const response = await fetch('/ops/snapshot', { cache: 'no-store' });
  const snapshot = (await response.json()) as SnapshotResponse;
  opsOutput.textContent = pretty(snapshot);
}

async function refreshHealth(): Promise<void> {
  const response = await fetch('/healthz', { cache: 'no-store' });
  const payload = (await response.json()) as { ok?: boolean };
  healthPill.textContent = payload.ok ? 'server: healthy' : 'server: unavailable';
}

must<HTMLButtonElement>('#sign-in-user').addEventListener('click', async () => {
  await setSession('/session/user', 'reader');
});

must<HTMLButtonElement>('#sign-in-admin').addEventListener('click', async () => {
  await setSession('/session/admin', 'admin');
});

must<HTMLButtonElement>('#logout').addEventListener('click', async () => {
  await setSession('/session/logout', 'anonymous');
});

must<HTMLButtonElement>('#call-me').addEventListener('click', async () => {
  await requestTelepact({ 'fn.me': {} });
});

must<HTMLButtonElement>('#call-admin').addEventListener('click', async () => {
  await requestTelepact({ 'fn.adminReport': {} });
});

must<HTMLButtonElement>('#call-failure').addEventListener('click', async () => {
  await requestTelepact({ 'fn.triggerFailure': {} });
});

must<HTMLButtonElement>('#refresh-ops').addEventListener('click', async () => {
  setBusy(true);
  try {
    await refreshOpsSnapshot();
  } finally {
    setBusy(false);
  }
});

void (async () => {
  await refreshHealth();
  await refreshOpsSnapshot();
})();
```

#### client/src/style.css

```css
/*|                                                                            |*/
/*|  Copyright The Telepact Authors                                            |*/
/*|                                                                            |*/
/*|  Licensed under the Apache License, Version 2.0 (the "License");           |*/
/*|  you may not use this file except in compliance with the License.          |*/
/*|  You may obtain a copy of the License at                                   |*/
/*|                                                                            |*/
/*|  https://www.apache.org/licenses/LICENSE-2.0                               |*/
/*|                                                                            |*/
/*|  Unless required by applicable law or agreed to in writing, software       |*/
/*|  distributed under the License is distributed on an "AS IS" BASIS,         |*/
/*|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  |*/
/*|  See the License for the specific language governing permissions and       |*/
/*|  limitations under the License.                                            |*/
/*|                                                                            |*/

:root {
  color-scheme: light;
  font-family: Inter, system-ui, sans-serif;
  line-height: 1.5;
  font-weight: 400;
  background: #f5f7fb;
  color: #172033;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
}

button {
  cursor: pointer;
  border: 1px solid #2247d5;
  background: #2247d5;
  color: white;
  border-radius: 0.6rem;
  padding: 0.7rem 1rem;
  font: inherit;
}

button.secondary {
  background: white;
  color: #2247d5;
}

button:disabled {
  opacity: 0.65;
  cursor: progress;
}

code,
pre {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

#app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem 3rem;
}

.hero {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.hero p {
  margin: 0;
  max-width: 62rem;
}

.grid {
  display: grid;
  gap: 1rem;
}

@media (min-width: 960px) {
  .grid {
    grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
  }
}

.card {
  background: white;
  border-radius: 1rem;
  padding: 1rem;
  border: 1px solid #dbe2f0;
  box-shadow: 0 18px 45px rgba(23, 32, 51, 0.06);
}

.card h2,
.card h3 {
  margin-top: 0;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.status-line {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1rem 0;
}

.pill {
  display: inline-flex;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: #eef3ff;
  color: #2247d5;
  font-weight: 600;
}

.stack {
  display: grid;
  gap: 1rem;
}

.note-list {
  margin: 0;
  padding-left: 1.1rem;
}

.output {
  min-height: 14rem;
  border-radius: 0.8rem;
  padding: 1rem;
  background: #0f1728;
  color: #d9e2ff;
  overflow: auto;
}
```

#### client/tests/e2e.spec.ts

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

import { expect, test } from '@playwright/test';

test('reader session can authenticate but not access the admin report', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText('server: healthy')).toBeVisible();
  await page.getByRole('button', { name: 'Who am I?' }).click();
  await expect(page.locator('#response-output')).toContainText('ErrorUnauthenticated_');

  await page.getByRole('button', { name: 'Sign in as reader' }).click();
  await expect(page.locator('#session-pill')).toContainText('reader');

  await page.getByRole('button', { name: 'Who am I?' }).click();
  await expect(page.locator('#response-output')).toContainText('Demo Reader');
  await expect(page.locator('#request-pill')).toContainText(/request id: [0-9a-f-]{36}/i);

  await page.getByRole('button', { name: 'Load admin report' }).click();
  await expect(page.locator('#response-output')).toContainText('ErrorUnauthorized_');
  await expect(page.locator('#ops-output')).toContainText('fn.adminReport');
});

test('admin session can access the admin report and see unknown errors stay generic', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('button', { name: 'Sign in as admin' }).click();
  await expect(page.locator('#session-pill')).toContainText('admin');

  await page.getByRole('button', { name: 'Load admin report' }).click();
  await expect(page.locator('#response-output')).toContainText('requestCount');
  await expect(page.locator('#response-output')).toContainText('unknownErrorCount');

  await page.getByRole('button', { name: 'Trigger server bug' }).click();
  await expect(page.locator('#response-output')).toContainText('ErrorUnknown_');
  await expect(page.locator('#response-output')).toContainText('caseId');
  await expect(page.locator('#ops-output')).toContainText('telepact.error');
  await expect(page.locator('#ops-output')).toContainText('ErrorUnknown_');
});
```

#### client/tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "module": "ESNext",
    "lib": [
      "ES2023",
      "DOM"
    ],
    "types": [
      "vite/client"
    ],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": [
    "src"
  ]
}
```

### schema-baseline/

#### schema-baseline/dashboard.telepact.yaml

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

- ///: Browser session credentials translated from HTTP cookies.
  union.Auth_:
    - Session:
        token: "string"
- ///: Return the normalized caller identity after transport auth extraction.
  fn.me: {}
  ->:
    - Ok_:
        userId: "string"
        role: "string"
        displayName: "string"
- ///: Return an admin-only operational summary.
  fn.adminReport: {}
  ->:
    - Ok_:
        requestCount: "integer"
        unauthorizedCount: "integer"
        unknownErrorCount: "integer"
        lastRequestId: "string?"
- ///: Force an unexpected server bug to demonstrate ErrorUnknown_ handling.
  fn.triggerFailure: {}
  ->:
    - Ok_:
        message: "string"
```

### server/

#### server/app.py

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
import json
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from telepact_app import log, process_telepact_request, read_session_cookie, snapshot_ops_state

EXAMPLE_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIST_DIR = EXAMPLE_DIR / 'client' / 'dist'
BODY_LIMIT_BYTES = 64 * 1024
STATIC_CONTENT_TYPES = {
    '.css': 'text/css; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.ico': 'image/x-icon',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
}


def _set_json_headers(handler: BaseHTTPRequestHandler, status_code: int = 200) -> None:
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Cache-Control', 'no-store')


def _write_json(handler: BaseHTTPRequestHandler, payload: dict[str, object], status_code: int = 200) -> None:
    encoded = json.dumps(payload).encode('utf-8')
    _set_json_headers(handler, status_code)
    handler.send_header('Content-Length', str(len(encoded)))
    handler.end_headers()
    handler.wfile.write(encoded)


def _safe_static_path(url_path: str) -> Path | None:
    client_root = CLIENT_DIST_DIR.resolve()
    requested_path = unquote(urlsplit(url_path).path)
    requested = PurePosixPath('index.html' if requested_path in ('', '/') else requested_path.lstrip('/'))
    if requested.is_absolute() or '..' in requested.parts:
        return None

    candidate = (client_root / Path(*requested.parts)).resolve()
    if candidate.exists() and candidate.is_file() and client_root in candidate.parents:
        return candidate

    fallback = (client_root / 'index.html').resolve()
    if requested.suffix == '' and fallback.exists() and client_root in fallback.parents:
        return fallback
    return None


def _serve_static(handler: BaseHTTPRequestHandler, url_path: str) -> None:
    file_path = _safe_static_path(url_path)
    if file_path is None or not file_path.is_file():
        handler.send_response(404)
        handler.end_headers()
        return

    data = file_path.read_bytes()
    content_type = STATIC_CONTENT_TYPES.get(file_path.suffix, 'application/octet-stream')
    handler.send_response(200)
    handler.send_header('Content-Type', content_type or 'application/octet-stream')
    handler.send_header('Content-Length', str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _set_session_cookie(handler: BaseHTTPRequestHandler, session_token: str | None) -> None:
    cookie = SimpleCookie()
    cookie['session'] = '' if session_token is None else session_token
    cookie['session']['path'] = '/'
    cookie['session']['httponly'] = True
    cookie['session']['samesite'] = 'Lax'
    if session_token is None:
        cookie['session']['max-age'] = 0
    handler.send_header('Set-Cookie', cookie.output(header='').strip())


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == '/healthz':
            _write_json(self, {'ok': True})
            return
        if self.path == '/ops/snapshot':
            _write_json(self, snapshot_ops_state())
            return
        _serve_static(self, self.path)

    def do_POST(self) -> None:
        if self.path == '/session/user':
            payload = {'session': 'reader', 'cookie': 'demo-user-session'}
            _set_json_headers(self)
            _set_session_cookie(self, 'demo-user-session')
            body = json.dumps(payload).encode('utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == '/session/admin':
            payload = {'session': 'admin', 'cookie': 'demo-admin-session'}
            _set_json_headers(self)
            _set_session_cookie(self, 'demo-admin-session')
            body = json.dumps(payload).encode('utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == '/session/logout':
            payload = {'session': 'anonymous'}
            _set_json_headers(self)
            _set_session_cookie(self, None)
            body = json.dumps(payload).encode('utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path != '/api/telepact':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', '0'))
        if content_length > BODY_LIMIT_BYTES:
            _write_json(self, {'error': 'request body too large'}, status_code=413)
            return

        request_bytes = self.rfile.read(content_length)
        request_id = str(uuid4())
        session_token = read_session_cookie(self.headers.get('Cookie'))
        response = process_telepact_request(request_bytes, request_id, session_token)

        self.send_response(200)
        self.send_header('Content-Type', response.content_type)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Request-ID', request_id)
        self.end_headers()
        self.wfile.write(response.response_bytes)

    def log_message(self, format_string: str, *args: object) -> None:
        return


def create_http_server(host: str = '127.0.0.1', port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), RequestHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the Telepact full-stack example server.')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    server = create_http_server(args.host, args.port)
    log.info('serving full-stack example on http://%s:%s', args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
```

#### server/telepact_app.py

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

import asyncio
import json
import logging
import threading
from collections import deque
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import dataclass
from http.cookies import SimpleCookie
from pathlib import Path
from time import perf_counter

from telepact import FunctionRouter, Message, Server, TelepactError, TelepactSchema, TelepactSchemaFiles

EXAMPLE_DIR = Path(__file__).resolve().parent.parent
RECENT_EVENT_LIMIT = 20

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger('telepact.example.full_stack')


@dataclass(frozen=True)
class SessionIdentity:
    user_id: str
    role: str
    display_name: str


@dataclass(frozen=True)
class TelepactHttpResponse:
    response_bytes: bytes
    content_type: str


VALID_SESSIONS = {
    'demo-user-session': SessionIdentity('user-123', 'reader', 'Demo Reader'),
    'demo-admin-session': SessionIdentity('admin-007', 'admin', 'Demo Admin'),
}

_METRICS_LOCK = threading.Lock()
_METRICS: dict[str, object] = {
    'requestCount': 0,
    'unauthorizedCount': 0,
    'unknownErrorCount': 0,
    'lastRequestId': None,
    'byFunction': {},
}
_RECENT_EVENTS: deque[dict[str, object]] = deque(maxlen=RECENT_EVENT_LIMIT)
_REQUEST_CONTEXT: ContextVar[dict[str, object]] = ContextVar('request_context', default={})

files = TelepactSchemaFiles(str(EXAMPLE_DIR / 'api'))
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


def _replace_context(context: dict[str, object]) -> None:
    _REQUEST_CONTEXT.set(context)


def _merge_context(**updates: object) -> dict[str, object]:
    current = dict(_REQUEST_CONTEXT.get())
    current.update({key: value for key, value in updates.items() if value is not None})
    _replace_context(current)
    return current


def _append_event(event_type: str, **fields: object) -> None:
    event = {'type': event_type, **fields}
    with _METRICS_LOCK:
        _RECENT_EVENTS.append(event)
    log.info(json.dumps(event, sort_keys=True))


def _record_metric(function_name: str, outcome: str, duration_ms: float, request_id: str | None) -> None:
    with _METRICS_LOCK:
        _METRICS['requestCount'] = int(_METRICS['requestCount']) + 1
        _METRICS['lastRequestId'] = request_id
        if outcome == 'ErrorUnauthorized_':
            _METRICS['unauthorizedCount'] = int(_METRICS['unauthorizedCount']) + 1
        if outcome == 'ErrorUnknown_':
            _METRICS['unknownErrorCount'] = int(_METRICS['unknownErrorCount']) + 1

        by_function = _METRICS['byFunction']
        assert isinstance(by_function, dict)
        function_metrics = by_function.setdefault(function_name, {
            'calls': 0,
            'totalDurationMs': 0.0,
            'outcomes': {},
        })
        assert isinstance(function_metrics, dict)
        function_metrics['calls'] = int(function_metrics['calls']) + 1
        function_metrics['totalDurationMs'] = float(function_metrics['totalDurationMs']) + duration_ms
        outcomes = function_metrics['outcomes']
        assert isinstance(outcomes, dict)
        outcomes[outcome] = int(outcomes.get(outcome, 0)) + 1


def snapshot_ops_state() -> dict[str, object]:
    with _METRICS_LOCK:
        metrics = deepcopy(_METRICS)
        events = list(_RECENT_EVENTS)

    by_function = metrics.get('byFunction', {})
    if isinstance(by_function, dict):
        for value in by_function.values():
            if isinstance(value, dict):
                calls = int(value.get('calls', 0))
                total_duration_ms = float(value.get('totalDurationMs', 0.0))
                value['averageDurationMs'] = round(total_duration_ms / calls, 2) if calls else 0.0
                value['totalDurationMs'] = round(total_duration_ms, 2)

    return {
        'metrics': metrics,
        'recentEvents': events,
    }


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


def normalized_identity(session_token: str | None) -> SessionIdentity | None:
    if session_token is None:
        return None
    return VALID_SESSIONS.get(session_token)


async def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    session = auth.get('Session') if isinstance(auth, dict) else None
    token = session.get('token') if isinstance(session, dict) else None
    identity = normalized_identity(token if isinstance(token, str) else None)
    if identity is None:
        return {}

    _merge_context(userId=identity.user_id, role=identity.role, displayName=identity.display_name)
    return {
        '@userId': identity.user_id,
        '@role': identity.role,
        '@displayName': identity.display_name,
    }


options.on_auth = on_auth


def on_request(message: Message) -> None:
    _merge_context(functionName=message.get_body_target(), startedAt=perf_counter())


options.on_request = on_request


def on_response(message: Message) -> None:
    context = dict(_REQUEST_CONTEXT.get())
    function_name = str(context.get('functionName', 'unknown'))
    request_id = context.get('requestId')
    user_id = context.get('userId', 'anonymous')
    role = context.get('role', 'anonymous')
    started_at = context.get('startedAt')
    duration_ms = round((perf_counter() - float(started_at)) * 1000, 2) if isinstance(started_at, (int, float)) else 0.0
    outcome = message.get_body_target()
    case_id = context.get('caseId')

    _record_metric(function_name, outcome, duration_ms, request_id if isinstance(request_id, str) else None)
    _append_event(
        'telepact.response',
        requestId=request_id,
        function=function_name,
        userId=user_id,
        role=role,
        outcome=outcome,
        durationMs=duration_ms,
        caseId=case_id,
    )


options.on_response = on_response


def on_error(error: TelepactError) -> None:
    context = _merge_context(caseId=error.case_id, errorKind=error.kind)
    _append_event(
        'telepact.error',
        requestId=context.get('requestId'),
        function=context.get('functionName', 'unknown'),
        caseId=error.case_id,
        kind=error.kind,
        message=str(error),
    )
    log.exception('telepact error case_id=%s', error.case_id, exc_info=error)


options.on_error = on_error


async def middleware(request_message: Message, function_router: FunctionRouter) -> Message:
    _merge_context(functionName=request_message.get_body_target())
    return await function_router.route(request_message)


options.middleware = middleware


async def me(_function_name: str, request_message: Message) -> Message:
    user_id = request_message.headers.get('@userId')
    role = request_message.headers.get('@role')
    display_name = request_message.headers.get('@displayName')
    if not isinstance(user_id, str) or not isinstance(role, str) or not isinstance(display_name, str):
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'missing or invalid session cookie',
            },
        })

    return Message({}, {
        'Ok_': {
            'userId': user_id,
            'role': role,
            'displayName': display_name,
        },
    })


async def admin_report(_function_name: str, request_message: Message) -> Message:
    if request_message.headers.get('@userId') is None:
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'sign in before requesting the admin report',
            },
        })

    if request_message.headers.get('@role') != 'admin':
        return Message({}, {
            'ErrorUnauthorized_': {
                'message!': 'admin role required',
            },
        })

    metrics = snapshot_ops_state()['metrics']
    assert isinstance(metrics, dict)
    return Message({}, {
        'Ok_': {
            'requestCount': int(metrics['requestCount']),
            'unauthorizedCount': int(metrics['unauthorizedCount']),
            'unknownErrorCount': int(metrics['unknownErrorCount']),
            'lastRequestId': metrics['lastRequestId'],
        },
    })


async def trigger_failure(_function_name: str, request_message: Message) -> Message:
    actor = request_message.headers.get('@displayName', 'anonymous caller')
    raise RuntimeError(f'demo bug for {actor}')


function_router = FunctionRouter({
    'fn.me': me,
    'fn.adminReport': admin_report,
    'fn.triggerFailure': trigger_failure,
})
telepact_server = Server(schema, function_router, options)


def process_telepact_request(request_bytes: bytes, request_id: str, session_token: str | None) -> TelepactHttpResponse:
    context_token = _REQUEST_CONTEXT.set({'requestId': request_id, 'transport': 'http'})
    loop = asyncio.new_event_loop()
    try:
        def update_headers(headers: dict[str, object]) -> None:
            headers['@requestId'] = request_id
            if session_token is not None:
                headers['@auth_'] = {'Session': {'token': session_token}}

        response = loop.run_until_complete(telepact_server.process(request_bytes, update_headers))
        content_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'
        return TelepactHttpResponse(response_bytes=response.bytes, content_type=content_type)
    finally:
        loop.close()
        _REQUEST_CONTEXT.reset(context_token)
```
