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
import { postBytes, startPythonServer, stopPythonServer, waitForLog } from './test_support.js';

test('simple auth example runs end to end against the python server', async () => {
    const server = await startPythonServer();
    try {
        const url = `http://127.0.0.1:${server.port}/api/telepact`;
        const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
            const requestBytes = serializer.serialize(message);
            const responseBytes = await postBytes(url, requestBytes);
            return serializer.deserialize(responseBytes);
        };
        const client = new Client(adapter, new ClientOptions());

        const meResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'admin',
                    'password': 'swordfish',
                },
            },
        }, {
            'fn.me': {},
        }));
        assert.equal(meResponse.getBodyTarget(), 'Ok_');
        assert.deepEqual(meResponse.getBodyPayload(), {
            'userId': 'user-123',
            'role': 'admin',
        });

        const adminReportResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'viewer',
                    'password': 'opensesame',
                },
            },
        }, {
            'fn.adminReport': {},
        }));
        assert.equal(adminReportResponse.getBodyTarget(), 'ErrorUnauthorized_');
        assert.deepEqual(adminReportResponse.getBodyPayload(), {
            'message!': 'admin role required',
        });

        const authFailureResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'explode',
                    'password': 'boom',
                },
            },
        }, {
            'fn.me': {},
        }));
        assert.equal(authFailureResponse.getBodyTarget(), 'ErrorUnauthenticated_');
        assert.deepEqual(authFailureResponse.getBodyPayload(), {
            'message!': 'Valid authentication is required.',
        });

        await waitForLog(server, '"event": "middleware.identity", "function": "fn.me", "role": "admin", "userId": "user-123"');
        await waitForLog(server, '"event": "middleware.identity", "function": "fn.adminReport", "role": "viewer", "userId": "user-456"');
    } finally {
        await stopPythonServer(server);
    }
});
