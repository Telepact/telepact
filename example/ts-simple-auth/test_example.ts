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
import { runPythonServer, stopPythonServer } from './test_support.js';

test('simple auth example runs end to end', async () => {
    const server = await runPythonServer();
    try {
        const client = new Client(async (message: Message, serializer: Serializer): Promise<Message> => {
            const response = await fetch(server.url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: serializer.serialize(message),
            });
            const responseBytes = new Uint8Array(await response.arrayBuffer());
            return serializer.deserialize(responseBytes);
        }, new ClientOptions());

        const unauthenticated = await client.request(new Message({}, {
            'fn.me': {},
        }));
        assert.equal(unauthenticated.body['ErrorUnauthenticated_']['message!'], 'missing or invalid credentials');

        const reader = await client.request(new Message({
            '@auth_': {
                'Credentials': {
                    'username': 'demo-user',
                    'password': 'demo-pass',
                },
            },
        }, {
            'fn.me': {},
        }));
        assert.equal(reader.body['Ok_']['userId'], 'user-123');
        assert.equal(reader.body['Ok_']['role'], 'reader');

        const unauthorized = await client.request(new Message({
            '@auth_': {
                'Credentials': {
                    'username': 'demo-user',
                    'password': 'demo-pass',
                },
            },
        }, {
            'fn.adminReport': {},
        }));
        assert.equal(unauthorized.body['ErrorUnauthorized_']['message!'], 'admin role required');

        const admin = await client.request(new Message({
            '@auth_': {
                'Credentials': {
                    'username': 'demo-admin',
                    'password': 'demo-pass',
                },
            },
        }, {
            'fn.adminReport': {},
        }));
        assert.equal(admin.body['Ok_']['summary'], 'secret report for admin-456');
    } finally {
        await stopPythonServer(server);
    }
});
