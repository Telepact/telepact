package io.github.msgpact.internal;

import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import io.github.msgpact.Message;
import io.github.msgpact.MsgPactSchema;
import io.github.msgpact.Serializer;
import io.github.msgpact.internal.binary.BinaryEncoderUnavailableError;
import io.github.msgpact.internal.binary.BinaryEncodingMissing;
import io.github.msgpact.internal.validation.InvalidMessage;
import io.github.msgpact.internal.validation.InvalidMessageBody;

public class ParseRequestMessage {
    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, MsgPactSchema msgPactSchema,
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
