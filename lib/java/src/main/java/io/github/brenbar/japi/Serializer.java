package io.github.brenbar.japi;

import java.util.List;

/**
 * The serializer used to serialize and deserialize jAPI Messages.
 */
public class Serializer {

    SerializationStrategy serializationStrategy;
    private BinaryEncodingStrategy binaryEncodingStrategy;

    Serializer(SerializationStrategy serializationStrategy, BinaryEncodingStrategy binaryEncodingStrategy) {
        this.serializationStrategy = serializationStrategy;
        this.binaryEncodingStrategy = binaryEncodingStrategy;
    }

    /**
     * Serialize the given jAPI message.
     * 
     * @param message
     * @return
     */
    public byte[] serialize(List<Object> message) {
        return InternalSerializer.serialize(message, this.binaryEncodingStrategy, this.serializationStrategy);
    }

    /**
     * Deserialize the given jAPI message bytes.
     * 
     * @param messageBytes
     * @return
     */
    public List<Object> deserialize(byte[] messageBytes) {
        return InternalSerializer.deserialize(messageBytes, this.serializationStrategy, this.binaryEncodingStrategy);
    }
}
