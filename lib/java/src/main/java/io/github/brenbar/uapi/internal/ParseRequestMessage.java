package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import io.github.brenbar.uapi.Message;
import io.github.brenbar.uapi.Serializer;
import io.github.brenbar.uapi.UApiSchema;
import io.github.brenbar.uapi.internal.binary.BinaryEncoderUnavailableError;
import io.github.brenbar.uapi.internal.binary.BinaryEncodingMissing;

public class ParseRequestMessage {
    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, UApiSchema uApiSchema,
            Consumer<Throwable> onError) {

        try {
            return serializer.deserialize(requestMessageBytes);
        } catch (Exception e) {
            onError.accept(e);

            String reason;
            if (e instanceof BinaryEncoderUnavailableError) {
                reason = "IncompatibleBinaryEncoding";
            } else if (e instanceof BinaryEncodingMissing) {
                reason = "BinaryDecodeFailure";
            } else if (e instanceof InvalidMessage) {
                reason = "ExpectedJsonArrayOfTwoObjects";
            } else if (e instanceof InvalidMessageBody) {
                reason = "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject";
            } else {
                reason = "ExpectedJsonArrayOfTwoObjects";
            }

            return new Message(Map.of("_parseFailures", List.of(Map.of(reason, Map.of()))),
                    Map.of("_unknown", Map.of()));
        }
    }
}
