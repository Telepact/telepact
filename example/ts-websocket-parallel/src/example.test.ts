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
import { Message } from 'telepact';
import { createExampleClient } from './client.js';
import { createExampleServer } from './server.js';

test('websocket example matches parallel responses by @id_', async () => {
    const server = createExampleServer();
    await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', () => resolve()));

    let closeClient: (() => Promise<void>) | null = null;
    try {
        const address = server.address() as AddressInfo | null;
        assert.ok(address && typeof address !== 'string');

        const { client, close } = await createExampleClient(`ws://127.0.0.1:${address.port}/ws/telepact`);
        closeClient = close;

        const requests = [
            new Message({}, { 'fn.greet': { subject: 'Ada', 'delayMs!': 60 } }),
            new Message({}, { 'fn.greet': { subject: 'Grace', 'delayMs!': 10 } }),
            new Message({}, { 'fn.greet': { subject: 'Linus', 'delayMs!': 30 } }),
        ];

        const responses = await Promise.all(requests.map(async (request) => {
            const response = await client.request(request);
            return {
                requestId: request.headers['@id_'],
                responseId: response.headers['@id_'],
                message: response.getBodyPayload().message,
            };
        }));

        assert.equal(new Set(responses.map((response) => response.requestId)).size, requests.length);
        assert.deepEqual(responses, [
            {
                requestId: requests[0].headers['@id_'],
                responseId: requests[0].headers['@id_'],
                message: 'Hello Ada!',
            },
            {
                requestId: requests[1].headers['@id_'],
                responseId: requests[1].headers['@id_'],
                message: 'Hello Grace!',
            },
            {
                requestId: requests[2].headers['@id_'],
                responseId: requests[2].headers['@id_'],
                message: 'Hello Linus!',
            },
        ]);
    } finally {
        if (closeClient !== null) {
            await closeClient();
        }

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
});
