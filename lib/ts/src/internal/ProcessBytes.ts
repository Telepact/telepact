import { Serializer } from '../Serializer';
import { TelepactSchema } from '../TelepactSchema';
import { Message } from '../Message';
import { handleMessage } from '../internal/HandleMessage';
import { parseRequestMessage } from '../internal/ParseRequestMessage';

export type ErrorHandler = (error: any) => void;
export type RequestHandler = (message: Message) => void;
export type ResponseHandler = (message: Message) => void;
export type MessageHandler = (message: Message) => Promise<Message>;

export async function processBytes(
    requestMessageBytes: Uint8Array,
    serializer: Serializer,
    telepactSchema: TelepactSchema,
    onError: ErrorHandler,
    onRequest: RequestHandler,
    onResponse: ResponseHandler,
    handler: MessageHandler,
): Promise<Uint8Array> {
    try {
        const requestMessage = parseRequestMessage(requestMessageBytes, serializer, telepactSchema, onError);

        try {
            onRequest(requestMessage);
        } catch (error) {
            // Handle error
        }

        const responseMessage = await handleMessage(requestMessage, telepactSchema, handler, onError);

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
