import { Message } from './Message';
import { Serialization } from './Serialization';
import { BinaryEncoder } from './internal/binary/BinaryEncoder';
import { serializeInternal } from './internal/SerializeInternal';
import { deserializeInternal } from './internal/DeserializeInternal';

export class Serializer {
    /**
     * A serializer that converts a Message to and from a serialized form.
     */

    private serializationImpl: Serialization;
    private binaryEncoder: BinaryEncoder;

    constructor(serializationImpl: Serialization, binaryEncoder: BinaryEncoder) {
        this.serializationImpl = serializationImpl;
        this.binaryEncoder = binaryEncoder;
    }

    public serialize(message: Message): Uint8Array {
        /**
         * Serialize a Message into a byte array.
         */
        return serializeInternal(message, this.binaryEncoder, this.serializationImpl);
    }

    public deserialize(messageBytes: Uint8Array): Message {
        /**
         * Deserialize a Message from a byte array.
         */
        return deserializeInternal(messageBytes, this.serializationImpl, this.binaryEncoder);
    }
}
