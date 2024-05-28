package uapi;

import static uapi.internal.DeserializeInternal.deserializeInternal;
import static uapi.internal.SerializeInternal.serializeInternal;

import uapi.internal.binary.BinaryEncoder;

/**
 * A serializer that converts a Message to and from a serialized form.
 */
public class Serializer {

    private Serialization serializationImpl;
    private BinaryEncoder binaryEncoder;

    Serializer(Serialization serializationImpl, BinaryEncoder binaryEncoder) {
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