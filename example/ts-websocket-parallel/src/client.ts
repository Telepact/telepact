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

import { once } from 'node:events';
import { RawData, WebSocket } from 'ws';
import { Client, ClientOptions, Message, Serializer } from 'telepact';

type PendingRequest = {
    resolve: (message: Message) => void;
    reject: (error: Error) => void;
};

function normalizeCallId(callId: unknown): string {
    return JSON.stringify(callId);
}

function toUint8Array(data: RawData): Uint8Array {
    if (data instanceof ArrayBuffer) {
        return new Uint8Array(data);
    }

    if (Array.isArray(data)) {
        return new Uint8Array(Buffer.concat(data));
    }

    return new Uint8Array(data);
}

function assignCallId(message: Message, nextCallId: () => string): string {
    if (!Object.prototype.hasOwnProperty.call(message.headers, '@id_')) {
        message.headers['@id_'] = nextCallId();
    }

    return normalizeCallId(message.headers['@id_']);
}

export async function createExampleClient(url: string): Promise<{
    client: Client;
    close: () => Promise<void>;
}> {
    const socket = new WebSocket(url);
    const pending = new Map<string, PendingRequest>();
    let serializerForResponses: Serializer | null = null;
    let nextCallNumber = 1;
    let closed = false;

    const rejectPending = (error: Error) => {
        if (closed) {
            return;
        }
        closed = true;
        for (const { reject } of pending.values()) {
            reject(error);
        }
        pending.clear();
    };

    socket.on('message', (responseBytes: RawData) => {
        if (serializerForResponses === null) {
            rejectPending(new Error('WebSocket response arrived before serializer was ready'));
            return;
        }

        const responseMessage = serializerForResponses.deserialize(toUint8Array(responseBytes));
        const callId = responseMessage.headers['@id_'];
        if (callId === undefined) {
            rejectPending(new Error('WebSocket response was missing @id_'));
            return;
        }

        const pendingRequest = pending.get(normalizeCallId(callId));
        if (!pendingRequest) {
            rejectPending(new Error(`No pending request matched @id_ ${JSON.stringify(callId)}`));
            return;
        }

        pending.delete(normalizeCallId(callId));
        pendingRequest.resolve(responseMessage);
    });
    socket.on('close', () => rejectPending(new Error('WebSocket closed before all responses arrived')));
    socket.on('error', (error: Error) => rejectPending(error));

    await once(socket, 'open');

    const adapter = async (requestMessage: Message, serializer: Serializer): Promise<Message> => {
        serializerForResponses = serializer;
        const callId = assignCallId(requestMessage, () => `call-${nextCallNumber++}`);
        const requestBytes = serializer.serialize(requestMessage);

        const responsePromise = new Promise<Message>((resolve, reject) => {
            pending.set(callId, { resolve, reject });
        });

        socket.send(Buffer.from(requestBytes), (error) => {
            if (!error) {
                return;
            }

            pending.delete(callId);
            rejectPending(error);
        });
        return responsePromise;
    };

    return {
        client: new Client(adapter, new ClientOptions()),
        close: async () => {
            if (socket.readyState === WebSocket.CLOSED) {
                closed = true;
                return;
            }

            await new Promise<void>((resolve) => {
                socket.once('close', () => {
                    closed = true;
                    resolve();
                });
                socket.close();
            });
        },
    };
}
