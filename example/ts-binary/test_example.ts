//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import assert from 'node:assert/strict';
import test from 'node:test';
import { Client, ClientOptions, Message, Serializer } from 'telepact';
import { buildTelepactServer } from './server.js';

test('binary example runs end to end', async () => {
    const telepactServer = buildTelepactServer();
    let sawBinaryResponse = false;

    const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
        const requestBytes = serializer.serialize(message);
        const response = await telepactServer.process(requestBytes);
        if ('@bin_' in response.headers) {
            sawBinaryResponse = true;
        }
        return serializer.deserialize(response.bytes);
    };

    const options = new ClientOptions();
    options.useBinary = true;
    options.alwaysSendJson = false;
    const client = new Client(adapter, options);

    for (let index = 0; index < 2; index += 1) {
        const response = await client.request(new Message({}, { 'fn.getNumbers': { 'limit': 3 } }));
        assert.deepEqual(response.body['Ok_']['values'], [1, 2, 3]);
    }

    assert.equal(sawBinaryResponse, true, 'expected at least one binary response');
});
