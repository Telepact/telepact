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

type TelepactHeaders = Record<string, unknown>;
type TelepactBody = Record<string, unknown>;

type TelepactResponse = {
    requestId: string;
    status: number;
    httpRequestId: string | null;
    headers: TelepactHeaders;
    body: TelepactBody;
};

const resultElement = document.getElementById('result');
const observabilityElement = document.getElementById('observability');

if (!(resultElement instanceof HTMLElement) || !(observabilityElement instanceof HTMLElement)) {
    throw new Error('expected output elements');
}

function nextRequestId(): string {
    if ('randomUUID' in crypto) {
        return crypto.randomUUID();
    }
    return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

async function postTelepact(functionName: string, payload: Record<string, unknown>): Promise<TelepactResponse> {
    const requestId = nextRequestId();
    const response = await fetch('/api/telepact', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-Request-Id': requestId,
        },
        body: JSON.stringify([
            { '@id_': requestId },
            { [functionName]: payload },
        ]),
    });

    const [headers, body] = await response.json() as [TelepactHeaders, TelepactBody];
    return {
        requestId,
        status: response.status,
        httpRequestId: response.headers.get('X-Request-Id'),
        headers,
        body,
    };
}

async function postSession(path: string): Promise<void> {
    const response = await fetch(path, {
        method: 'POST',
        credentials: 'same-origin',
    });
    if (!response.ok) {
        throw new Error(`session request failed with ${response.status}`);
    }
}

async function loadObservability(): Promise<void> {
    const response = await fetch('/ops/observability', {
        credentials: 'same-origin',
    });
    const payload = await response.json();
    observabilityElement.textContent = JSON.stringify(payload, null, 2);
}

function renderResult(label: string, value: unknown): void {
    resultElement.textContent = `${label}\n\n${JSON.stringify(value, null, 2)}`;
}

async function wireButton(id: string, handler: () => Promise<void>): Promise<void> {
    const button = document.getElementById(id);
    if (!(button instanceof HTMLButtonElement)) {
        throw new Error(`expected button ${id}`);
    }
    button.addEventListener('click', () => {
        void (async () => {
            try {
                await handler();
            } catch (error: unknown) {
                renderResult('error', {
                    message: error instanceof Error ? error.message : String(error),
                });
            }
        })();
    });
}

await wireButton('login-viewer', async () => {
    await postSession('/login?role=viewer');
    renderResult('signed in', { role: 'viewer' });
    await loadObservability();
});

await wireButton('login-admin', async () => {
    await postSession('/login?role=admin');
    renderResult('signed in', { role: 'admin' });
    await loadObservability();
});

await wireButton('logout', async () => {
    await postSession('/logout');
    renderResult('signed out', {});
    await loadObservability();
});

await wireButton('load-dashboard', async () => {
    const response = await postTelepact('fn.viewerDashboard', {});
    renderResult('dashboard response', response);
    await loadObservability();
});

await wireButton('load-admin-audit', async () => {
    const response = await postTelepact('fn.adminAudit', {});
    renderResult('admin audit response', response);
    await loadObservability();
});

await wireButton('trigger-crash', async () => {
    const response = await postTelepact('fn.debugCrash', {});
    renderResult('crash response', response);
    await loadObservability();
});

await wireButton('refresh-observability', loadObservability);
