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

        const shiftResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'lead-baker',
                    'password': 'sourdough',
                },
            },
        }, {
            'fn.myShift': {},
        }));
        assert.equal(shiftResponse.getBodyTarget(), 'Ok_');
        assert.deepEqual(shiftResponse.getBodyPayload(), {
            'employeeId': 'baker-001',
            'station': 'oven',
            'pastry': 'sesame loaf',
        });

        const specialResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'cashier',
                    'password': 'croissant',
                },
            },
        }, {
            'fn.approveSpecial': {},
        }));
        assert.equal(specialResponse.getBodyTarget(), 'ErrorUnauthorized_');
        assert.deepEqual(specialResponse.getBodyPayload(), {
            'message!': 'oven station required to approve the special',
        });

        const authFailureResponse = await client.request(new Message({
            '@auth_': {
                'Password': {
                    'username': 'explode',
                    'password': 'boom',
                },
            },
        }, {
            'fn.myShift': {},
        }));
        assert.equal(authFailureResponse.getBodyTarget(), 'ErrorUnauthenticated_');
        assert.deepEqual(authFailureResponse.getBodyPayload(), {
            'message!': 'Valid authentication is required.',
        });

        await waitForLog(server, '"employeeId": "baker-001", "event": "middleware.identity", "function": "fn.myShift", "station": "oven"');
        await waitForLog(server, '"employeeId": "cashier-002", "event": "middleware.identity", "function": "fn.approveSpecial", "station": "counter"');
    } finally {
        await stopPythonServer(server);
    }
});
