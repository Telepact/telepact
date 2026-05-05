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
        assert.equal(unauthenticatedBody['ErrorUnauthenticated_']['message!'], 'missing or invalid session cookie');

        const reader = await postJson(url, [
            {},
            {
                'fn.me': {},
            },
        ], { 'Cookie': 'session=demo-user-session' });
        assert.equal(reader[1]['Ok_']['userId'], 'user-123');
        assert.equal(reader[1]['Ok_']['role'], 'reader');

        const unauthorized = await postJson(url, [
            {},
            {
                'fn.adminReport': {},
            },
        ], { 'Cookie': 'session=demo-user-session' });
        assert.equal(unauthorized[1]['ErrorUnauthorized_']['message!'], 'admin role required');

        const admin = await postJson(url, [
            {},
            {
                'fn.adminReport': {},
            },
        ], { 'Cookie': 'session=demo-admin-session' });
        assert.equal(admin[1]['Ok_']['summary'], 'secret report for admin-456');
    } finally {
        await stopServer(server);
    }
});
