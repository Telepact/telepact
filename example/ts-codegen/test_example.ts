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
import { Client, ClientOptions, Message, Serializer } from 'telepact';
import { TypedClient, greet } from './gen/genTypes.js';
import { createHttpServer } from './server.js';

async function runServer(server: ReturnType<typeof createHttpServer>): Promise<void> {
    await new Promise<void>((resolve) => {
        server.listen(0, '127.0.0.1', () => resolve());
    });
}

async function stopServer(server: ReturnType<typeof createHttpServer>): Promise<void> {
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

async function postBytes(url: string, requestBytes: Uint8Array): Promise<Uint8Array> {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: Buffer.from(requestBytes),
    });
    return new Uint8Array(await response.arrayBuffer());
}

test('codegen example runs end to end', async () => {
    const server = createHttpServer();
    await runServer(server);
    try {
        const address = server.address() as AddressInfo;
        const url = `http://127.0.0.1:${address.port}/api/telepact`;

        const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
            const requestBytes = serializer.serialize(message);
            const responseBytes = await postBytes(url, requestBytes);
            return serializer.deserialize(responseBytes);
        };

        const client = new TypedClient(new Client(adapter, new ClientOptions()));
        const response = await client.greet({}, greet.Input.from({ subject: 'Telepact' }));

        const ok = response.body.getTaggedValue();
        assert.equal(ok.tag, 'Ok_');
        assert.equal(ok.value.message(), 'Hello Telepact from generated code!');
        assert.deepEqual(response.headers, {});
    } finally {
        await stopServer(server);
    }
});
