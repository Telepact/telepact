package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.Objects;

public class Serializer {

    SerializationStrategy serializationStrategy;
    private BinaryEncodingStrategy binaryEncoderStrategy;

    public Serializer(SerializationStrategy serializationStrategy, BinaryEncodingStrategy binaryEncoderStrategy) {
        this.serializationStrategy = serializationStrategy;
        this.binaryEncoderStrategy = binaryEncoderStrategy;
    }

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

    public List<Object> deserialize(byte[] message) throws DeserializationError {
        if (message[0] == '[') {
            return serializationStrategy.fromJson(message);
        } else {
            var encodedMessage = serializationStrategy.fromMsgPack(message);
            try {
                return binaryEncoderStrategy.decode(encodedMessage);
            } catch (BinaryEncoderUnavailableError e) {
                throw new DeserializationError(e);
            }
        }
    }
}
