package io.github.msgpact.internal;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;

import io.github.msgpact.Message;
import io.github.msgpact.MsgPactError;
import io.github.msgpact.Serializer;

public class ProcessRequestObject {
    public static Message processRequestObject(Message requestMessage,
            BiFunction<Message, Serializer, Future<Message>> adapter, Serializer serializer, long timeoutMsDefault,
            boolean useBinaryDefault, boolean alwaysSendJson) {
        final Map<String, Object> header = requestMessage.headers;

        try {
            if (!header.containsKey("time_")) {
                header.put("time_", timeoutMsDefault);
            }

            if (useBinaryDefault) {
                header.put("_binary", true);
            }

            if (Objects.equals(header.get("_binary"), true) && alwaysSendJson) {
                header.put("_forceSendJson", true);
            }

            final var timeoutMs = ((Number) header.get("time_")).longValue();

            final var responseMessage = adapter.apply(requestMessage, serializer).get(timeoutMs, TimeUnit.MILLISECONDS);

            if (Objects.equals(responseMessage.body,
                    Map.of("ErrorParseFailure_",
                            Map.of("reasons", List.of(Map.of("IncompatibleBinaryEncoding", Map.of())))))) {
                // Try again, but as json
                header.put("_binary", true);
                header.put("_forceSendJson", true);

                return adapter.apply(requestMessage, serializer).get(timeoutMs,
                        TimeUnit.MILLISECONDS);
            }

            return responseMessage;
        } catch (Exception e) {
            throw new MsgPactError(e);
        }
    }
}
