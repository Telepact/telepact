import { SerializationError } from 'uapi/SerializationError';
import { Serialization } from 'uapi/Serialization';
import { Message } from 'uapi/Message';
import { BinaryEncoder } from 'uapi/internal/binary/BinaryEncoder';

export function serializeInternal(
    message: Message,
    binaryEncoder: BinaryEncoder,
    serializer: Serialization,
): Uint8Array {
    const headers: Record<string, any> = message.header;

    let serializeAsBinary: boolean;
    if ('_binary' in headers) {
        serializeAsBinary = headers['_binary'] === true;
        delete headers['_binary'];
    } else {
        serializeAsBinary = false;
    }

    const messageAsPseudoJson: any[] = [message.header, message.body];

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
