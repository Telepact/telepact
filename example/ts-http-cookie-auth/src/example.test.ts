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
import { createExampleServer } from './server.js';

async function post(url: string, cookie?: string): Promise<any> {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            ...(cookie ? { cookie } : {}),
        },
        body: JSON.stringify([{}, { 'fn.me': {} }]),
    });

    assert.equal(response.status, 200);
    return response.json();
}

test('cookie auth example runs end to end', async () => {
    const server = createExampleServer();
    await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', () => resolve()));

    try {
        const address = server.address() as AddressInfo | null;
        assert.ok(address && typeof address !== 'string');
        const url = `http://127.0.0.1:${address.port}/api/telepact`;

        const unauthenticated = await post(url);
        const unauthenticatedBody = unauthenticated[1] as Record<string, unknown> | undefined;
        assert.ok(unauthenticatedBody, JSON.stringify(unauthenticated));
        assert.equal(unauthenticatedBody.Ok_, undefined);
        assert.ok(
            Object.keys(unauthenticatedBody).some((key) => key.toLowerCase().includes('error')),
            JSON.stringify(unauthenticated),
        );

        const authenticated = await post(url, 'session=demo-session');
        assert.equal(authenticated[1]?.Ok_?.userId, 'user-123');
    } finally {
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
