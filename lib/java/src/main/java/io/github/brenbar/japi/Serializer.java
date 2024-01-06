package io.github.brenbar.japi;

/**
 * A serializer that converts a Message to and from a serialized form.
 */
public class Serializer {

    private SerializationImpl serializationImpl;
    private BinaryEncoder binaryEncoder;

    Serializer(SerializationImpl serializationImpl, BinaryEncoder binaryEncoder) {
        this.serializationImpl = serializationImpl;
        this.binaryEncoder = binaryEncoder;
    }

    public byte[] serialize(Message message) {
        return _SerializeUtil.serialize(message, this.binaryEncoder, this.serializationImpl);
    }

    public Message deserialize(byte[] messageBytes) {
        return _SerializeUtil.deserialize(messageBytes, this.serializationImpl, this.binaryEncoder);
    }
}