import { SerializationImpl } from './SerializationImpl';
import { Message } from './Message';
import { serialize as _serialize, deserialize as _deserialize } from './_util';
import { _BinaryEncoder } from './_utilTypes';

/**
 * A serializer that converts a Message to and from a serialized form.
 */
class Serializer {
    private serializationImpl: SerializationImpl;
    private binaryEncoder: _BinaryEncoder;

    constructor(serializationImpl: SerializationImpl, binaryEncoder: _BinaryEncoder) {
        this.serializationImpl = serializationImpl;
        this.binaryEncoder = binaryEncoder;
    }

    /**
     * Serialize a Message into a byte array.
     * 
     * @param message
     * @return
     */
    public serialize(message: Message): Uint8Array {
        return _serialize(message, this.binaryEncoder, this.serializationImpl);
    }

    /**
     * Deserialize a Message from a byte array.
     * 
     * @param messageBytes
     * @return
     */
    public deserialize(messageBytes: Uint8Array): Message {
        return _deserialize(messageBytes, this.serializationImpl, this.binaryEncoder);
    }
}

export { Serializer };
