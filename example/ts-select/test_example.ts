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

const INDEX_MESSAGE_BODY = 1;

test('select example runs end to end', async () => {
    const server = createHttpServer();
    await runServer(server);
    try {
        const address = server.address() as AddressInfo;
        const url = `http://127.0.0.1:${address.port}/api/telepact`;
        const structPayload = await postJson(url, [
            {
                '@select_': {
                    'struct.User': ['id'],
                },
            },
            {
                'fn.listUsers': {},
            },
        ]);

        assert.deepEqual(structPayload, [
            {},
            {
                'Ok_': {
                    'users': [
                        { 'id': 'user-1' },
                        { 'id': 'user-2' },
                    ],
                    'usersById': {
                        'user-1': { 'id': 'user-1' },
                        'user-2': { 'id': 'user-2' },
                    },
                    'featured': {
                        'Team': {
                            'team': {
                                'id': 'team-core',
                                'name': 'Core Platform',
                                'memberCount': 2,
                            },
                            'note': 'Maintains the shared Telepact APIs',
                        },
                    },
                },
            },
        ]);
        const responseBody = structPayload[INDEX_MESSAGE_BODY] as Record<string, any>;
        assert.deepEqual(responseBody['Ok_']['users'], [
            { 'id': 'user-1' },
            { 'id': 'user-2' },
        ]);

        const unionPayload = await postJson(url, [
            {
                '@select_': {
                    '->': {
                        'Ok_': ['featured'],
                    },
                },
            },
            {
                'fn.listUsers': {},
            },
        ]);

        assert.deepEqual(unionPayload, [
            {},
            {
                'Ok_': {
                    'featured': {
                        'Team': {
                            'team': {
                                'id': 'team-core',
                                'name': 'Core Platform',
                                'memberCount': 2,
                            },
                            'note': 'Maintains the shared Telepact APIs',
                        },
                    },
                },
            },
        ]);

        const nestedUnionPayload = await postJson(url, [
            {
                '@select_': {
                    '->': {
                        'Ok_': ['featured'],
                    },
                    'union.Highlight': {
                        'Team': ['team'],
                    },
                    'struct.Team': ['name'],
                },
            },
            {
                'fn.listUsers': {},
            },
        ]);

        assert.deepEqual(nestedUnionPayload, [
            {},
            {
                'Ok_': {
                    'featured': {
                        'Team': {
                            'team': {
                                'name': 'Core Platform',
                            },
                        },
                    },
                },
            },
        ]);
    } finally {
        await stopServer(server);
    }
});
