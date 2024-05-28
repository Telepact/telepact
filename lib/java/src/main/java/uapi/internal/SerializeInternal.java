package uapi.internal;

import java.util.List;
import java.util.Objects;

import uapi.Message;
import uapi.SerializationError;
import uapi.Serialization;
import uapi.internal.binary.BinaryEncoder;
import uapi.internal.binary.BinaryEncoderUnavailableError;

public class SerializeInternal {
    public static byte[] serializeInternal(Message message, BinaryEncoder binaryEncoder,
            Serialization serializer) {
        final var headers = message.header;

        final boolean serializeAsBinary;
        if (headers.containsKey("_binary")) {
            serializeAsBinary = Objects.equals(true, headers.remove("_binary"));
        } else {
            serializeAsBinary = false;
        }

        final List<Object> messageAsPseudoJson = List.of(message.header, message.body);

        try {
            if (serializeAsBinary) {
                try {
                    final var encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                    return serializer.toMsgPack(encodedMessage);
                } catch (BinaryEncoderUnavailableError e) {
                    // We can still submit as json
                    return serializer.toJson(messageAsPseudoJson);
                }
            } else {
                return serializer.toJson(messageAsPseudoJson);
            }
        } catch (Throwable e) {
            throw new SerializationError(e);
        }
    }
}
