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

        assert.equal(
            followUpPayload[INDEX_MESSAGE_BODY]['Ok_']['summary'],
            'Followed up on follow-up-1 with for follow-up execution',
        );
        assert.deepEqual(followUpPayload[INDEX_MESSAGE_BODY]['Ok_']['details'], {
            kept: 'Ship docs',
            extra: 'for follow-up execution',
        });
    } finally {
        await stopServer(server);
    }
});

test('select can target types downstream of a link without trimming the link', async () => {
    const server = createHttpServer();
    await runServer(server);
    try {
        const address = server.address() as AddressInfo;
        const url = `http://127.0.0.1:${address.port}/api/telepact`;
        const payload = await postJson(url, [
            {
                '@select_': {
                    '->': {
                        Ok_: ['next!'],
                    },
                    'struct.FollowUpDetails': ['kept'],
                },
            },
            {
                'fn.createIssueLink': {
                    'title': 'Ship docs',
                },
            },
        ]);

        const nextCall = payload[INDEX_MESSAGE_BODY]['Ok_']['next!'];
        assert.deepEqual(nextCall, {
            'fn.getFollowUp': {
                'id': 'follow-up-1',
                'details': {
                    'kept': 'Ship docs',
                    'extra': 'for follow-up execution',
                },
            },
        });

        const followUpPayload = await postJson(url, [
            {},
            nextCall,
        ]);

        assert.equal(
            followUpPayload[INDEX_MESSAGE_BODY]['Ok_']['summary'],
            'Followed up on follow-up-1 with for follow-up execution',
        );
    } finally {
        await stopServer(server);
    }
});
