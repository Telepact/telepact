import { SerializationError } from '../SerializationError';
import { Serialization } from '../Serialization';
import { Message } from '../Message';
import { BinaryEncoder } from '../internal/binary/BinaryEncoder';

export function serializeInternal(
    message: Message,
    binaryEncoder: BinaryEncoder,
    serializer: Serialization,
): Uint8Array {
    const headers: Record<string, any> = message.headers;

    let serializeAsBinary: boolean;
    if ('_binary' in headers) {
        serializeAsBinary = headers['_binary'] === true;
        delete headers['_binary'];
    } else {
        serializeAsBinary = false;
    }

    const messageAsPseudoJson: any[] = [message.headers, message.body];

    try {
        if (serializeAsBinary) {
            try {
                const encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                return serializer.toMsgpack(encodedMessage);
            } catch (error) {
                // We can still submit as JSON
                return serializer.toJson(messageAsPseudoJson);
            }
        } else {
            return serializer.toJson(messageAsPseudoJson);
        }
    } catch (error) {
        throw new SerializationError(error as Error);
    }
}
