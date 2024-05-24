package io.github.brenbar.uapi;

import io.github.brenbar.uapi.internal._BinaryEncoder;

import static io.github.brenbar.uapi.internal.SerializeInternal.serializeInternal;
import static io.github.brenbar.uapi.internal.DeserializeInternal.deserializeInternal;

/**
 * A serializer that converts a Message to and from a serialized form.
 */
public class Serializer {

    private SerializationImpl serializationImpl;
    private _BinaryEncoder binaryEncoder;

    Serializer(SerializationImpl serializationImpl, _BinaryEncoder binaryEncoder) {
        this.serializationImpl = serializationImpl;
        this.binaryEncoder = binaryEncoder;
    }

    /**
     * Serialize a Message into a byte array.
     * 
     * @param message
     * @return
     */
    public byte[] serialize(Message message) {
        return serializeInternal(message, this.binaryEncoder, this.serializationImpl);
    }

    /**
     * Deserialize a Message from a byte array.
     * 
     * @param messageBytes
     * @return
     */
    public Message deserialize(byte[] messageBytes) {
        return deserializeInternal(messageBytes, this.serializationImpl, this.binaryEncoder);
    }
}