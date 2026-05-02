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
