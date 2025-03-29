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

import { Message } from '../Message';
import { Serializer } from '../Serializer';
import { TelepactError } from '../TelepactError';
import { objectsAreEqual } from './ObjectsAreEqual';

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
        throw new TelepactError(e as Error);
    }
}
