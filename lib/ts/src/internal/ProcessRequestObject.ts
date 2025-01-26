import { Message } from '../Message';
import { Serializer } from '../Serializer';
import { UApiError } from '../UApiError';
import { objectsAreEqual } from '../internal/ObjectsAreEqual';

function timeoutPromise(timeoutMs: number): Promise<never> {
    return new Promise((_resolve, reject) => {
        setTimeout(() => {
            reject(new Error('Promise timed out'));
        }, timeoutMs);
    });
}

export async function processRequestObject(
    requestMessage: Message,
    adapter: (message: Message, serializer: Serializer) => Promise<Message>,
    serializer: Serializer,
    timeoutMsDefault: number,
    useBinaryDefault: boolean,
    alwaysSendJson: boolean,
): Promise<Message> {
    const header: Record<string, any> = requestMessage.headers;

    try {
        if (!header.hasOwnProperty('time_')) {
            header['time_'] = timeoutMsDefault;
        }

        if (useBinaryDefault) {
            header['_binary'] = true;
        }

        if (header['_binary'] && alwaysSendJson) {
            header['_forceSendJson'] = true;
        }

        const timeoutMs = header['time_'] as number;

        const responseMessage = await Promise.race([adapter(requestMessage, serializer), timeoutPromise(timeoutMs)]);

        if (
            objectsAreEqual(responseMessage.body, {
                ErrorParseFailure_: { reasons: [{ IncompatibleBinaryEncoding: {} }] },
            })
        ) {
            header['_binary'] = true;
            header['_forceSendJson'] = true;

            return await Promise.race([adapter(requestMessage, serializer), timeoutPromise(timeoutMs)]);
        }

        return responseMessage;
    } catch (e) {
        throw new UApiError(e as Error);
    }
}
