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
