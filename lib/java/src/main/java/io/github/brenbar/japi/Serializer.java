package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * The serializer used to serialize and deserialize jAPI Messages.
 */
public class Serializer {

    SerializationStrategy serializationStrategy;
    private BinaryEncodingStrategy binaryEncoderStrategy;

    Serializer(SerializationStrategy serializationStrategy, BinaryEncodingStrategy binaryEncoderStrategy) {
        this.serializationStrategy = serializationStrategy;
        this.binaryEncoderStrategy = binaryEncoderStrategy;
    }

    /**
     * Serialize the given jAPI message.
     * 
     * @param message
     * @return
     */
    public byte[] serialize(List<Object> message) {
        var headers = (Map<String, Object>) message.get(1);
        var serializeAsBinary = Objects.equals(true, headers.remove("_serializeAsBinary"));
        var forceSendJson = Objects.equals(true, headers.remove("_serializeAsJson"));
        if (serializeAsBinary && !forceSendJson) {
            try {
                var encodedMessage = binaryEncoderStrategy.encode(message);
                return serializationStrategy.toMsgPack(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                // We can still submit as json
                return serializationStrategy.toJson(message);
            }
        } else {
            return serializationStrategy.toJson(message);
        }
    }

    /**
     * Deserialize the given jAPI message bytes.
     * 
     * @param messageBytes
     * @return
     */
    public List<Object> deserialize(byte[] messageBytes) {
        if (messageBytes[0] == '[') {
            return serializationStrategy.fromJson(messageBytes);
        } else {
            var encodedMessage = serializationStrategy.fromMsgPack(messageBytes);
            try {
                return binaryEncoderStrategy.decode(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                throw new DeserializationError(e);
            }
        }
    }
}
