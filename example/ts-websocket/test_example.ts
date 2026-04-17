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
import { once } from 'node:events';
import { AddressInfo } from 'node:net';
import test from 'node:test';
import { WebSocket } from 'ws';
import { createWebSocketServer } from './server';

test('websocket example runs end to end', async () => {
    const server = await createWebSocketServer();
    try {
        const address = server.address() as AddressInfo;
        const websocket = new WebSocket(`ws://127.0.0.1:${address.port}/ws/telepact`);
        await once(websocket, 'open');
        websocket.send(JSON.stringify([{}, { 'fn.greet': { 'subject': 'Telepact' } }]));
        const [response] = await once(websocket, 'message');
        const responseText = typeof response === 'string' ? response : response.toString('utf-8');
        assert.match(responseText, /Hello Telepact from WebSocket!/);
        websocket.close();
        await once(websocket, 'close');
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
