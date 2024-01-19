package io.github.brenbar.uapi;

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
        return _SerializeUtil.serialize(message, this.binaryEncoder, this.serializationImpl);
    }

    /**
     * Deserialize a Message from a byte array.
     * 
     * @param messageBytes
     * @return
     */
    public Message deserialize(byte[] messageBytes) {
        return _SerializeUtil.deserialize(messageBytes, this.serializationImpl, this.binaryEncoder);
    }
}