package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;

class _ClientUtil {

    static Message processRequestObject(Message requestMessage,
            BiFunction<Message, Serializer, Future<Message>> adapter, Serializer serializer, long timeoutMsDefault,
            boolean useBinaryDefault) {
        try {
            if (!requestMessage.header.containsKey("_tim")) {
                requestMessage.header.put("_tim", timeoutMsDefault);
            }

            if (useBinaryDefault) {
                requestMessage.header.put("_binary", true);
            }

            final var timeoutMs = ((Number) requestMessage.header.get("_tim")).longValue();

            final var responseMessage = adapter.apply(requestMessage, serializer).get(timeoutMs, TimeUnit.MILLISECONDS);

            if (Objects.equals(responseMessage.body,
                    Map.of("_ErrorParseFailure",
                            Map.of("reasons", List.of(Map.of("IncompatibleBinaryEncoding", Map.of())))))) {
                // Try again, but as json
                requestMessage.header.put("_forceSendJson", true);

                return adapter.apply(requestMessage, serializer).get(timeoutMs,
                        TimeUnit.MILLISECONDS);
            }

            return responseMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
