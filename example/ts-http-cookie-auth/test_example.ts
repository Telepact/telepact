//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
        assert.equal('Ok_' in unauthenticatedBody, false);
        assert.equal(Object.keys(unauthenticatedBody).some((key) => key.toLowerCase().includes('error')), true);

        const authenticated = await postJson(url, [
            {},
            {
                'fn.me': {},
            },
        ], { 'Cookie': 'session=demo-session' });
        assert.equal(authenticated[1]['Ok_']['userId'], 'user-123');
    } finally {
        await stopServer(server);
    }
});
