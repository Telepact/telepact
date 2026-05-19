//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import assert from 'node:assert/strict';
import test from 'node:test';
import { AddressInfo } from 'node:net';
import { createHttpServer } from './server.js';
import { postJson, runServer, stopServer } from './test_support.js';

test('select example runs end to end', async () => {
    const server = createHttpServer();
    await runServer(server);
    try {
        const address = server.address() as AddressInfo;
        const url = `http://127.0.0.1:${address.port}/api/telepact`;
        const fullPayload = await postJson(url, [
            {},
            {
                'fn.trackPackage': {},
            },
        ]);
        const selectedPayload = await postJson(url, [
            {
                '@select_': {
                    '->': {
                        'Ok_': ['package', 'latestEvent'],
                    },
                    'struct.Package': ['trackingId'],
                    'union.DeliveryEvent': {
                        'Dropoff': ['location'],
                    },
                },
            },
            {
                'fn.trackPackage': {},
            },
        ]);

        assert.deepEqual(fullPayload, [
            {},
            {
                'Ok_': {
                    'package': {
                        'trackingId': 'PKG-42',
                        'recipient': 'Ada Lovelace',
                        'city': 'London',
                    },
                    'latestEvent': {
                        'Dropoff': {
                            'location': 'Front desk',
                            'signedBy': 'M. Singh',
                        },
                    },
                    'note': 'Left with building reception.',
                },
            },
        ]);
        assert.deepEqual(selectedPayload, [
            {},
            {
                'Ok_': {
                    'package': {
                        'trackingId': 'PKG-42',
                    },
                    'latestEvent': {
                        'Dropoff': {
                            'location': 'Front desk',
                        },
                    },
                },
            },
        ]);
        assert.notDeepEqual(selectedPayload, fullPayload);
    } finally {
        await stopServer(server);
    }
});
