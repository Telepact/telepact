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
