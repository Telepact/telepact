package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import io.github.brenbar.uapi.Message;
import io.github.brenbar.uapi.Serializer;
import io.github.brenbar.uapi.UApiSchema;

public class ParseRequestMessage {
    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, UApiSchema uApiSchema,
            Consumer<Throwable> onError) {

        try {
            return serializer.deserialize(requestMessageBytes);
        } catch (Exception e) {
            onError.accept(e);

            String reason;
            if (e instanceof _BinaryEncoderUnavailableError) {
                reason = "IncompatibleBinaryEncoding";
            } else if (e instanceof _BinaryEncodingMissing) {
                reason = "BinaryDecodeFailure";
            } else if (e instanceof _InvalidMessage) {
                reason = "ExpectedJsonArrayOfTwoObjects";
            } else if (e instanceof _InvalidMessageBody) {
                reason = "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject";
            } else {
                reason = "ExpectedJsonArrayOfTwoObjects";
            }

            return new Message(Map.of("_parseFailures", List.of(Map.of(reason, Map.of()))),
                    Map.of("_unknown", Map.of()));
        }
    }
}
