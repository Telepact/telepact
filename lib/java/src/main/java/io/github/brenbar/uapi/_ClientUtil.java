package io.github.brenbar.uapi;

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
            if (!requestMessage.header.containsKey("_tim")) {
                requestMessage.header.put("_tim", defaultTimeoutMs);
            }

            if (defaultBinary) {
                requestMessage.header.put("_binary", true);
            }

            var timeoutMs = ((Number) requestMessage.header.get("_tim")).longValue();

            var responseMessage = adapter.apply(requestMessage, serializer).get(timeoutMs,
                    TimeUnit.MILLISECONDS);

            if (Objects.equals(responseMessage.body,
                    Map.of("_ErrorParseFailure",
                            Map.of("reasons", List.of(Map.of("IncompatibleBinaryEncoding", Map.of())))))) {
                // Try again, but as json
                requestMessage.header.put("_forceSendJson", true);
                responseMessage = adapter.apply(requestMessage, serializer).get(timeoutMs,
                        TimeUnit.MILLISECONDS);
            }

            return responseMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
