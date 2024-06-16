import { Message } from 'uapi/Message';
import { Serializer } from 'uapi/Serializer';
import { UApiError } from 'uapi/UApiError';
import { timeout } from 'util';

export async function processRequestObject(
    requestMessage: Message,
    adapter: (message: Message, serializer: Serializer) => Promise<Message>,
    serializer: Serializer,
    timeoutMsDefault: number,
    useBinaryDefault: boolean,
): Promise<Message> {
    const header: Record<string, any> = requestMessage.header;

    try {
        if (!header.hasOwnProperty('tim_')) {
            header['tim_'] = timeoutMsDefault;
        }

        if (useBinaryDefault) {
            header['_binary'] = true;
        }

        const timeoutMs = header['tim_'] as number;

        const responseMessage = await timeout(timeoutMs / 1000, adapter(requestMessage, serializer));

        if (responseMessage.body === { ErrorParseFailure_: { reasons: [{ IncompatibleBinaryEncoding: {} }] } }) {
            header['_binary'] = true;
            header['_forceSendJson'] = true;

            return await timeout(timeoutMs / 1000, adapter(requestMessage, serializer));
        }

        return responseMessage;
    } catch (e) {
        throw new UApiError();
    }
}
