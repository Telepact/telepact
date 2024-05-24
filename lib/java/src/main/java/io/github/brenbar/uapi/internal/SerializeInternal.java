package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Objects;

import io.github.brenbar.uapi.Message;
import io.github.brenbar.uapi.SerializationError;
import io.github.brenbar.uapi.SerializationImpl;

public class SerializeInternal {
    public static byte[] serializeInternal(Message message, _BinaryEncoder binaryEncoder,
            SerializationImpl serializer) {
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
                } catch (_BinaryEncoderUnavailableError e) {
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
