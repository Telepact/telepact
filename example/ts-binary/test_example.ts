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
import { buildTelepactServer } from './server.js';

test('binary example runs end to end', async () => {
    const telepactServer = buildTelepactServer();
    let sawBinaryResponse = false;

    const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
        const requestBytes = serializer.serialize(message);
        const response = await telepactServer.process(requestBytes);
        if ('.bin_' in response.headers) {
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
