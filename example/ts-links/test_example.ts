//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import assert from 'node:assert/strict';
import test from 'node:test';
import { AddressInfo } from 'node:net';
import { createHttpServer } from './server.js';
import { postJson, runServer, stopServer } from './test_support.js';

const INDEX_MESSAGE_BODY = 1;

test('links example runs end to end', async () => {
    const server = createHttpServer();
    await runServer(server);
    try {
        const address = server.address() as AddressInfo;
        const url = `http://127.0.0.1:${address.port}/api/telepact`;
        const payload = await postJson(url, [
            {},
            {
                'fn.createIssueLink': {
                    'title': 'Ship docs',
                },
            },
        ]);

        const nextCall = payload[INDEX_MESSAGE_BODY]['Ok_']['next!'];
        const followUpPayload = await postJson(url, [
            {},
            nextCall,
        ]);

        assert.equal(followUpPayload[INDEX_MESSAGE_BODY]['Ok_']['summary'], 'Followed up on follow-up-1');
    } finally {
        await stopServer(server);
    }
});
