//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import assert from 'node:assert/strict';
import { once } from 'node:events';
import { AddressInfo } from 'node:net';
import test from 'node:test';
import { WebSocket } from 'ws';
import { createWebSocketServer } from './server.js';

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
            server.close((error?: Error) => {
                if (error) {
                    reject(error);
                    return;
                }
                resolve();
            });
        });
    }
});
