package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;

class _ClientUtil {

    static Message constructRequestMessage(Request request, boolean useBinaryDefault,
            boolean forceSendJsonDefault,
            long timeoutMsDefault) {
        boolean finalUseBinary;
        Optional<Boolean> useBinaryOptional = request.useBinary;
        if (useBinaryOptional.isPresent()) {
            finalUseBinary = request.useBinary.get();
        } else {
            finalUseBinary = useBinaryDefault;
        }

        boolean finalJsonRequest;
        Optional<Boolean> forceSendJsonOptional = request.forceSendJson;
        if (forceSendJsonOptional.isPresent()) {
            finalJsonRequest = request.forceSendJson.get();
        } else {
            finalJsonRequest = forceSendJsonDefault;
        }

        long finalTimeoutMs;
        Optional<Long> timeoutMsOptional = request.timeoutMs;
        if (timeoutMsOptional.isPresent()) {
            finalTimeoutMs = request.timeoutMs.get();
        } else {
            finalTimeoutMs = timeoutMsDefault;
        }

        Map<String, Object> headers = request.headers;
        Map<String, List<String>> selectedStructFields = request.selectedStructFields;

        if (!selectedStructFields.isEmpty()) {
            headers.put("_sel", selectedStructFields);
        }

        headers.put("_tim", finalTimeoutMs);

        if (finalUseBinary) {
            headers.put("_binary", true);
        }

        return new Message(headers, request.functionName, request.functionArgument);
    }

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

            if (!requestMessage.header.containsKey("_binary")) {
                requestMessage.header.put("_binary", defaultBinary);
            }

            var responseMessage = adapter.apply(requestMessage, serializer).get(finalTimeoutMs,
                    TimeUnit.MILLISECONDS);
            return responseMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
