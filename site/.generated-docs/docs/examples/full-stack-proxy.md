# full-stack-proxy

A runnable Telepact example with a TypeScript browser client, a Python HTTP-to-NATS
proxy, and a Go Telepact server.

This example shows how to expose an internal NATS RPC subject through a more common
HTTP transport without putting any Telepact logic in the proxy itself. The browser
still sends Telepact request bytes and receives Telepact response bytes over fixed
HTTP routes, while the Python proxy is the only generalized component that forwards
those bytes between HTTP and the NATS subject encoded in the URL.

## Layout

- [`api/greet.telepact.yaml`](#api-greet-telepact-yaml) - Telepact schema used by the Go server and browser client
- [`client/`](#client) - Vite-powered browser app and Playwright e2e coverage
- [`proxy/app.py`](#proxy-app-py) - Python HTTP server that serves the app and forwards raw bytes to NATS
- [`server/main.go`](#server-main-go) - Go Telepact server that listens on the configured NATS subject

## Run it

```bash
make run
```

That target rebuilds the local Go and TypeScript Telepact libraries, installs the
proxy dependencies, builds the browser app, compiles the Go server, and runs the
Playwright end-to-end suite against the full stack.

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
PYTHON := proxy/.venv/bin/python

.PHONY: run clean

run:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/go; \
	$(MAKE) -C ../../lib/ts; \
	rm -rf proxy/.venv client/node_modules client/dist client/playwright-report client/test-results client/telepact.tgz server/bin; \
	uv venv --python python3.11 proxy/.venv; \
	uv pip install --python $(PYTHON) -r proxy/requirements.txt; \
	cp ../../lib/ts/dist-tgz/*.tgz client/telepact.tgz; \
	(cd client && npm install --ignore-scripts --no-package-lock); \
	(cd client && npm run build); \
	mkdir -p server/bin; \
	(cd server && GOTOOLCHAIN=local go build -o ./bin/full-stack-proxy-server .); \
	(cd client && npx playwright install chromium); \
	(cd client && npm test)

clean:
	@rm -rf proxy/.venv client/node_modules client/dist client/playwright-report client/test-results client/telepact.tgz server/bin
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

- ///: Send a greeting request through an HTTP-to-NATS proxy.
  fn.greet:
    name: "string"
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
    <title>Telepact full-stack proxy example</title>
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
  "name": "telepact-example-full-stack-proxy-client",
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
const serverBinary = path.resolve(__dirname, '../server/bin/full-stack-proxy-server');
const apiDir = path.resolve(__dirname, '../api');
const proxyPython = path.resolve(__dirname, '../proxy/.venv/bin/python');
const proxyEntrypoint = path.resolve(__dirname, '../proxy/app.py');
const port = 4173;
const natsPort = 4322;
const healthPort = 8413;
const TEST_TIMEOUT_MS = 60 * 1000;

export default defineConfig({
  testDir: './tests',
  timeout: TEST_TIMEOUT_MS,
  use: {
    baseURL: `http://127.0.0.1:${port}`,
  },
  webServer: [
    {
      command: `nats-server -D -p ${natsPort}`,
      port: natsPort,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: `${serverBinary} --nats-url nats://127.0.0.1:${natsPort} --subject rpc.demo.greet --api-dir ${apiDir} --health-port ${healthPort}`,
      port: healthPort,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: `${proxyPython} ${proxyEntrypoint} --host 127.0.0.1 --port ${port} --nats-url nats://127.0.0.1:${natsPort}`,
      port,
      reuseExistingServer: !process.env.CI,
    },
  ],
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
  <span class="pill">Browser TypeScript → HTTP → Python proxy → NATS → Go Telepact server</span>
  <h1>Telepact full-stack proxy demo</h1>
  <p>
    The browser sends Telepact request bytes over HTTP to a Python proxy. The proxy does not use
    Telepact at all; it only forwards the raw bytes to the NATS subject encoded in the request URL.
    A Go Telepact server listens on that subject and replies with Telepact response bytes.
  </p>
</section>
<section class="grid">
  <div class="stack">
    <div class="card">
      <h2>Route over HTTP</h2>
      <label class="field">
        <span>Name</span>
        <input id="name-input" type="text" value="Telepact" spellcheck="false" />
      </label>
      <div class="actions">
        <button id="send-request">Send greeting</button>
        <button id="send-missing" class="secondary">Use missing subject</button>
        <button id="refresh-health" class="secondary">Refresh proxy health</button>
      </div>
      <div class="status-line">
        <span class="pill" id="health-pill">proxy: loading</span>
        <span class="pill" id="path-pill">POST /rpc/rpc.demo.greet</span>
        <span class="pill" id="outcome-pill">outcome: none</span>
      </div>
    </div>
    <div class="card">
      <h2>What this example demonstrates</h2>
      <ul class="note-list">
        <li>the browser can use plain HTTP while the internal RPC transport stays on NATS</li>
        <li>the proxy forwards raw request and response bytes without importing Telepact</li>
        <li>the browser uses fixed routes, while the proxy stays generic and routes by URL subject</li>
        <li>the Go server still speaks normal Telepact once the bytes arrive on its topic</li>
      </ul>
    </div>
  </div>
  <div class="stack">
    <div class="card">
      <h2>Latest response</h2>
      <div class="output"><pre id="response-output">Waiting for a browser action…</pre></div>
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

type HealthResponse = {
  ok?: boolean;
  natsUrl?: string;
};

const GREET_SUBJECT = 'rpc.demo.greet';
const MISSING_SUBJECT = 'rpc.demo.missing';

const app = document.querySelector<HTMLDivElement>('#app');
if (app === null) {
  throw new Error('missing #app root');
}

app.innerHTML = appHtml;

const nameInput = must<HTMLInputElement>('#name-input');
const healthPill = must<HTMLSpanElement>('#health-pill');
const pathPill = must<HTMLSpanElement>('#path-pill');
const outcomePill = must<HTMLSpanElement>('#outcome-pill');
const responseOutput = must<HTMLPreElement>('#response-output');
const buttons = Array.from(document.querySelectorAll<HTMLButtonElement>('button'));

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

function formatError(error: unknown): string {
  if (error instanceof Error && error.cause instanceof Error) {
    return error.cause.message;
  }
  return String(error);
}

function setBusy(isBusy: boolean): void {
  for (const button of buttons) {
    button.disabled = isBusy;
  }
}

function requestPath(subject: string): string {
  return `/rpc/${encodeURIComponent(subject)}`;
}

function syncSubjectUi(subject: string): string {
  pathPill.textContent = `POST ${requestPath(subject)}`;
  return subject;
}

async function sendGreeting(subject: string): Promise<void> {
  setBusy(true);
  syncSubjectUi(subject);

  try {
    const client = new Client(async (message: Message, serializer: Serializer): Promise<Message> => {
      const requestBytes = serializer.serialize(message);
      const requestBody = new Uint8Array(requestBytes.byteLength);
      requestBody.set(requestBytes);
      const response = await fetch(requestPath(subject), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: requestBody,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`proxy returned ${response.status}: ${errorText}`);
      }

      const responseBytes = new Uint8Array(await response.arrayBuffer());
      return serializer.deserialize(responseBytes);
    }, new ClientOptions());

    const response = await client.request(new Message({}, {
      'fn.greet': {
        name: nameInput.value,
      },
    }));
    outcomePill.textContent = `outcome: ${response.getBodyTarget()}`;
    responseOutput.textContent = pretty({
      subject,
      body: response.body,
    });
  } catch (error: unknown) {
    outcomePill.textContent = 'outcome: transport failure';
    responseOutput.textContent = pretty({
      subject,
      error: formatError(error),
    });
  } finally {
    setBusy(false);
  }
}

async function refreshHealth(): Promise<void> {
  const response = await fetch('/healthz', { cache: 'no-store' });
  const payload = (await response.json()) as HealthResponse;
  healthPill.textContent = payload.ok
    ? `proxy: connected to ${payload.natsUrl ?? 'NATS'}`
    : 'proxy: disconnected';
}

must<HTMLButtonElement>('#send-request').addEventListener('click', async () => {
  await sendGreeting(syncSubjectUi(GREET_SUBJECT));
});

must<HTMLButtonElement>('#send-missing').addEventListener('click', async () => {
  await sendGreeting(syncSubjectUi(MISSING_SUBJECT));
});

must<HTMLButtonElement>('#refresh-health').addEventListener('click', async () => {
  setBusy(true);
  try {
    await refreshHealth();
  } finally {
    setBusy(false);
  }
});

void (async () => {
  syncSubjectUi(GREET_SUBJECT);
  await refreshHealth();
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

button,
input {
  font: inherit;
}

button {
  cursor: pointer;
  border: 1px solid #2247d5;
  background: #2247d5;
  color: white;
  border-radius: 0.6rem;
  padding: 0.7rem 1rem;
}

button.secondary {
  background: white;
  color: #2247d5;
}

button:disabled {
  opacity: 0.65;
  cursor: progress;
}

input {
  width: 100%;
  border: 1px solid #cad3e4;
  border-radius: 0.6rem;
  padding: 0.7rem 0.85rem;
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
  max-width: 1100px;
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
  max-width: 64rem;
}

.grid {
  display: grid;
  gap: 1rem;
}

@media (min-width: 960px) {
  .grid {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }
}

.stack {
  display: grid;
  gap: 1rem;
}

.card {
  background: white;
  border-radius: 1rem;
  padding: 1rem;
  border: 1px solid #dbe2f0;
  box-shadow: 0 18px 45px rgba(23, 32, 51, 0.06);
}

.card h2 {
  margin-top: 0;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.status-line {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.pill {
  display: inline-flex;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: #eef3ff;
  color: #2247d5;
  font-weight: 600;
}

.field {
  display: grid;
  gap: 0.35rem;
  margin-top: 0.85rem;
}

.note-list {
  margin: 0;
  padding-left: 1.1rem;
}

.output {
  min-height: 16rem;
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

test('browser request reaches the Go Telepact server through the Python proxy', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('#health-pill')).toContainText('proxy: connected');
  await page.getByRole('button', { name: 'Send greeting' }).click();

  await expect(page.locator('#outcome-pill')).toContainText('Ok_');
  await expect(page.locator('#response-output')).toContainText('Hello Telepact from the Go Telepact server!');
  await expect(page.locator('#response-output')).toContainText('rpc.demo.greet');
  await expect(page.locator('#path-pill')).toContainText('POST /rpc/rpc.demo.greet');
});

test('browser uses a fixed missing-subject route and surfaces proxy transport failures', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('button', { name: 'Use missing subject' }).click();

  await expect(page.locator('#outcome-pill')).toContainText('transport failure');
  await expect(page.locator('#response-output')).toContainText('rpc.demo.missing');
  await expect(page.locator('#response-output')).toContainText('proxy returned');
  await expect(page.locator('#path-pill')).toContainText('POST /rpc/rpc.demo.missing');
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

### proxy/

#### proxy/app.py

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
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import nats
from nats.aio.client import Client as NatsClient
from nats.errors import TimeoutError as NatsTimeoutError

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


class ProxyTransportError(Exception):
    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class NatsProxy:
    def __init__(self, nats_url: str, timeout_seconds: float) -> None:
        self._nats_url = nats_url
        self._timeout_seconds = timeout_seconds
        self._loop = asyncio.new_event_loop()
        self._client: NatsClient | None = None
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _connect_with_retry(self, timeout_seconds: float) -> None:
        deadline = self._loop.time() + timeout_seconds
        while True:
            try:
                self._client = await nats.connect(self._nats_url, name='telepact-full-stack-proxy')
                return
            except Exception:
                if self._loop.time() >= deadline:
                    raise
                await asyncio.sleep(0.1)

    def connect(self, timeout_seconds: float = 10.0) -> None:
        future = asyncio.run_coroutine_threadsafe(self._connect_with_retry(timeout_seconds), self._loop)
        future.result(timeout=timeout_seconds + 1)

    async def _request(self, subject: str, payload: bytes) -> bytes:
        if self._client is None or self._client.is_closed:
            raise ProxyTransportError('NATS connection is not available', status_code=503)
        message = await self._client.request(subject, payload, timeout=self._timeout_seconds)
        return bytes(message.data)

    def request(self, subject: str, payload: bytes) -> bytes:
        future = asyncio.run_coroutine_threadsafe(self._request(subject, payload), self._loop)
        try:
            return future.result(timeout=self._timeout_seconds + 1)
        except NatsTimeoutError as error:
            raise ProxyTransportError(f'NATS request timed out for {subject}', status_code=504) from error
        except ProxyTransportError:
            raise
        except Exception as error:
            raise ProxyTransportError(f'NATS request failed for {subject}: {error}', status_code=502) from error

    async def _close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.close()
        self._loop.stop()

    def close(self) -> None:
        future = asyncio.run_coroutine_threadsafe(self._close(), self._loop)
        future.result(timeout=5)
        self._thread.join(timeout=5)

    def is_connected(self) -> bool:
        client = self._client
        return client is not None and client.is_connected and not client.is_closed

    @property
    def nats_url(self) -> str:
        return self._nats_url


NATS_PROXY: NatsProxy | None = None


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
    handler.send_header('Content-Type', content_type)
    handler.send_header('Content-Length', str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _proxy() -> NatsProxy:
    if NATS_PROXY is None:
        raise RuntimeError('proxy not initialized')
    return NATS_PROXY


def _read_request_bytes(handler: BaseHTTPRequestHandler) -> bytes:
    content_length = int(handler.headers.get('Content-Length', '0'))
    if content_length > BODY_LIMIT_BYTES:
        raise ProxyTransportError('request body too large', status_code=413)
    return handler.rfile.read(content_length)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == '/healthz':
            proxy = _proxy()
            status_code = 200 if proxy.is_connected() else 503
            _write_json(self, {'ok': proxy.is_connected(), 'natsUrl': proxy.nats_url}, status_code=status_code)
            return
        _serve_static(self, self.path)

    def do_POST(self) -> None:
        request_path = urlsplit(self.path).path
        if not request_path.startswith('/rpc/'):
            self.send_response(404)
            self.end_headers()
            return

        subject = unquote(request_path.removeprefix('/rpc/')).strip()
        if not subject:
            _write_json(self, {'error': 'missing NATS subject in URL'}, status_code=400)
            return

        try:
            request_bytes = _read_request_bytes(self)
            response_bytes = _proxy().request(subject, request_bytes)
        except ProxyTransportError as error:
            _write_json(self, {'error': str(error), 'subject': subject}, status_code=error.status_code)
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.send_header('X-NATS-Subject', subject)
        self.end_headers()
        self.wfile.write(response_bytes)

    def log_message(self, format_string: str, *args: object) -> None:
        return


def create_http_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), RequestHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the full-stack proxy example HTTP server.')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--nats-url', default='nats://127.0.0.1:4222')
    parser.add_argument('--nats-timeout-seconds', type=float, default=2.0)
    args = parser.parse_args()

    global NATS_PROXY
    NATS_PROXY = NatsProxy(args.nats_url, args.nats_timeout_seconds)
    NATS_PROXY.connect()

    server = create_http_server(args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if NATS_PROXY is not None:
            NATS_PROXY.close()


if __name__ == '__main__':
    main()
```

#### proxy/requirements.txt

### server/

#### server/go.mod

#### server/main.go

```go
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

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"
	"time"

	nats "github.com/nats-io/nats.go"
	telepact "github.com/telepact/telepact/lib/go"
)

func main() {
	natsURL := flag.String("nats-url", "nats://127.0.0.1:4222", "NATS server URL")
	subject := flag.String("subject", "rpc.demo.greet", "NATS subject to serve")
	apiDir := flag.String("api-dir", "../api", "Directory containing Telepact schema files")
	healthPort := flag.Int("health-port", 8413, "HTTP health port")
	flag.Parse()

	server, err := buildTelepactServer(*apiDir, *subject)
	if err != nil {
		log.Fatal(err)
	}

	nc, err := nats.Connect(*natsURL, nats.Name("telepact-full-stack-proxy-example"))
	if err != nil {
		log.Fatal(err)
	}
	defer nc.Close()

	_, err = nc.Subscribe(*subject, func(msg *nats.Msg) {
		resp, processErr := server.Process(msg.Data)
		if processErr != nil {
			log.Printf("server.Process error: %v", processErr)
			_ = msg.Respond(buildUnknownPayload())
			return
		}
		if respondErr := msg.Respond(resp.Bytes); respondErr != nil {
			log.Printf("respond error: %v", respondErr)
		}
	})
	if err != nil {
		log.Fatal(err)
	}
	if err := nc.Flush(); err != nil {
		log.Fatal(err)
	}

	healthServer := &http.Server{
		Addr:              fmt.Sprintf("127.0.0.1:%d", *healthPort),
		ReadHeaderTimeout: 5 * time.Second,
		Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.URL.Path != "/healthz" {
				http.NotFound(w, r)
				return
			}
			w.Header().Set("Content-Type", "application/json; charset=utf-8")
			_ = json.NewEncoder(w).Encode(map[string]any{
				"ok":      true,
				"subject": *subject,
			})
		}),
	}

	go func() {
		if serveErr := healthServer.ListenAndServe(); serveErr != nil && serveErr != http.ErrServerClosed {
			log.Printf("health server error: %v", serveErr)
		}
	}()

	log.Printf("go proxy example server ready on %s", *subject)

	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM)
	<-signals

	_ = healthServer.Close()
}

func buildTelepactServer(apiDir string, subject string) (*telepact.Server, error) {
	files, err := telepact.NewTelepactSchemaFiles(filepath.Clean(apiDir))
	if err != nil {
		return nil, err
	}
	schema, err := telepact.TelepactSchemaFromFileJSONMap(files.FilenamesToJSON)
	if err != nil {
		return nil, err
	}

	functionRouter := telepact.NewFunctionRouter(map[string]telepact.FunctionRoute{
		"fn.greet": func(functionName string, requestMessage telepact.Message) (telepact.Message, error) {
			arguments, ok := requestMessage.Body[functionName].(map[string]any)
			if !ok {
				return telepact.Message{}, fmt.Errorf("unexpected %s payload", functionName)
			}
			name, _ := arguments["name"].(string)
			return telepact.NewMessage(
				map[string]any{},
				map[string]any{
					"Ok_": map[string]any{
						"message": fmt.Sprintf("Hello %s from the Go Telepact server!", name),
					},
				},
			), nil
		},
	})

	options := telepact.NewServerOptions()
	options.AuthRequired = false
	return telepact.NewServer(schema, functionRouter, options)
}

func buildUnknownPayload() []byte {
	payload, err := json.Marshal([]any{map[string]any{}, map[string]any{"ErrorUnknown_": map[string]any{}}})
	if err != nil {
		return []byte(`[{},{"ErrorUnknown_":{}}]`)
	}
	return payload
}
```
