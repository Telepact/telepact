package io.github.brenbar.japi;

import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;

class _ClientUtil {

    static Message constructRequestMessage(Request request, boolean useBinaryDefault,
            boolean forceSendJsonDefault,
            long timeoutMsDefault) {
        boolean finalUseBinary;
        if (request.useBinary.isPresent()) {
            finalUseBinary = request.useBinary.get();
        } else {
            finalUseBinary = useBinaryDefault;
        }

        boolean finalForceSendJson;
        if (request.forceSendJson.isPresent()) {
            finalForceSendJson = request.forceSendJson.get();
        } else {
            finalForceSendJson = forceSendJsonDefault;
        }

        long finalTimeoutMs;
        if (request.timeoutMs.isPresent()) {
            finalTimeoutMs = request.timeoutMs.get();
        } else {
            finalTimeoutMs = timeoutMsDefault;
        }

        var headers = request.headers;

        if (!request.selectedStructFields.isEmpty()) {
            headers.put("_sel", request.selectedStructFields);
        }

        if (finalForceSendJson) {
            headers.put("_serializeAsJson", finalForceSendJson);
        }

        headers.put("_tim", finalTimeoutMs);

        if (finalUseBinary) {
            headers.put("_serializeAsBinary", true);
        }

        return new Message(headers, request.functionName, request.functionArgument);
    }

    static Message processRequestObject(Message requestMessage,
            BiFunction<Message, Serializer, Future<Message>> adapter, Serializer serializer, long timeoutMs) {
        try {
            var responseMessage = adapter.apply(requestMessage, serializer).get(timeoutMs, TimeUnit.MILLISECONDS);
            return responseMessage;
        } catch (Exception e) {
            throw new ClientProcessError(e);
        }
    }
}
