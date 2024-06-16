import { Serializer } from 'uapi/Serializer';
import { UApiSchema } from 'uapi/UApiSchema';
import { Message } from 'uapi/Message';
import { handleMessage } from 'uapi/internal/HandleMessage';
import { parseRequestMessage } from 'uapi/internal/ParseRequestMessage';

export type ErrorHandler = (error: any) => void;
export type RequestHandler = (message: Message) => void;
export type ResponseHandler = (message: Message) => void;
export type MessageHandler = (message: Message) => Promise<Message>;

export async function processBytes(
    requestMessageBytes: Uint8Array,
    serializer: Serializer,
    uapiSchema: UApiSchema,
    onError: ErrorHandler,
    onRequest: RequestHandler,
    onResponse: ResponseHandler,
    handler: MessageHandler,
): Promise<Uint8Array> {
    try {
        const requestMessage = parseRequestMessage(requestMessageBytes, serializer, uapiSchema, onError);

        try {
            onRequest(requestMessage);
        } catch (error) {
            // Handle error
        }

        const responseMessage = await handleMessage(requestMessage, uapiSchema, handler, onError);

        try {
            onResponse(responseMessage);
        } catch (error) {
            // Handle error
        }

        return serializer.serialize(responseMessage);
    } catch (error) {
        try {
            onError(error);
        } catch (error) {
            // Handle error
        }

        return serializer.serialize(new Message({}, { ErrorUnknown_: {} }));
    }
}
