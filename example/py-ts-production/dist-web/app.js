"use strict";
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
const resultNode = document.getElementById('result');
const observabilityNode = document.getElementById('observability');
if (!(resultNode instanceof HTMLElement) || !(observabilityNode instanceof HTMLElement)) {
    throw new Error('expected output elements');
}
const resultElement = resultNode;
const observabilityElement = observabilityNode;
function nextRequestId() {
    if ('randomUUID' in crypto) {
        return crypto.randomUUID();
    }
    return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
async function postTelepact(functionName, payload) {
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
    const [headers, body] = await response.json();
    return {
        requestId,
        status: response.status,
        httpRequestId: response.headers.get('X-Request-Id'),
        headers,
        body,
    };
}
async function postSession(path) {
    const response = await fetch(path, {
        method: 'POST',
        credentials: 'same-origin',
    });
    if (!response.ok) {
        throw new Error(`session request failed with ${response.status}`);
    }
}
async function loadObservability() {
    const response = await fetch('/ops/observability', {
        credentials: 'same-origin',
    });
    const payload = await response.json();
    observabilityElement.textContent = JSON.stringify(payload, null, 2);
}
function renderResult(label, value) {
    resultElement.textContent = `${label}\n\n${JSON.stringify(value, null, 2)}`;
}
function wireButton(id, handler) {
    const button = document.getElementById(id);
    if (!(button instanceof HTMLButtonElement)) {
        throw new Error(`expected button ${id}`);
    }
    button.addEventListener('click', () => {
        void (async () => {
            try {
                await handler();
            }
            catch (error) {
                renderResult('error', {
                    message: error instanceof Error ? error.message : String(error),
                });
            }
        })();
    });
}
wireButton('login-viewer', async () => {
    await postSession('/login?role=viewer');
    renderResult('signed in', { role: 'viewer' });
    await loadObservability();
});
wireButton('login-admin', async () => {
    await postSession('/login?role=admin');
    renderResult('signed in', { role: 'admin' });
    await loadObservability();
});
wireButton('logout', async () => {
    await postSession('/logout');
    renderResult('signed out', {});
    await loadObservability();
});
wireButton('load-dashboard', async () => {
    const response = await postTelepact('fn.viewerDashboard', {});
    renderResult('dashboard response', response);
    await loadObservability();
});
wireButton('load-admin-audit', async () => {
    const response = await postTelepact('fn.adminAudit', {});
    renderResult('admin audit response', response);
    await loadObservability();
});
wireButton('trigger-crash', async () => {
    const response = await postTelepact('fn.debugCrash', {});
    renderResult('crash response', response);
    await loadObservability();
});
wireButton('refresh-observability', loadObservability);
