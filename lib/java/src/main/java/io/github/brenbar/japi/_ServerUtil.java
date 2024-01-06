package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;

class _ServerUtil {
    static byte[] processBytes(byte[] requestMessageBytes, Serializer serializer, JApiSchema jApiSchema,
            Consumer<Throwable> onError, Consumer<Message> onRequest, Consumer<Message> onResponse,
            Function<Message, Message> handler) {
        try {
            var requestMessage = parseRequestMessage(requestMessageBytes, serializer,
                    jApiSchema, onError);

            try {
                onRequest.accept(requestMessage);
            } catch (Throwable ignored) {
            }

            var responseMessage = _ServerHandlerUtil.handleMessage(requestMessage, jApiSchema, handler, onError);

            try {
                onResponse.accept(responseMessage);
            } catch (Throwable ignored) {
            }

            return serializer.serialize(responseMessage);
        } catch (Throwable e) {
            try {
                onError.accept(e);
            } catch (Throwable ignored) {
            }

            return serializer
                    .serialize(new Message(new HashMap<>(), Map.of("_ErrorUnknown", Map.of())));
        }
    }

    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, JApiSchema jApiSchema,
            Consumer<Throwable> onError) {

        Message requestMessage;
        try {
            requestMessage = serializer.deserialize(requestMessageBytes);
        } catch (DeserializationError e) {
            try {
                onError.accept(e);
            } catch (Throwable ignored) {
            }
            var cause = e.getCause();

            List<Map<String, Object>> parseFailures;
            if (cause instanceof BinaryEncoderUnavailableError e2) {
                parseFailures = List.of(Map.of("IncompatibleBinaryEncoding", Map.of()));
            } else if (cause instanceof BinaryEncodingMissing e2) {
                parseFailures = List.of(Map.of("BinaryDecodeFailure", Map.of()));
            } else if (cause instanceof InvalidJsonError e2) {
                parseFailures = List.of(Map.of("InvalidJson", Map.of()));
            } else if (cause instanceof MessageParseError e2) {
                parseFailures = e2.failures.stream().map(f -> (Map<String, Object>) (Object) Map.of(f, Map.of()))
                        .toList();
            } else {
                // TODO: Change this to something like "CouldNotParse"
                parseFailures = List.of(Map.of("MessageMustBeArrayWithTwoElements", Map.of()));
            }

            var requestHeaders = new HashMap<String, Object>();
            requestHeaders.put("_parseFailures", parseFailures);

            return new Message(requestHeaders, Map.of());
        }

        return requestMessage;
    }
}
