package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;

class _ClientUtil {

    static Message processRequestObject(Message requestMessage,
            BiFunction<Message, Serializer, Future<Message>> adapter, Serializer serializer, long defaultTimeoutMs,
            boolean defaultBinary) {
        try {
            Long finalTimeoutMs;
            if (requestMessage.header.containsKey("_tim")) {
                finalTimeoutMs = (Long) requestMessage.header.get("_tim");
            } else {
                var timeoutMs = requestMessage.header.remove("_timeoutMs");
                if (timeoutMs != null) {
                    finalTimeoutMs = (Long) timeoutMs;
                } else {
                    finalTimeoutMs = defaultTimeoutMs;
                }
                requestMessage.header.put("_tim", finalTimeoutMs);
            }

            if (!requestMessage.header.containsKey("_sel")) {
                var selectFields = requestMessage.header.remove("_select");
                if (selectFields != null) {
                    requestMessage.header.put("_sel", selectFields);
                }
            }

            if (requestMessage.header.containsKey("_bin")) {
                throw new RuntimeException(
                        "The client manages the _bin header. Use _binary = true to enable binary encoding.");
            }

            if (!requestMessage.header.containsKey("_binary")) {
                requestMessage.header.put("_binary", defaultBinary);
            }

            var responseMessage = adapter.apply(requestMessage, serializer).get(finalTimeoutMs,
                    TimeUnit.MILLISECONDS);

            if (Objects.equals(responseMessage.body,
                    Map.of("_ErrorParseFailure",
                            Map.of("reasons", List.of(Map.of("IncompatibleBinaryEncoding", Map.of())))))) {
                // Try again, but as json
                requestMessage.header.put("_forceSendJson", true);
                responseMessage = adapter.apply(requestMessage, serializer).get(finalTimeoutMs,
                        TimeUnit.MILLISECONDS);
            }

            return responseMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
