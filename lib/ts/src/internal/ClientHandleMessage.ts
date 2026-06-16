//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Message } from '../Message.js';
import { Serializer } from '../Serializer.js';
import { TelepactError } from '../TelepactError.js';
import { objectsAreEqual } from './ObjectsAreEqual.js';
import { SerializationError } from '../SerializationError.js';

function timeoutPromise(timeoutMs: number): Promise<never> {
    return new Promise((_resolve, reject) => {
        setTimeout(() => {
            reject(new Error('Promise timed out'));
        }, timeoutMs);
    });
}

export async function clientHandleMessage(
    requestMessage: Message,
    adapter: (message: Message, serializer: Serializer) => Promise<Message>,
    serializer: Serializer,
    timeoutMsDefault: number,
    useBinaryDefault: boolean,
    alwaysSendJson: boolean,
): Promise<Message> {
    const header: Record<string, any> = requestMessage.headers;

    try {
        if (!header.hasOwnProperty('@time_')) {
            header['@time_'] = timeoutMsDefault;
        }

        if (useBinaryDefault) {
            header['@binary_'] = true;
        }

        if (header['@binary_'] && alwaysSendJson) {
            header['_forceSendJson'] = true;
        }

        const timeoutMs = header['@time_'] as number;

        const responseMessage = await Promise.race([adapter(requestMessage, serializer), timeoutPromise(timeoutMs)]);

        if (
            objectsAreEqual(responseMessage.body, {
                ErrorParseFailure_: { reasons: [{ IncompatibleBinaryEncoding: {} }] },
            })
        ) {
            header['@binary_'] = true;
            header['_forceSendJson'] = true;

            return await Promise.race([adapter(requestMessage, serializer), timeoutPromise(timeoutMs)]);
        }

        return responseMessage;
    } catch (e) {
        if (e instanceof TelepactError) {
            throw e;
        }
        if (e instanceof SerializationError) {
            throw new TelepactError(
                'telepact client serialization or deserialization failed',
                'serialization',
                e,
            );
        }
        if (e instanceof Error && e.message === 'Promise timed out') {
            throw new TelepactError(
                `telepact client transport timed out after ${header['@time_']}ms`,
                'transport',
                e,
            );
        }
        throw new TelepactError('telepact client transport failed', 'transport', e);
    }
}
